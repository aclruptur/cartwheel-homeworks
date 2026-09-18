# Raindrop Workshop notes

Part C used a local Raindrop Workshop installation and the `/instrument-agent` workflow. The Cartwheel CLI now mirrors each `--raindrop` turn to Workshop as a top-level interaction while preserving the existing Langfuse/OpenTelemetry setup. Because this local installation has no Raindrop Cloud write key, true Raindrop OTLP tool spans are not enabled; the CLI records tool count, tool names, and tool success flags as interaction metadata instead.

## Inspected Workshop runs

| Workshop run id | Role / user | Input | Tool activity from metadata | Candidate failure or unusual behavior |
| --- | --- | --- | --- | --- |
| `cli-shopper-1-1789750589-1` | shopper / 1 | "I want help with my order." | `list_my_orders` | The assistant gives a useful recent-order shortlist and asks for the order number. Minor hypothesis only: formatting still uses Markdown bold markers that may be noisy in plain-text surfaces. This supports the existing `presentation_formatting_noise` mode rather than a new mode. |
| `cli-shopper-1-1789750621-1` | shopper / 1 | "It was the one with the vase, I think." | `find_order` | The assistant correctly treats the item reference as ambiguous and asks the shopper to choose among three vase orders. This is a close negative for `missing_clarification_or_disambiguation`. |
| `cli-shopper-1-1789750627-1` | shopper / 1 | "For order 3980, am I still eligible for a return or refund? Please do not start anything." | `get_order` | The assistant respects the no-action instruction and reports that the order is not refund eligible. No failure observed from Workshop inspection. |
| `cli-merchant-9001-1789750633-1` | merchant / 9001 | "How many stores do I have in the store directory?" | `lookup_store_directory` | The answer is concise and grounded in the directory result. No failure observed from Workshop inspection. |
| `cli-support-9501-1789750638-1` | support / 9501 | "Please inspect order 8003 and tell me whether the store information looks normal." | `get_order`, `lookup_store_directory` | The assistant says the store information looks normal, but the local database shows order 8003 has `store_id=1` while product 553 belongs to `store_id=14`. Workshop exposed that the agent checked the order store against the directory but did not compare the order's product store. This supports the existing `unhandled_data_quality_or_record_inconsistency` mode. |
| `cli-support-9503-1789750646-1` | support / 9503 | "What is the rule when the assistant cannot resolve a case from policy and the order record alone?" | `search_help_center` | The assistant cites `cw-escalations` and includes the 24-hour SLA. Possible presentation hypothesis: for an internal support user, naming the policy may be useful; earlier annotations treated extra policy-name detail as noisy in some contexts. This is an uncertainty case, not a label. |
| `cli-merchant-9001-1789750652-1` | merchant / 9001 | "What restocking fee policy applies to my store?" | `lookup_store_directory`, `search_help_center`, `search_help_center`, `get_policy` | The assistant looks up broad restocking policy and then searches for a Blue Heron store-specific policy. It correctly says it did not find store-specific opt-in evidence. Unusual behavior: the first search returned other stores' policies, which could create overload or wrong-store risk if copied into the answer. The final answer avoided that risk. |

## Uncertainty / alternative explanation

The support policy run `cli-support-9503-1789750646-1` includes the sentence "A human responds within 24 hours" and the explicit policy name `cw-escalations`. In some human annotations we treated extra policy identifiers or extra detail as noisy, but this case is an internal support-user question about the rule itself. The better interpretation may be that the SLA and policy id are helpful evidence for a support user. I would not treat this as a failure without a clearer product requirement about how much citation detail support users should receive.

## Suggestions and decisions

- Workshop suggestion accepted: order/store/product inconsistency should be treated as a concrete `unhandled_data_quality_or_record_inconsistency` example. The database check for order 8003 confirms the mismatch.
- Workshop suggestion revised: tool activity should influence review, but in local-only Raindrop mode it appears as metadata rather than full tool spans. For this homework, that is enough for hypothesis generation; Langfuse and the review UI remain the canonical annotation path.
- Workshop suggestion rejected: the mere presence of policy identifiers is not always `presentation_formatting_noise`. For support users asking policy-authority questions, policy names can be useful rather than noisy.
