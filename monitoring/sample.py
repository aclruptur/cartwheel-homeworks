"""Select a random sample for estimation and extra traces for inspection."""

from __future__ import annotations

from typing import Any, Callable


def select_traces(
    traces: list[dict[str, Any]],
    random_rate: float,
    risk_groups: dict[str, Callable[[dict[str, Any]], bool]],
    seed: int = 7,
) -> dict[str, Any]:
    """Select the traces that the LLM judge will review.

    The returned plan keeps two kinds of traces separate:

      1. **Random sample.** Draw
         ``max(1, round(random_rate * len(traces)))`` traces uniformly at
         random without replacement, using
         ``random.Random(seed).sample`` on the traces in their given order.
         Only this sample may be used to estimate the failure rate.
      2. **Risk groups.** For each group in ``risk_groups``, include every
         matching trace. A trace can appear in more than one group.
      3. **All traces to judge.** ``to_judge`` contains every unique trace
         selected by either method. Deduplicate the traces by ``"id"`` and
         keep the random traces first, followed by the risk groups in their
         dictionary order.
      4. Each trace dict is passed through untouched; membership lives in
         the returned plan, not as mutations of the inputs.

    Args:
        traces: the batch, each dict carrying at least an "id".
        random_rate: random sampling rate in (0, 1].
        risk_groups: group name mapped to a predicate over a trace dict.
        seed: RNG seed; the same inputs and seed produce the same plan.

    Returns:
        {"random": [trace, ...],
         "risk_groups": {name: [trace, ...], ...},
         "to_judge": [trace, ...]}

    Raises:
        ValueError: if random_rate is outside (0, 1] or a trace has no "id".
    """
    import random

    if not (0 < random_rate <= 1):
        raise ValueError("random_rate must be in (0, 1]")
    for trace in traces:
        if not trace.get("id"):
            raise ValueError("every trace must have an id")

    sample_size = max(1, round(random_rate * len(traces))) if traces else 0
    rng = random.Random(seed)
    random_sample = rng.sample(traces, sample_size) if sample_size else []

    selected_risk_groups: dict[str, list[dict[str, Any]]] = {}
    for name, predicate in risk_groups.items():
        selected_risk_groups[name] = [trace for trace in traces if predicate(trace)]

    seen: set[str] = set()
    to_judge: list[dict[str, Any]] = []
    for trace in random_sample:
        trace_id = str(trace["id"])
        if trace_id not in seen:
            seen.add(trace_id)
            to_judge.append(trace)
    for group_traces in selected_risk_groups.values():
        for trace in group_traces:
            trace_id = str(trace["id"])
            if trace_id not in seen:
                seen.add(trace_id)
                to_judge.append(trace)

    return {
        "random": list(random_sample),
        "risk_groups": selected_risk_groups,
        "to_judge": to_judge,
    }


# Each function identifies one risk group in the Cartwheel traces.
DEFAULT_RISK_GROUPS: dict[str, Callable[[dict[str, Any]], bool]] = {
    "policy_lookup": lambda t: bool(
        {"get_policy", "search_help_center"} & set(t.get("tools", t.get("tool_names", [])))
    ),
    "write_action": lambda t: bool(
        {"issue_refund", "cancel_order"} & set(t.get("tools", t.get("tool_names", [])))
    ),
    "multi_turn": lambda t: int(t.get("turn_count", t.get("user_turns", 0))) > 1,
    "override_policy_question": lambda t: bool(
        t.get("segments", {}).get("store_override_topic")
    ),
    "above_threshold_refund": lambda t: bool(
        t.get("segments", {}).get("above_threshold_refund")
    ),
}
