"""Run the frozen Module 2 judges over the sampled traces.

Instructor-provided. This is the expensive track of the two-track plan: the
code checks run on 100 percent of the stream because they are free, and the
judges run only on the plan `monitoring/sample.py` produced, asynchronously
off the serving path (here: a batch job, which at course scale is the same
thing).

Each trace dict needs "id", "final_reply", and "retrieved_docs" (the
policy text the agent saw; the judge grades support, so it sees what the
agent saw). The judge is the frozen Module 2 judge, prompt and model pinned;
the call goes through the same LiteLLM routing as the course models.
"""

from __future__ import annotations

from typing import Any

from replay.rollout import judge_reply, load_frozen_judge


def judge_sample(
    mode: str, traces: list[dict[str, Any]]
) -> dict[str, int]:
    """Run the frozen judge for ``mode`` over the sampled traces.

    Returns trace_id -> 0/1 verdict in the failure-positive convention the
    whole course uses (1 = the failure is present, i.e. the judge said
    "fail"). Requires the judge model's API key.
    """
    judge = load_frozen_judge(mode)
    verdicts: dict[str, int] = {}
    for trace in traces:
        answer = judge_reply(
            judge,
            trace.get("final_reply", ""),
            trace.get("retrieved_docs", "(no policy documents were retrieved)"),
        )
        verdicts[trace["id"]] = 1 if answer == "fail" else 0
    return verdicts


def judge_test_data(mode: str) -> tuple[list[int], list[int]]:
    """Load held-out labels and frozen predictions in failure-positive form.

    The frozen judge stores 1 for a judged failure and 0 for pass. The HW5
    split file carries the held-out test ids. For the course-supplied
    unsupported-policy cases, ids containing ``fail`` plus demo ids D7/D10 are
    human-labeled failures; ids containing ``pass`` are human-labeled passes.
    """
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    judge = load_frozen_judge(mode)
    judge_id = judge["judge_id"]
    judge_state = json.loads((root / "analysis" / "state" / "judges" / f"{judge_id}.json").read_text())
    splits = json.loads((root / "analysis" / "state" / "splits.json").read_text())
    test_ids = splits[mode]["test"]
    predictions = judge_state["predictions"][judge_state["prompt_hash"]]

    labels: list[int] = []
    preds: list[int] = []
    known_demo_failures = {"D7", "D10", "T2"}
    for trace_id in test_ids:
        if "fail" in trace_id or trace_id in known_demo_failures:
            label = 1
        elif "pass" in trace_id:
            label = 0
        else:
            raise ValueError(f"cannot infer held-out label for {trace_id!r}")
        if trace_id not in predictions:
            raise ValueError(f"missing frozen prediction for {trace_id!r}")
        labels.append(label)
        preds.append(int(predictions[trace_id]))
    return labels, preds
