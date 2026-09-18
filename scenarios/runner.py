"""Scripted scenario runner. Instructor-provided and complete.

Plays each scenario from a JSONL file against the running endpoint
(server/app.py), 1 to 3 turns, sequentially. Sequential execution is fine at
course scale; a full simulated-user loop is deferred to Module 3's sandbox.

Each turn sends the scenario id along, so the server stamps
`cartwheel.scenario_id` on the trace and Module 3 can join traces back to
ground truth.

Usage:
    uv run uvicorn server.app:app --port 8010          # in one terminal
    uv run python -m scenarios.runner path/to/scenarios.jsonl \
        --model gpt-5.5 [--base-url http://localhost:8010] [--limit 50] \
        [--output scenarios/final-primary.jsonl]

Without ``--output``, results land in the gitignored scratch directory
``scenarios/results/``. Homework submissions should name an output explicitly.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from scenarios.validate import load_jsonl, validate_scenarios

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "scenarios" / "results"

# Demo users per role (seeded by seed/generate.py). A scenario tuple may
# name an explicit user_id instead.
DEFAULT_USERS = {"shopper": 1, "merchant": 9001, "support": 9501}
MAX_TURNS_PER_SCENARIO = 3
REQUEST_TIMEOUT_S = 180


def _post(url: str, payload: dict[str, Any], token: str | None = None) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_S) as response:
        return json.loads(response.read())


def load_scenarios(path: Path) -> list[dict[str, Any]]:
    scenarios = load_jsonl(path)
    validate_scenarios(scenarios)
    return scenarios


def load_results(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return load_jsonl(path)


def selected_scenarios(
    scenarios: list[dict[str, Any]],
    *,
    limit: int | None,
    resume: bool,
    ids: set[str] | None,
    existing_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if limit is not None:
        scenarios = scenarios[:limit]

    if ids:
        return [scenario for scenario in scenarios if scenario["id"] in ids]

    if not resume:
        return scenarios

    completed_ids = {
        row["scenario_id"] for row in existing_results if row.get("status") == "completed"
    }
    return [scenario for scenario in scenarios if scenario["id"] not in completed_ids]


def merge_results(
    scenarios: Iterable[dict[str, Any]],
    existing_results: list[dict[str, Any]],
    fresh_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    fresh_by_id = {row["scenario_id"]: row for row in fresh_results}
    existing_by_id = {row["scenario_id"]: row for row in existing_results}
    merged: list[dict[str, Any]] = []
    for scenario in scenarios:
        scenario_id = scenario["id"]
        if scenario_id in fresh_by_id:
            merged.append(fresh_by_id[scenario_id])
        elif scenario_id in existing_by_id:
            merged.append(existing_by_id[scenario_id])
    return merged


def run_scenario(
    scenario: dict[str, Any], base_url: str, model: str | None
) -> dict[str, Any]:
    """Play one scenario end to end. Returns a result record."""
    tuple_ = scenario.get("tuple", {})
    role = tuple_.get("role", "shopper")
    user_id = tuple_.get("user_id", DEFAULT_USERS.get(role, 1))
    turns: list[dict[str, str]] = []
    started = time.time()
    try:
        session = _post(f"{base_url}/sessions", {"user_id": user_id, "role": role})
        messages = [scenario["opening_message"]]
        followups = scenario.get("followups") or []
        # Every followup is an exact user utterance. The scenario skill forbids
        # persona notes or generation instructions in this field.
        messages.extend(followups[: MAX_TURNS_PER_SCENARIO - 1])
        for message in messages:
            reply = _post(
                f"{base_url}/sessions/{session['session_id']}/messages",
                {
                    "message": message,
                    "model": model,
                    "scenario_id": scenario["id"],
                    "expected": scenario["expected"],
                },
                token=session["token"],
            )
            turns.append({"user": message, "agent": reply["reply"]})
        status = "completed"
        error = None
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError) as exc:
        status = "error"
        error = str(exc)
    return {
        "scenario_id": scenario["id"],
        "scenario_group": scenario["scenario_group"],
        "model": model,
        "status": status,
        "error": error,
        "turns": turns,
        "expected": scenario["expected"],
        "duration_s": round(time.time() - started, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run scenarios against the endpoint.")
    parser.add_argument("scenarios", type=Path, help="scenario JSONL file")
    parser.add_argument("--base-url", default="http://localhost:8010")
    parser.add_argument("--limit", type=int, default=None, help="run only the first N")
    parser.add_argument("--model", required=True, help="model recorded on every request and result")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="explicit result JSONL path (recommended for committed homework artifacts)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="keep completed records in the output file and rerun only missing or non-completed scenarios",
    )
    parser.add_argument(
        "--ids",
        default=None,
        help="comma-separated scenario ids to rerun; their records replace any earlier results in the output file",
    )
    args = parser.parse_args()

    out_path = args.output or RESULTS_DIR / f"run-{int(time.time())}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if args.resume and args.output is None:
        raise SystemExit("--resume requires --output so the runner knows which results file to update")

    ids = {value.strip() for value in (args.ids or "").split(",") if value.strip()} or None
    if args.resume and ids:
        raise SystemExit("use either --resume or --ids, not both")

    scenarios = load_scenarios(args.scenarios)
    existing_results = load_results(out_path) if (args.resume or ids) else []
    scheduled = selected_scenarios(
        scenarios,
        limit=args.limit,
        resume=args.resume,
        ids=ids,
        existing_results=existing_results,
    )

    completed = 0
    fresh_results: list[dict[str, Any]] = []
    total = len(scheduled)
    for i, scenario in enumerate(scheduled, start=1):
        result = run_scenario(scenario, args.base_url, args.model)
        fresh_results.append(result)
        completed += result["status"] == "completed"
        print(f"[{i}/{total}] {result['scenario_id']}: {result['status']}")

    final_results = merge_results(scenarios[: args.limit] if args.limit is not None else scenarios, existing_results, fresh_results)
    with open(out_path, "w") as out:
        for result in final_results:
            out.write(json.dumps(result) + "\n")
            out.flush()

    if args.resume:
        total_label = f"{completed}/{total} rerun completed"
    elif ids:
        total_label = f"{completed}/{total} targeted reruns completed"
    else:
        total_label = f"{completed}/{total} completed"

    print(f"\n{total_label}. Results: {out_path}")
    print("Now open Langfuse and run reports/smoke.sql against ClickHouse.")


if __name__ == "__main__":
    main()
