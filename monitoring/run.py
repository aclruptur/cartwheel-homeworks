"""Run the Homework 7 monitoring job over Langfuse traces."""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from analysis.helpers.normalization import normalize_trace
from monitoring.chart import prevalence_chart
from monitoring.correct import corrected_mode_prevalence
from monitoring.sample import DEFAULT_RISK_GROUPS, select_traces
from monitoring.run_judges import judge_sample, judge_test_data
from monitoring.write_scores import build_score_records, post_scores

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "monitoring" / "config.json"
SCENARIOS_PATH = REPO_ROOT / "scenarios" / "monitoring_scenarios.jsonl"
OUTPUT_DIR = REPO_ROOT / "monitoring" / "outputs"
HISTORY_PATH = REPO_ROOT / "monitoring" / "history.jsonl"
CHART_PATH = REPO_ROOT / "monitoring" / "prevalence.svg"


def _load_env() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "model_dump"):
        return _jsonable(value.model_dump(mode="json", by_alias=True))
    if hasattr(value, "dict"):
        return _jsonable(value.dict(by_alias=True))
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "__dict__"):
        return {
            key: _jsonable(item)
            for key, item in vars(value).items()
            if not key.startswith("_")
        }
    return value


def _metadata_attrs(record: dict[str, Any]) -> dict[str, Any]:
    metadata = record.get("metadata") if isinstance(record, dict) else {}
    if not isinstance(metadata, dict):
        return {}
    attributes = metadata.get("attributes")
    return attributes if isinstance(attributes, dict) else {}


def _scenario_id(record: dict[str, Any]) -> str | None:
    metadata = record.get("metadata") if isinstance(record, dict) else {}
    attrs = _metadata_attrs(record)
    if isinstance(metadata, dict):
        return (
            record.get("cartwheel_scenario_id")
            or attrs.get("cartwheel.scenario_id")
            or metadata.get("cartwheel.scenario_id")
            or metadata.get("scenario_id")
        )
    return record.get("cartwheel_scenario_id")


def _session_id(record: dict[str, Any]) -> str | None:
    metadata = record.get("metadata") if isinstance(record, dict) else {}
    attrs = _metadata_attrs(record)
    if isinstance(metadata, dict):
        return (
            record.get("sessionId")
            or record.get("session_id")
            or attrs.get("cartwheel.session_id")
            or metadata.get("cartwheel.session_id")
        )
    return record.get("sessionId") or record.get("session_id")


def _trace_time(trace: dict[str, Any]) -> str:
    return str(trace.get("timestamp") or "")


def _load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    return json.loads(path.read_text())


def _load_scenario_ids(path: Path = SCENARIOS_PATH) -> list[str]:
    ids: list[str] = []
    for line in path.read_text().splitlines():
        if line.strip():
            ids.append(json.loads(line)["id"])
    if len(ids) != len(set(ids)):
        raise ValueError("monitoring scenarios contain duplicate ids")
    return ids


def _period(config: dict[str, Any], label: str) -> dict[str, Any]:
    for period in config.get("periods", []):
        if period.get("label") == label:
            return period
    raise ValueError(f"unknown period: {label}")


def fetch_period_traces(period: dict[str, Any]) -> list[dict[str, Any]]:
    """Fetch full Langfuse traces whose timestamps fall in the period."""
    _load_env()
    from langfuse import Langfuse

    client = Langfuse()
    start = _parse_time(period["from"])
    end = _parse_time(period["to"])
    records: list[dict[str, Any]] = []
    page = 1
    page_size = 100
    while True:
        response = client.api.trace.list(page=page, limit=page_size)
        batch = list(response.data or [])
        if not batch:
            break
        for trace_summary in batch:
            summary = _jsonable(trace_summary)
            timestamp = summary.get("timestamp") or summary.get("createdAt")
            if not timestamp:
                continue
            ts = _parse_time(str(timestamp))
            if not (start <= ts <= end):
                continue
            full = client.api.trace.get(summary["id"])
            records.append(_jsonable(full))
        if len(batch) < page_size:
            break
        page += 1
    return records


