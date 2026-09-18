"""File-backed review server for the error-analysis skill.

Adapted from the instructor's error-discovery skill. This is the review
interface's backend: a Python standard-library HTTP server (no dependencies)
that serves the single-file HTML app in ``ui/`` and a small JSON API over the
plain files in ``analysis/state/``. The human annotates in the browser, the
app auto-saves every change here, and the coding agent watches
``state/annotations.json`` on a 2-second poll loop (see review-loop.md).

Langfuse is the canonical store for traces and accepted labels. The state
files are an inspectable local mirror and hold workflow state that does not
belong in the trace store. The offline demonstration uses only these files,
and its replay path fabricates a live session without a Langfuse connection.

API (kept compatible with the error-discovery skill so the same UI works):

    GET  /                    the HTML review app
    GET  /api/samples         current sample set (+ manifest of why picked)
    POST /api/samples         push a new or updated sample set
    GET  /api/annotations     current human annotations
    POST /api/annotations     save annotations (the app posts on every change)
    GET  /api/graph           the 2D projection of all traces for the map view
    GET  /api/patterns        the taxonomy as the agent currently holds it
    POST /api/patterns        push the updated taxonomy
    GET  /api/structured_labels  structured pass/fail matrix for final modes
    GET  /api/suggestions     agent depth-scan suggestions awaiting accept/reject
    POST /api/suggestions     push suggestions

Run it:

    python analysis/server.py                       # serve on :8020
    python analysis/server.py --port 8021
    python analysis/server.py --replay state/demo_annotations.json

The ``--replay`` flag replays a canned annotations file on a timer, appending
one annotation every few seconds, so the watcher, the grouping, and the
suggestion pipeline all fire on stage even if live annotation fails. The canned
file (``state/demo_annotations.json``) is produced by the course seed and
committed with the repo.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STATE_DIR = HERE / "state"
UI_DIR = HERE / "ui"
WORLD_DB_PATH = ROOT / "data" / "cartwheel.db"

# API path -> the state file that backs it. GET reads the file, POST overwrites
# it. Keeping this a plain table makes the whole contract inspectable and keeps
# the handler tiny.
API_FILES: dict[str, Path] = {
    "/api/samples": STATE_DIR / "samples.json",
    "/api/annotations": STATE_DIR / "annotations.json",
    "/api/graph": STATE_DIR / "graph.json",
    "/api/patterns": STATE_DIR / "patterns.json",
    "/api/structured_labels": STATE_DIR / "structured_labels_matrix.json",
    "/api/suggestions": STATE_DIR / "suggestions.json",
}

# Default empty document per endpoint, so a fresh checkout serves valid JSON
# before the agent has written anything. samples/annotations/suggestions are
# lists; graph and patterns are objects.
API_DEFAULTS: dict[str, Any] = {
    "/api/samples": [],
    "/api/annotations": [],
    "/api/graph": {"nodes": [], "clusters": []},
    "/api/patterns": {},
    "/api/structured_labels": [],
    "/api/suggestions": [],
}

PILOT_REVIEW_PATH = HERE.parent / "scenarios" / "pilot_review.jsonl"


def _read_json(path: Path, default: Any) -> Any:
    """Return the parsed JSON at ``path``, or ``default`` if missing or bad.

    A half-written file (the app crashed mid-save) reads as the default rather
    than crashing the server; the next good POST repairs it.
    """
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return default


def _read_jsonl(path: Path) -> list[Any]:
    """Return parsed JSONL records from ``path``, skipping blank/bad lines."""
    if not path.exists():
        return []
    records: list[Any] = []
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except OSError:
        return []
    return records


def _write_json(path: Path, data: Any) -> None:
    """Write ``data`` to ``path`` atomically (write temp, then replace)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)


