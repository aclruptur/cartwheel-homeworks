"""CLI chat shell for the Cartwheel support agent. Instructor-provided.

Module 1 has no graphical UI on purpose; the first UI of the course is the
error-analysis UI Module 2 builds. Chat here.

Usage:
    uv run python -m agent.cli --role shopper
    uv run python -m agent.cli --role merchant --model claude-opus-4-6
    uv run python -m agent.cli --role support --user 9502 --trace
    uv run python -m agent.cli --role support --defenses   # Module 4 guards + refund pause

The role picks a default demo user (shopper 1, merchant 9001, support 9501);
--user overrides it. The auth context comes from the users table, exactly as
the server would inject it. It is never taken from the chat itself.

``--defenses`` turns on the Module 4 controls (Homework 8): the input and
output guardrails and the ``needs_approval`` refund pause. It is off by
default, so the plain chat is the Module 1 agent. With it on, an
above-threshold refund pauses before the tool runs. The pause seam in ``chat``
shows the pending tool call and asks whether the tool may run.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import time

from agents import Runner, SQLiteSession
from opentelemetry import trace

from agent import db
from agent.agent import (
    build_agent,
    prompt_version,
    render_system_prompt,
    reset_debug_tool_calls,
    set_debug_tool_calls,
)
from agent.auth import AuthContext
from agent.config import REPO_ROOT
from observability.instrument import load_env, setup_raindrop, setup_tracing

DEFAULT_USERS = {"shopper": 1, "merchant": 9001, "support": 9501}
MAX_TURNS = 12  # cap runaway loops; keeps conversations bounded
SESSIONS_DB = REPO_ROOT / ".sessions.db"
_tracer = trace.get_tracer("cartwheel.cli")


def resolve_auth(role: str, user_id: int | None) -> AuthContext:
    """Build the auth context from the users table (the injected block)."""
    conn = db.connect()
    try:
        user = db.get_user(conn, user_id if user_id is not None else DEFAULT_USERS[role])
    finally:
        conn.close()
    if user is None:
        raise SystemExit(f"no such user id: {user_id}")
    if user.role != role:
        raise SystemExit(
            f"user {user.id} has role '{user.role}', not '{role}'; pick a matching --user"
        )
    return AuthContext(user_id=user.id, role=user.role, store_id=user.store_id)


async def chat(
    ctx: AuthContext,
    model: str | None,
    defenses: bool = False,
    debug: bool = False,
    raindrop_client=None,
) -> None:
    agent = build_agent(ctx, model=model, defenses=defenses)
    model_name = getattr(agent.model, "model", agent.model)
    if model_name is not None:
        model_name = str(model_name)
    session_id = f"cli-{ctx.role}-{ctx.user_id}-{int(time.time())}"
    session = SQLiteSession(session_id, str(SESSIONS_DB))
    version = prompt_version(render_system_prompt(ctx))
    print(
        f"Cartwheel support CLI | role={ctx.role} user={ctx.user_id} "
        f"store={ctx.store_id} prompt_version={version} defenses={'on' if defenses else 'off'}"
    )
    print("Type a message, or 'quit' to exit.\n")
    turn_index = 0
    while True:
        try:
            line = input(f"{ctx.role}> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not line:
            continue
        if line.lower() in {"quit", "exit"}:
            return
        turn_index += 1
        rd_interaction = None
        if raindrop_client is not None:
            rd_interaction = raindrop_client.begin(
                user_id=str(ctx.user_id),
                event="cartwheel.cli.turn",
                event_id=f"{session_id}-{turn_index}",
                convo_id=session_id,
                input=line,
                model=model_name,
                properties={
                    "cartwheel.surface": "cli",
                    "cartwheel.user_role": ctx.role,
                    "cartwheel.user_id": str(ctx.user_id),
                    "cartwheel.store_id": ctx.store_id,
                    "cartwheel.prompt_version": version,
                    "cartwheel.session_id": session_id,
                    "cartwheel.turn_index": turn_index,
                    "cartwheel.defenses": defenses,
                },
            )
        try:
            with _tracer.start_as_current_span("cartwheel.session_message") as span:
                if span.is_recording():
                    span.set_attribute("cartwheel.user_role", ctx.role)
                    span.set_attribute("cartwheel.user_id", str(ctx.user_id))
                    span.set_attribute("cartwheel.prompt_version", version)
                tool_calls: list[dict] = []
                debug_token = set_debug_tool_calls(tool_calls) if debug else None
                try:
                    result = await Runner.run(
                        agent, line, session=session, context=ctx, max_turns=MAX_TURNS
                    )
                finally:
                    if debug_token is not None:
                        reset_debug_tool_calls(debug_token)
        except Exception as exc:
            if rd_interaction is not None:
                rd_interaction.finish(output=f"Error: {type(exc).__name__}: {exc}")
                raindrop_client.flush()
            raise

        # ------------------------------------------------------------------
        # Module 4 pause and resume code (Homework 8, Part D). With defenses on,
        # an above-threshold refund makes refund_needs_human return True, so
        # the SDK pauses the run instead of executing the tool and lists the
        # pending call(s) in result.interruptions (each a ToolApprovalItem).
        # A queued run is not finished: result.final_output is not the answer
        # until the interruptions are resolved and the run resumes.
        #
        # Your job (the seam below): while result has interruptions, show each
        # pending tool name and its arguments, ask whether the tool may run,
        # save the answer in a resumable state, and resume the run. The SDK
        # contract (verified, openai-agents 0.17.7):
        #
        #   state = result.to_state()
        #   for item in result.interruptions:        # ToolApprovalItem
        #       # item.tool_name names the tool. item.raw_item carries the
        #       # pending call, including its JSON arguments.
        #       state.approve(item)                  # or state.reject(item)
        #   result = await Runner.run(agent, state, context=ctx,
        #                             max_turns=MAX_TURNS)
        #
        # Loop until result.interruptions is empty (a resumed run can pause
        # again). Then fall through to printing final_output. Approving here
        # only allows the tool to run. The tool may then create a refund with
        # status queued_for_approval. A support user makes the later refund
        # decision through agent/review.py.
        # ------------------------------------------------------------------
        if getattr(result, "interruptions", None):
            ### YOUR CODE HERE (m4)
            raise NotImplementedError(
                "m4: show each pending tool call, allow or reject it via "
                "result.to_state(), and resume with Runner.run(agent, state, ...). "
                "See the seam comment above."
            )

        print(f"\nagent> {result.final_output}")
        if rd_interaction is not None:
            rd_interaction.set_properties(
                {
                    "cartwheel.tool_call_count": len(tool_calls),
                    "cartwheel.tool_call_names": [call["name"] for call in tool_calls],
                    "cartwheel.tool_call_ok": [
                        call.get("result", {}).get("ok") for call in tool_calls
                    ],
                }
            )
            rd_interaction.finish(output=str(result.final_output))
            raindrop_client.flush()
        if debug:
            print("tool_calls> " + json.dumps(tool_calls, sort_keys=True))
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with the Cartwheel support agent.")
    parser.add_argument("--role", choices=["shopper", "merchant", "support"], default="shopper")
    parser.add_argument("--user", type=int, default=None, help="user id (defaults per role)")
    parser.add_argument(
        "--model",
        default=None,
        help="gpt-5.5 | claude-opus-4-6 | glm-5.2 (default: $CARTWHEEL_MODEL or gpt-5.5)",
    )
    parser.add_argument(
        "--trace", action="store_true", help="ship spans to Langfuse (Lecture 2)"
    )
    parser.add_argument(
        "--defenses",
        action="store_true",
        help="turn on the Module 4 guards and the refund approval pause (Homework 8)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="print each tool call's name, arguments, and result after each turn",
    )
    parser.add_argument(
        "--raindrop",
        action="store_true",
        help="mirror CLI turns to local Raindrop Workshop",
    )
    args = parser.parse_args()

    load_env()
    if args.trace:
        setup_tracing()
    raindrop_client = setup_raindrop() if args.raindrop else None
    ctx = resolve_auth(args.role, args.user)
    asyncio.run(
        chat(
            ctx,
            args.model,
            defenses=args.defenses,
            debug=args.debug,
            raindrop_client=raindrop_client,
        )
    )


if __name__ == "__main__":
    main()