def _model_ok(trace: dict[str, Any], expected_model: str) -> bool:
    models = {str(model) for model in (trace.get("models") or []) if model}
    for obs in trace.get("observations") or []:
        model = obs.get("model")
        if model:
            models.add(str(model))
    # Langfuse exports for the HW3/HW7 runs do not always include model metadata
    # on traces or observations. The scenario result files record the model; here
    # we reject only explicit evidence of a different model.
    if not models:
        return True
    return any(model == expected_model or model.startswith(f"{expected_model}-") for model in models)


def _message_text(message: dict[str, Any]) -> str:
    if message.get("text") is not None:
        return str(message.get("text"))
    if message.get("content") is not None:
        return str(message.get("content"))
    return ""


def _conversation_text(traces: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for trace in traces:
        timestamp = trace.get("timestamp") or ""
        lines.append(f"Trace {trace['id']} {timestamp}".strip())
        for message in trace.get("trace") or []:
            role = str(message.get("role") or "step")
            name = message.get("name") or message.get("label")
            prefix = f"{role.upper()} {name}" if name else role.upper()
            text = _message_text(message)
            if text:
                lines.append(f"{prefix}: {text}")
        lines.append("")
    return "\n".join(lines).strip()


def _final_reply(traces: list[dict[str, Any]]) -> str:
    for trace in reversed(traces):
        for message in reversed(trace.get("trace") or []):
            if message.get("role") == "assistant":
                text = _message_text(message).strip()
                if text:
                    return text
    return ""


def _retrieved_docs(traces: list[dict[str, Any]]) -> str:
    chunks: list[str] = []
    for trace in traces:
        for message in trace.get("trace") or []:
            role = message.get("role")
            name = str(message.get("name") or message.get("label") or "")
            content = message.get("content")
            if role != "tool_result":
                continue
            if "search_help_center" in name and isinstance(content, dict):
                for hit in content.get("results", []) or []:
                    if isinstance(hit, dict):
                        chunks.append(
                            f"[{hit.get('policy_id')}] {hit.get('title')}: {hit.get('snippet')}"
                        )
            elif "get_policy" in name and isinstance(content, dict):
                chunks.append(f"[{content.get('policy_id')}] {content.get('body', '')}")
    return "\n\n".join(chunk for chunk in chunks if chunk.strip()) or "(no policy documents were retrieved)"


def _tool_names(traces: list[dict[str, Any]]) -> list[str]:
    names: list[str] = []
    for trace in traces:
        for message in trace.get("trace") or []:
            if message.get("role") == "tool_call" and message.get("name"):
                names.append(str(message["name"]))
    return names


def _tool_result_payloads(traces: list[dict[str, Any]], tool_name: str) -> list[Any]:
    payloads: list[Any] = []
    for trace in traces:
        for message in trace.get("trace") or []:
            if message.get("role") != "tool_result":
                continue
            name = str(message.get("name") or message.get("label") or "")
            if tool_name in name:
                payloads.append(message.get("content"))
    return payloads


def _has_above_threshold_refund(traces: list[dict[str, Any]], tool_names: list[str]) -> bool:
    if "issue_refund" not in tool_names:
        return False
    for payload in _tool_result_payloads(traces, "issue_refund"):
        if isinstance(payload, dict):
            status = str(payload.get("status") or payload.get("refund_status") or "").lower()
            if "approval" in status or "queued" in status:
                return True
            for key in ("amount", "amount_usd", "refund_amount", "refund_amount_usd"):
                value = payload.get(key)
                if isinstance(value, (int, float)) and value > 100:
                    return True
    return False


def _segments(
    traces: list[dict[str, Any]],
    tool_names: list[str],
    retrieved_docs: str,
    user_turns: int,
) -> dict[str, Any]:
    docs = retrieved_docs.lower()
    return {
        "store_override_topic": "cw-store-overrides" in docs or "store override" in docs,
        "above_threshold_refund": _has_above_threshold_refund(traces, tool_names),
        "policy_lookup": any(name in {"search_help_center", "get_policy"} for name in tool_names),
        "write_action": any(name in {"issue_refund", "cancel_order"} for name in tool_names),
        "multi_turn": user_turns > 1,
    }


def _conversation_record(session_id: str, traces: list[dict[str, Any]]) -> dict[str, Any]:
    traces = sorted(traces, key=_trace_time)
    final_trace = traces[-1]
    tool_names = _tool_names(traces)
    text = _conversation_text(traces)
    retrieved_docs = _retrieved_docs(traces)
    user_turns = sum(
        1 for trace in traces for message in trace.get("trace", []) if message.get("role") == "user"
    )
    return {
        "id": final_trace["id"],
        "session_id": session_id,
        "scenario_id": final_trace.get("meta", {}).get("scenario_id"),
        "trace_ids": [trace["id"] for trace in traces],
        "text": text,
        "final_reply": _final_reply(traces),
        "retrieved_docs": retrieved_docs,
        "tool_names": tool_names,
        "user_turns": user_turns,
        "segments": _segments(traces, tool_names, retrieved_docs, user_turns),
        "signals": {},
        "timestamp": final_trace.get("timestamp"),
    }


def build_session_records(
    raw_records: list[dict[str, Any]],
    *,
    model: str,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for raw in raw_records:
        session_id = _session_id(raw)
        if not session_id:
            continue
        normalized_trace = normalize_trace(raw)
        if not _model_ok(normalized_trace, model):
            continue
        normalized_trace.setdefault("meta", {})["conversation_id"] = session_id
        normalized.append(normalized_trace)

    by_session: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for trace in normalized:
        session_id = trace.get("meta", {}).get("conversation_id")
        if session_id:
            by_session[str(session_id)].append(trace)

    return [
        _conversation_record(session_id, traces)
        for session_id, traces in sorted(by_session.items())
        if traces
    ]


def build_conversation_records(
    raw_records: list[dict[str, Any]],
    *,
    expected_ids: list[str],
    model: str,
) -> list[dict[str, Any]]:
    normalized = []
    for raw in raw_records:
        scenario_id = _scenario_id(raw)
        if scenario_id not in set(expected_ids):
            continue
        raw.setdefault("cartwheel_scenario_id", scenario_id)
        normalized.append(normalize_trace(raw))

    by_scenario: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for trace in normalized:
        scenario_id = trace.get("meta", {}).get("scenario_id")
        if scenario_id in set(expected_ids):
            by_scenario[str(scenario_id)].append(trace)

    missing = [scenario_id for scenario_id in expected_ids if scenario_id not in by_scenario]
    if missing:
        raise ValueError(f"period is missing {len(missing)} scenario ids: {missing[:10]}")
    extra = sorted(set(by_scenario) - set(expected_ids))
    if extra:
        raise ValueError(f"period contains unexpected scenario ids: {extra[:10]}")

    records: list[dict[str, Any]] = []
    for scenario_id in expected_ids:
        traces = sorted(by_scenario[scenario_id], key=_trace_time)
        for trace in traces:
            if not _model_ok(trace, model):
                raise ValueError(f"{scenario_id}: trace {trace['id']} used a different model")
        records.append(_conversation_record(scenario_id, traces))
    if len(records) != 50:
        raise ValueError(f"expected 50 conversation records, got {len(records)}")
    return records


def _selected_risk_verdicts(plan: dict[str, Any], verdicts: dict[str, int]) -> dict[str, dict[str, int]]:
    return {
        name: {trace["id"]: verdicts[trace["id"]] for trace in traces if trace["id"] in verdicts}
        for name, traces in plan["risk_groups"].items()
    }


def _risk_union_verdicts(risk_verdicts: dict[str, dict[str, int]]) -> dict[str, int]:
    union: dict[str, int] = {}
    for group_verdicts in risk_verdicts.values():
        for trace_id, verdict in group_verdicts.items():
            union[trace_id] = verdict
    return union


def _upsert_history(record: dict[str, Any]) -> list[dict[str, Any]]:
    existing: list[dict[str, Any]] = []
    if HISTORY_PATH.exists():
        existing = [json.loads(line) for line in HISTORY_PATH.read_text().splitlines() if line.strip()]
    by_label = {row["period"]: row for row in existing}
    by_label[record["period"]] = record
    order = [period["label"] for period in _load_config().get("periods", [])]
    rows = [by_label[label] for label in order if label in by_label]
    rows.extend(row for label, row in by_label.items() if label not in order)
    HISTORY_PATH.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
    return rows


def _refresh_chart(history_rows: list[dict[str, Any]], config: dict[str, Any]) -> None:
    points = [
        {
            "label": row["period"],
            "corrected": row["corrected_rate"],
            "ci_low": row["ci_low"],
            "ci_high": row["ci_high"],
        }
        for row in history_rows
    ]
    if points:
        CHART_PATH.write_text(
            prevalence_chart(points, threshold=config["threshold"], mode=config["judge_mode"]) + "\n"
        )


def _score_timestamp(label: str, config: dict[str, Any]) -> datetime:
    for period in config.get("periods", []):
        if period.get("label") == label and period.get("to"):
            return _parse_time(str(period["to"]))
    return datetime.now(timezone.utc)


def _write_monitor_outputs(result: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    _load_env()
    test_labels, test_preds = judge_test_data(config["judge_id"])
    random_verdicts = result["random_verdicts"]
    risk_verdicts = result["risk_verdicts"]
    estimate = corrected_mode_prevalence(
        list(random_verdicts.values()),
        test_labels,
        test_preds,
    )
    risk_union = _risk_union_verdicts(risk_verdicts)
    score_records = build_score_records(
        config["judge_mode"],
        random_verdicts,
        risk_union,
        estimate,
        result["period"],
        timestamp=_score_timestamp(result["period"], config),
    )
    posted = post_scores(score_records)
    history_record = {
        "period": result["period"],
        "judge_id": config["judge_id"],
        "model": config["model"],
        "trace_count": result["trace_count"],
        "window_trace_count": result.get("window_trace_count", result["trace_count"]),
        "conversation_count": result["conversation_count"],
        "random_sample_count": len(random_verdicts),
        "risk_sample_count": len(risk_union),
        "raw_rate": estimate["raw"],
        "corrected_rate": estimate["corrected"],
        "ci_low": estimate["ci_low"],
        "ci_high": estimate["ci_high"],
        "interval": [estimate["ci_low"], estimate["ci_high"]],
        "confidence": estimate["confidence"],
        "failure_sensitivity": estimate["failure_sensitivity"],
        "pass_specificity": estimate["pass_specificity"],
        "validity_warning": estimate["validity_warning"],
    }
    history_rows = _upsert_history(history_record)
    _refresh_chart(history_rows, config)
    return {
        "estimate": estimate,
        "score_record_count": len(score_records),
        "posted_score_count": posted,
        "history_record": history_record,
    }


def load_existing_verdicts(label: str) -> dict[str, Any]:
    path = OUTPUT_DIR / f"{label}-verdicts.json"
    if not path.exists():
        raise FileNotFoundError(f"missing verdict file: {path}")
    return json.loads(path.read_text())


def _run_records(
    label: str,
    records: list[dict[str, Any]],
    raw_record_count: int,
    config: dict[str, Any],
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    selected_groups = {
        name: DEFAULT_RISK_GROUPS[name]
        for name in config.get("risk_groups", [])
    }
    plan = select_traces(records, config["random_rate"], selected_groups)
    random_ids = [trace["id"] for trace in plan["random"]]
    risk_ids = {name: [trace["id"] for trace in traces] for name, traces in plan["risk_groups"].items()}
    to_judge_ids = [trace["id"] for trace in plan["to_judge"]]
    matched_trace_count = sum(len(record["trace_ids"]) for record in records)
    print(
        f"{label}: {matched_trace_count} matched Langfuse traces "
        f"({raw_record_count} total traces in time window) -> {len(records)} conversations; "
        f"random={len(random_ids)}, risk_union={len(set().union(*[set(v) for v in risk_ids.values()]) if risk_ids else set())}, "
        f"judge_calls={len(to_judge_ids)}"
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    preview = {
        "period": label,
        "trace_count": matched_trace_count,
        "window_trace_count": raw_record_count,
        "conversation_count": len(records),
        "random_ids": random_ids,
        "risk_ids": risk_ids,
        "to_judge_ids": to_judge_ids,
        "records": records,
    }
    (OUTPUT_DIR / f"{label}-selection.json").write_text(json.dumps(preview, indent=2) + "\n")
    if dry_run:
        return {**preview, "verdicts": {}}

    verdicts = judge_sample(config["judge_id"], plan["to_judge"])
    result = {
        "period": label,
        "judge_id": config["judge_id"],
        "judge_mode": config["judge_mode"],
        "model": config["model"],
        "trace_count": matched_trace_count,
        "window_trace_count": raw_record_count,
        "conversation_count": len(records),
        "random_verdicts": {trace_id: verdicts[trace_id] for trace_id in random_ids if trace_id in verdicts},
        "risk_verdicts": _selected_risk_verdicts(plan, verdicts),
        "all_verdicts": verdicts,
    }
    write_result = _write_monitor_outputs(result, config)
    result.update(write_result)
    (OUTPUT_DIR / f"{label}-verdicts.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def run_period(label: str, *, dry_run: bool = False) -> dict[str, Any]:
    config = _load_config()
    period = _period(config, label)
    expected_ids = _load_scenario_ids()
    raw_records = fetch_period_traces(period)
    records = build_conversation_records(raw_records, expected_ids=expected_ids, model=config["model"])
    return _run_records(label, records, len(raw_records), config, dry_run=dry_run)


def run_last_hours(hours: int, *, dry_run: bool = False) -> dict[str, Any]:
    if hours <= 0:
        raise ValueError("--last-hours must be positive")
    config = _load_config()
    now = datetime.now(timezone.utc)
    period = {
        "label": f"last-{hours}-hours",
        "from": (now - timedelta(hours=hours)).isoformat().replace("+00:00", "Z"),
        "to": now.isoformat().replace("+00:00", "Z"),
    }
    raw_records = fetch_period_traces(period)
    records = build_session_records(raw_records, model=config["model"])
    if not records:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out = {
            "mode": "last-hours",
            "period": period["label"],
            "from": period["from"],
            "to": period["to"],
            "trace_count": 0,
            "window_trace_count": len(raw_records),
            "conversation_count": 0,
            "random_sample_count": 0,
            "risk_sample_count": 0,
            "judge_calls": 0,
            "note": "no eligible conversations found; judge was not called",
        }
        (OUTPUT_DIR / "last-hours.json").write_text(json.dumps(out, indent=2) + "\n")
        return out
    return _run_records(period["label"], records, len(raw_records), config, dry_run=dry_run)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the HW7 monitor for one period.")
    parser.add_argument("--period", choices=["before", "after"], help="configured period label")
    parser.add_argument("--dry-run", action="store_true", help="fetch, validate, and sample without judge calls")
    parser.add_argument("--write-existing", action="store_true", help="write scores/history from an existing verdict file without judge calls")
    parser.add_argument("--last-hours", type=int, default=None, help="scheduled mode placeholder")
    args = parser.parse_args()
    if args.last_hours is not None:
        result = run_last_hours(args.last_hours, dry_run=args.dry_run)
        print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2))
        return
    if not args.period:
        parser.error("--period is required unless --last-hours is used")
    if args.write_existing:
        config = _load_config()
        result = load_existing_verdicts(args.period)
        result.update(_write_monitor_outputs(result, config))
        (OUTPUT_DIR / f"{args.period}-verdicts.json").write_text(json.dumps(result, indent=2) + "\n")
    else:
        result = run_period(args.period, dry_run=args.dry_run)
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2))


if __name__ == "__main__":
    main()