def _dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def _rows(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def _sample_by_trace_id(trace_id: str) -> dict[str, Any] | None:
    samples = _read_json(API_FILES["/api/samples"], API_DEFAULTS["/api/samples"])
    if not isinstance(samples, list):
        return None
    for sample in samples:
        if isinstance(sample, dict) and str(sample.get("trace_id")) == trace_id:
            return sample
    return None


def _message_text(message: dict[str, Any]) -> str:
    value = message.get("text", message.get("content", ""))
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


def _referenced_order_ids(sample: dict[str, Any]) -> list[int]:
    text_parts = []
    for message in sample.get("trace") or []:
        if isinstance(message, dict):
            text_parts.append(_message_text(message))
    text = "\n".join(text_parts)
    ids = []
    for match in re.finditer(r"(?:#|\border(?:\s+id)?\s+)(\d{3,5})\b", text, re.I):
        value = int(match.group(1))
        if 1900 <= value <= 2100:
            continue
        if value not in ids:
            ids.append(value)
    return ids[:20]


def _data_quality_case_id(sample: dict[str, Any]) -> str | None:
    expected = sample.get("expected") if isinstance(sample.get("expected"), dict) else {}
    source = expected.get("source") if isinstance(expected.get("source"), dict) else {}
    reference = str(source.get("reference") or "")
    match = re.search(r"\b(dq-[a-z0-9-]+)\b", reference)
    return match.group(1) if match else None


def _scope_clause(role: str | None, user_id: int | None, store_id: int | None) -> tuple[str, tuple[Any, ...]]:
    if role == "shopper" and user_id is not None:
        return "o.user_id = ?", (user_id,)
    if role == "merchant" and store_id is not None:
        return "o.store_id = ?", (store_id,)
    return "1 = 1", ()


def _order_select(where: str) -> str:
    return f"""
        SELECT
            o.id AS order_id,
            o.user_id,
            o.store_id,
            os.name AS store_name,
            o.product_id,
            p.title AS product_title,
            p.category AS product_category,
            p.store_id AS product_store_id,
            ps.name AS product_store_name,
            o.quantity,
            ROUND(o.total_cents / 100.0, 2) AS total_usd,
            o.status,
            o.ordered_at,
            o.shipped_at,
            o.delivered_at,
            o.refund_eligible
        FROM orders o
        JOIN products p ON p.id = o.product_id
        JOIN stores os ON os.id = o.store_id
        JOIN stores ps ON ps.id = p.store_id
        WHERE {where}
    """


def _order_data_quality_checks(orders: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    seen: set[tuple[Any, Any, Any]] = set()
    for order in orders:
        if (
            order.get("store_id") is not None
            and order.get("product_store_id") is not None
            and order.get("store_id") != order.get("product_store_id")
        ):
            key = (
                order.get("order_id"),
                order.get("store_id"),
                order.get("product_store_id"),
            )
            if key in seen:
                continue
            seen.add(key)
            checks.append(
                {
                    "kind": "order_product_store_mismatch",
                    "severity": "warning",
                    "order_id": order.get("order_id"),
                    "product_id": order.get("product_id"),
                    "order_store_id": order.get("store_id"),
                    "order_store_name": order.get("store_name"),
                    "product_store_id": order.get("product_store_id"),
                    "product_store_name": order.get("product_store_name"),
                    "message": (
                        f"Order #{order.get('order_id')} is tied to store "
                        f"{order.get('store_id')} ({order.get('store_name')}), but "
                        f"product {order.get('product_id')} belongs to store "
                        f"{order.get('product_store_id')} ({order.get('product_store_name')})."
                    ),
                }
            )
    return checks


def _product_select(where: str) -> str:
    return f"""
        SELECT
            p.id AS product_id,
            p.store_id AS product_store_id,
            s.name AS product_store_name,
            p.title AS product_title,
            p.description AS product_description,
            p.category AS product_category,
            ROUND(p.price_cents / 100.0, 2) AS price_usd
        FROM products p
        JOIN stores s ON s.id = p.store_id
        WHERE {where}
    """


def _data_quality_entity(
    conn: sqlite3.Connection, case: dict[str, Any] | None, checks: list[dict[str, Any]]
) -> dict[str, Any] | None:
    if not case:
        return None
    entity_type = case.get("entity_type")
    entity_id = case.get("entity_id")
    if entity_type == "order":
        sql = _order_select("o.id = ?")
        rows = _rows(conn, sql, (entity_id,))
        checks.append({"name": "data_quality_order", "sql": sql.strip(), "params": [entity_id]})
        return {"type": "order", "rows": rows}
    if entity_type == "product":
        sql = _product_select("p.id = ?")
        rows = _rows(conn, sql, (entity_id,))
        checks.append({"name": "data_quality_product", "sql": sql.strip(), "params": [entity_id]})
        return {"type": "product", "rows": rows}
    return None


def _ground_truth(trace_id: str) -> dict[str, Any]:
    sample = _sample_by_trace_id(trace_id)
    if sample is None:
        return {"ok": False, "error": "not_found", "reason": "trace is not in samples.json"}
    if not WORLD_DB_PATH.exists():
        return {
            "ok": False,
            "error": "missing_database",
            "reason": f"{WORLD_DB_PATH} does not exist",
        }

    meta = sample.get("meta") if isinstance(sample.get("meta"), dict) else {}
    user_id = int(meta["user_id"]) if str(meta.get("user_id", "")).isdigit() else None
    role = str(meta.get("role") or "") or None
    referenced_ids = _referenced_order_ids(sample)
    dq_case_id = _data_quality_case_id(sample)
    checks: list[dict[str, Any]] = []

    conn = sqlite3.connect(f"file:{WORLD_DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        user = _dict(
            conn.execute(
                "SELECT id, name, role, store_id FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        ) if user_id is not None else None
        store_id = user.get("store_id") if user else None
        store = _dict(
            conn.execute(
                "SELECT id, name, slug, category, return_window_days_override, restocking_fee_opt_in FROM stores WHERE id = ?",
                (store_id,),
            ).fetchone()
        ) if store_id is not None else None
        checks.append(
            {
                "name": "user",
                "sql": "SELECT id, name, role, store_id FROM users WHERE id = ?",
                "params": [user_id],
            }
        )
        if store_id is not None:
            checks.append(
                {
                    "name": "merchant_store",
                    "sql": "SELECT id, name, slug, category, return_window_days_override, restocking_fee_opt_in FROM stores WHERE id = ?",
                    "params": [store_id],
                }
            )
        merchant_store_count = 1 if user and user.get("role") == "merchant" and store else 0

        scope, scope_params = _scope_clause(role, user_id, store_id)
        recent_sql = _order_select(scope) + " ORDER BY o.ordered_at DESC, o.id DESC LIMIT 20"
        recent_orders = _rows(conn, recent_sql, scope_params)
        checks.append({"name": "recent_scoped_orders", "sql": recent_sql.strip(), "params": list(scope_params)})

        referenced_orders = []
        if referenced_ids:
            placeholders = ",".join("?" for _ in referenced_ids)
            ref_sql = _order_select(f"o.id IN ({placeholders})") + " ORDER BY o.id"
            referenced_orders = _rows(conn, ref_sql, tuple(referenced_ids))
            checks.append({"name": "referenced_orders", "sql": ref_sql.strip(), "params": referenced_ids})
        data_quality_case = None
        data_quality_entity = None
        if dq_case_id:
            dq_sql = (
                "SELECT case_id, entity_type, entity_id, issue_type, description, "
                "expected_handling FROM data_quality_cases WHERE case_id = ?"
            )
            data_quality_case = _dict(conn.execute(dq_sql, (dq_case_id,)).fetchone())
            checks.append({"name": "data_quality_case", "sql": dq_sql, "params": [dq_case_id]})
            data_quality_entity = _data_quality_entity(conn, data_quality_case, checks)

        dq_orders = list(referenced_orders)
        if data_quality_entity and data_quality_entity.get("type") == "order":
            dq_orders.extend(data_quality_entity.get("rows") or [])
        data_quality_checks = _order_data_quality_checks(dq_orders)

        return {
            "ok": True,
            "trace_id": trace_id,
            "conversation_id": meta.get("conversation_id"),
            "user": user,
            "merchant_store": store,
            "merchant_store_count": merchant_store_count,
            "role_from_trace": role,
            "recent_scoped_orders": recent_orders,
            "referenced_orders": referenced_orders,
            "data_quality_case": data_quality_case,
            "data_quality_entity": data_quality_entity,
            "data_quality_checks": data_quality_checks,
            "checks": checks,
        }
    finally:
        conn.close()


class ReviewHandler(BaseHTTPRequestHandler):
    """Serves the UI and the file-backed JSON API."""

    # Quiet by default; the agent narrates the session, not the access log.
    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A002
        return

    # -- helpers ----------------------------------------------------------

    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        # Local single-user tool; permissive CORS keeps a file:// or
        # different-port UI from tripping over the browser same-origin check.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self._send_json({"error": f"not found: {path.name}"}, status=404)
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> Any:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return None
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    # -- routes -----------------------------------------------------------

    def do_OPTIONS(self) -> None:  # noqa: N802  (http.server naming)
        self._send_json({}, status=204)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self._send_file(UI_DIR / "index.html", "text/html; charset=utf-8")
            return

        # Any other static asset the UI references (kept single-file by
        # default, but this lets an adapted UI ship a companion file).
        if path.startswith("/ui/"):
            asset = UI_DIR / path[len("/ui/"):]
            if asset.is_file() and UI_DIR in asset.resolve().parents:
                self._send_file(asset, _guess_type(asset))
                return

        if path in API_FILES:
            data = _read_json(API_FILES[path], API_DEFAULTS[path])
            self._send_json(data)
            return

        if path == "/api/reviews":
            self._send_json(_read_jsonl(PILOT_REVIEW_PATH))
            return

        if path == "/api/ground_truth":
            query = parse_qs(parsed.query)
            trace_id = (query.get("trace_id") or [""])[0]
            if not trace_id:
                self._send_json(
                    {
                        "ok": False,
                        "error": "invalid_argument",
                        "reason": "trace_id is required",
                    },
                    status=400,
                )
                return
            self._send_json(_ground_truth(trace_id))
            return

        self._send_json({"error": f"unknown path: {path}"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path not in API_FILES:
            self._send_json({"error": f"cannot POST to {path}"}, status=404)
            return
        data = self._read_body()
        if data is None:
            self._send_json({"error": "expected a JSON body"}, status=400)
            return
        synced = 0
        if path == "/api/annotations":
            try:
                synced = _sync_annotation_scores(data)
            except Exception as exc:  # pragma: no cover - network-only path
                # Preserve a resumable local copy, but tell the client that
                # the canonical write did not complete.
                _write_json(API_FILES[path], data)
                self._send_json(
                    {
                        "error": f"Langfuse score write failed: {exc}",
                        "cached_locally": True,
                    },
                    status=502,
                )
                return
        _write_json(API_FILES[path], data)
        result = {"ok": True, "count": _count(data)}
        if synced:
            result["langfuse_scores_written"] = synced
        self._send_json(result)


def _count(data: Any) -> int:
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        return len(data)
    return 0


def _annotation_list(data: Any) -> list[dict[str, Any]]:
    """Normalize the annotations payload (a bare list or ``{"annotations": []}``)."""
    if isinstance(data, dict):
        data = data.get("annotations", [])
    return [a for a in data if isinstance(a, dict)] if isinstance(data, list) else []


def _sync_annotation_scores(data: Any) -> int:
    """Write labeled annotations to Langfuse scores when configured.

    Langfuse is canonical when configured, while ``annotations.json`` is the
    local mirror. The function does nothing when the ``LANGFUSE_*``
    environment is absent, so the
    offline demo, the ``--replay`` path, and the test suite never make a
    network call here. An annotation is written as a score only when it
    carries both a ``mode`` and a 0/1 ``label`` (a per-trace binary verdict);
    free-text-only notes are stored on disk but have nothing to score against.

    Return the number of scores written, or zero in offline mode. Propagate a
    Langfuse error so the server can report that the canonical write failed.
    """
    try:
        from analysis.helpers import langfuse_io
    except Exception:
        return 0
    if not langfuse_io.is_configured():
        return 0

    written = 0
    client = langfuse_io._client()
    for ann in _annotation_list(data):
        trace_id = ann.get("trace_id")
        mode = ann.get("mode")
        label = ann.get("label")
        if not trace_id or not mode or label not in (0, 1, "0", "1"):
            continue
        langfuse_io.write_label_score(
            trace_id=str(trace_id),
            mode=str(mode),
            label=int(label),
            comment=ann.get("note"),
            client=client,
        )
        written += 1
    return written


def _guess_type(path: Path) -> str:
    return {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css",
        ".js": "text/javascript",
        ".json": "application/json",
        ".svg": "image/svg+xml",
    }.get(path.suffix, "application/octet-stream")


# ---------------------------------------------------------------------------
# Demo replay: append canned annotations on a timer.
# ---------------------------------------------------------------------------


def _load_canned(replay_path: Path) -> list[Any]:
    """Read the canned annotations, accepting either on-disk shape.

    The committed demo file wraps its list as ``{"annotations": [...]}`` (it
    carries a little metadata alongside), while an ad-hoc file may be a bare
    list. Accept both so the demo fallback does not care which the course seed
    produced. Each annotation is given a stable ``id`` if it lacks one, so the
    UI's id-based merge and de-duplication work on replayed items.
    """
    raw = _read_json(replay_path, None)
    if isinstance(raw, dict):
        raw = raw.get("annotations", [])
    if not isinstance(raw, list):
        return []
    out: list[Any] = []
    for i, ann in enumerate(raw):
        if isinstance(ann, dict) and "id" not in ann:
            ann = {**ann, "id": f"replay-{i}"}
        out.append(ann)
    return out


def _replay_annotations(replay_path: Path, interval: float) -> None:
    """Append the canned annotations to state/annotations.json on a timer.

    Reads the whole canned list up front, then adds one annotation every
    ``interval`` seconds. The watcher and the UI both poll annotations.json, so
    grouping and the suggestion pipeline fire exactly as they would in a live
    session. Idempotent enough for a demo: it starts from an empty live file so
    a re-run replays from the top.
    """
    canned = _load_canned(replay_path)
    if not canned:
        print(f"[replay] nothing to replay from {replay_path}")
        return
    live_path = API_FILES["/api/annotations"]
    _write_json(live_path, [])
    print(f"[replay] replaying {len(canned)} annotations, one per {interval:g}s")
    accumulated: list[Any] = []
    for i, ann in enumerate(canned, start=1):
        time.sleep(interval)
        accumulated.append(ann)
        _write_json(live_path, accumulated)
        note = ann.get("note", "") if isinstance(ann, dict) else ""
        print(f"[replay] {i}/{len(canned)}: {note[:70]}")
    print("[replay] done")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8020)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument(
        "--replay",
        metavar="PATH",
        help="canned annotations file to replay on a timer (e.g. "
        "state/demo_annotations.json), for the demo fallback",
    )
    parser.add_argument(
        "--replay-interval",
        type=float,
        default=4.0,
        help="seconds between replayed annotations (default 4)",
    )
    args = parser.parse_args()

    STATE_DIR.mkdir(parents=True, exist_ok=True)

    if args.replay:
        replay_path = Path(args.replay)
        if not replay_path.is_absolute():
            replay_path = HERE / replay_path
        thread = threading.Thread(
            target=_replay_annotations,
            args=(replay_path, args.replay_interval),
            daemon=True,
        )
        thread.start()

    server = ThreadingHTTPServer((args.host, args.port), ReviewHandler)
    url = f"http://{args.host}:{args.port}/"
    print(f"review interface on {url}")
    print(f"serving state from {STATE_DIR}")
    print("open the URL, read a trace, select the failing text, type a note.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
        server.shutdown()


if __name__ == "__main__":
    main()
