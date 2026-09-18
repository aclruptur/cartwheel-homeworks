"""The Cartwheel endpoint, with the session routes completed in Homework 2.

A thin FastAPI wrapper with three routes (Lecture 2.3):

  - POST /sessions            binds a user + role, returns a signed dev token
  - POST /sessions/{id}/messages   one conversation turn
  - GET  /health              liveness

Why an endpoint at all: one choke point to authenticate, log, sample,
rate-limit, and replay. Modules 3 and 4 need a surface to monitor and attack.

The token is dev-only auth: a base64 JSON payload signed with an HMAC over a
shared secret (CARTWHEEL_DEV_SECRET). It is not real auth; the *shape* (a
server-issued credential carrying user id + role that tools trust) is what
Module 4 attacks. In production you would stream responses and assemble the
final message in middleware; this server does not stream.

Run with:
    uv run uvicorn server.app:app --port 8010
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
import time
import uuid
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Any, AsyncIterator

from agents import Runner, SQLiteSession
from fastapi import FastAPI, Header, HTTPException
from opentelemetry import trace
from pydantic import BaseModel

from agent import db
from agent.agent import SYSTEM_PROMPT_TEMPLATE, build_agent, prompt_version, render_system_prompt
from agent.auth import ROLES, AuthContext
from agent.config import REPO_ROOT, db_path
from observability.instrument import load_env, setup_tracing

MAX_TURNS = 12  # cap runaway loops; keeps conversations bounded
SESSIONS_DB = REPO_ROOT / ".sessions.db"

_tracer = trace.get_tracer("cartwheel.server")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    load_env()
    setup_tracing()  # no-op with a warning if LANGFUSE_PUBLIC_KEY is unset
    yield


app = FastAPI(title="Cartwheel support agent", lifespan=lifespan)

# session_id -> (AuthContext, SQLiteSession). In-memory on purpose: the trace
# store is the durable record, not this dict.
_SESSIONS: dict[str, tuple[AuthContext, SQLiteSession]] = {}


# ---------------------------------------------------------------------------
# Signed dev token: base64url(JSON payload) + "." + HMAC-SHA256 signature.
# ---------------------------------------------------------------------------


def _secret() -> bytes:
    return os.environ.get("CARTWHEEL_DEV_SECRET", "cartwheel-dev-secret").encode()


def create_token(payload: dict[str, Any]) -> str:
    body = base64.urlsafe_b64encode(
        json.dumps(payload, sort_keys=True).encode()
    ).decode()
    sig = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def verify_token(token: str) -> dict[str, Any] | None:
    """Return the payload if the signature checks out, else None."""
    try:
        body, sig = token.rsplit(".", 1)
    except ValueError:
        return None
    expected = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return None
    try:
        return json.loads(base64.urlsafe_b64decode(body.encode()))
    except (binascii.Error, json.JSONDecodeError):
        return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


class SessionCreate(BaseModel):
    user_id: int
    role: str


class MessageIn(BaseModel):
    message: str
    model: str | None = None
    # Set by the scenario runner (Lecture 3) so a trace links back to its
    # ground truth. Manual sessions leave it null.
    scenario_id: str | None = None
    # Scenario runners can pass the answer key so Langfuse exports carry the
    # review ground truth without requiring a later local scenario-file join.
    expected: dict[str, Any] | None = None


@lru_cache(maxsize=1)
def _scenario_expectations() -> dict[str, dict[str, Any]]:
    """Return scenario id -> expected answer key for local scenario runs.

    The runner sends ``expected`` explicitly for new traces. This lookup is a
    fallback for callers that only pass ``scenario_id`` while still running
    from this checkout.
    """
    paths = [
        REPO_ROOT / "scenarios" / "support_scenarios.jsonl",
        REPO_ROOT / "scenarios" / "pilot_scenarios.jsonl",
        REPO_ROOT / "scenarios" / "pilot_extra_challenges.jsonl",
        REPO_ROOT / "security" / "supplied_attacks.jsonl",
    ]
    out: dict[str, dict[str, Any]] = {}
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            scenario_id = record.get("id") or record.get("scenario_id")
            expected = record.get("expected")
            if isinstance(scenario_id, str) and isinstance(expected, dict):
                out[scenario_id] = expected
    return out


def _expected_for_message(body: MessageIn) -> dict[str, Any] | None:
    if isinstance(body.expected, dict):
        return body.expected
    if body.scenario_id:
        return _scenario_expectations().get(body.scenario_id)
    return None


def _stamp_expected_attributes(span: Any, expected: dict[str, Any] | None) -> None:
    """Attach scenario expected outcome/source to the active trace span."""
    if not expected:
        return
    span.set_attribute("cartwheel.expected.evaluation", str(expected.get("evaluation") or ""))
    if expected.get("outcome") is not None:
        span.set_attribute("cartwheel.expected.outcome", str(expected["outcome"]))
    if expected.get("criterion") is not None:
        span.set_attribute("cartwheel.expected.criterion", str(expected["criterion"]))
    source = expected.get("source")
    if isinstance(source, dict):
        if source.get("type") is not None:
            span.set_attribute("cartwheel.expected.source.type", str(source["type"]))
        if source.get("reference") is not None:
            span.set_attribute(
                "cartwheel.expected.source.reference", str(source["reference"])
            )
    span.set_attribute(
        "cartwheel.expected",
        json.dumps(expected, sort_keys=True, ensure_ascii=False),
    )


@app.post("/sessions")
def create_session(body: SessionCreate) -> dict[str, Any]:
    """Bind a verified database user to a new server-side session.

    Validate the requested role, load the user from the database, and reject
    a request whose claimed role differs from the stored role. Create an
    AuthContext and SQLiteSession, save them in _SESSIONS, then return the
    session id and a signed token. The token payload must contain session_id,
    user_id, role, store_id, and issued_at.
    """
    if body.role not in ROLES:
        raise HTTPException(status_code=400, detail="unknown role")

    conn = db.connect()
    try:
        user = db.get_user(conn, body.user_id)
    finally:
        conn.close()

    if user is None:
        raise HTTPException(status_code=404, detail="unknown user")
    if user.role != body.role:
        raise HTTPException(status_code=403, detail="role does not match user")

    context = AuthContext(
        user_id=user.id,
        role=user.role,
        store_id=user.store_id,
    )
    session_id = str(uuid.uuid4())
    session = SQLiteSession(session_id, str(SESSIONS_DB))
    _SESSIONS[session_id] = (context, session)
    token = create_token(
        {
            "session_id": session_id,
            "user_id": user.id,
            "role": user.role,
            "store_id": user.store_id,
            "issued_at": int(time.time()),
        }
    )
    return {"session_id": session_id, "token": token}


def _authorize(session_id: str, authorization: str | None) -> AuthContext:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    payload = verify_token(authorization.removeprefix("Bearer "))
    if payload is None:
        raise HTTPException(status_code=401, detail="bad token signature")
    if payload.get("session_id") != session_id:
        raise HTTPException(status_code=403, detail="token is for another session")
    if session_id not in _SESSIONS:
        raise HTTPException(status_code=404, detail="unknown session (server restarted?)")
    return _SESSIONS[session_id][0]


@app.post("/sessions/{session_id}/messages")
async def post_message(
    session_id: str,
    body: MessageIn,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    """Run one authenticated conversation turn inside a root trace span.

    Authorize the token, recover the server-side session, and build the agent
    for the authenticated context. Compute the rendered prompt's version.
    The cartwheel.session_message span must record the user role, user id,
    prompt version, and a nonempty scenario id when one is supplied. Run the
    agent inside that span, then return the session id, final reply, and
    prompt version.
    """
    ctx = _authorize(session_id, authorization)
    session = _SESSIONS[session_id][1]
    agent = build_agent(ctx, model=body.model)
    version = prompt_version(SYSTEM_PROMPT_TEMPLATE)
    expected = _expected_for_message(body)

    with _tracer.start_as_current_span("cartwheel.session_message") as span:
        if span.is_recording():
            span.set_attribute("cartwheel.user_role", ctx.role)
            span.set_attribute("cartwheel.user_id", str(ctx.user_id))
            span.set_attribute("cartwheel.prompt_version", version)
            if body.scenario_id:
                span.set_attribute("cartwheel.scenario_id", body.scenario_id)
            _stamp_expected_attributes(span, expected)
            span.set_attribute(
                "gen_ai.input.messages",
                json.dumps(
                    [
                        {
                            "role": "user",
                            "parts": [{"type": "text", "content": body.message}],
                        }
                    ]
                ),
            )
        result = await Runner.run(
            agent,
            body.message,
            session=session,
            context=ctx,
            max_turns=MAX_TURNS,
        )
        if span.is_recording():
            span.set_attribute(
                "gen_ai.output.messages",
                json.dumps(
                    [
                        {
                            "role": "assistant",
                            "parts": [
                                {"type": "text", "content": result.final_output}
                            ],
                        }
                    ]
                ),
            )

    return {
        "session_id": session_id,
        "reply": result.final_output,
        "prompt_version": version,
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "db_exists": db_path().exists(),
        "active_sessions": len(_SESSIONS),
    }
