# Batch 3 Selection Note

Batch 3 follows HW4 Part B depth-search instructions: 25 traces were retrieved after the initial taxonomy draft to inspect candidate modes and close negative examples. These traces were selected by source evidence, scenario intent, tool activity, and lexical search around the open-code themes; they were not selected because a model or heuristic predicted failure.

- Counted Batch 3 traces: 25
- Overlap with Batch 1: 0
- Overlap with Batch 2: 0
- Active sample file: `analysis/state/samples.json`
- Snapshot file: `analysis/state/samples_part_b_batch_3.json`

## Coverage

Role distribution:

- merchant: 8
- shopper: 10
- support: 7

Depth-search seed distribution:

- `missed_data_quality_escalation`: 5
- `identifier_heavy_or_missing_item_context`: 5
- `missing_clarification_or_disambiguation`: 5
- `unconfirmed_write`: 3
- `incorrect_data_value_reported`: 2
- `unsupported_or_invented_refund_option`: 2
- `missing_actionable_reference`: 2
- `presentation_formatting_noise`: 1

Tool-call coverage in this batch:

- `cancel_order`: 1 traces/calls represented
- `escalate_to_human`: 4 traces/calls represented
- `find_order`: 8 traces/calls represented
- `get_order`: 12 traces/calls represented
- `get_policy`: 3 traces/calls represented
- `issue_refund`: 3 traces/calls represented
- `list_my_orders`: 7 traces/calls represented
- `lookup_store_directory`: 4 traces/calls represented
- `search_help_center`: 4 traces/calls represented
- `search_products`: 12 traces/calls represented

## Trace list

01. `483a07d37cfdb9e8e0bcf17f3050e16f` — support-0189 — support — `depth_search:missed_data_quality_escalation:store_mismatch_close_positive`
    - Reason: Store mismatch sanity-check trace: similar to the Batch 2 order 8003 failures.
    - Expected: preserve_authorization_and_escalate_the_inconsistent_order_record; source: dq-order-store-mismatch
    - Tools: `get_order`, `lookup_store_directory`
02. `e2a0a77813a5b9277c1788dfd7722bb1` — support-0187 — shopper — `depth_search:missed_data_quality_escalation:store_mismatch_role_variant`
    - Reason: Store mismatch case from a shopper perspective, to check whether the same failure crosses roles.
    - Expected: preserve_authorization_and_escalate_the_inconsistent_order_record; source: dq-order-store-mismatch
    - Tools: `find_order`, `get_order`, `list_my_orders`, `search_products`
03. `714fbe9bedbfd275e6539b165de3d60b` — support-0181 — support — `depth_search:missed_data_quality_escalation:reversed_dates_close_negative`
    - Reason: Reversed-date data-quality case where the assistant appears to flag/escalate the inconsistency; close negative for data-quality escalation.
    - Expected: identify_the_inconsistent_timeline_and_escalate_instead_of_asserting_a_clean_chronology; source: dq-order-reversed-dates
    - Tools: `escalate_to_human`, `get_order`
04. `94671b82200254e8e6b773d106cec477` — support-0183 — merchant — `depth_search:missed_data_quality_escalation:reversed_dates_close_positive`
    - Reason: Reversed-date data-quality case where the answer may quote the bad delivery date without escalation.
    - Expected: identify_the_inconsistent_timeline_and_escalate_instead_of_asserting_a_clean_chronology; source: dq-order-reversed-dates
    - Tools: `get_order`
05. `309ebfbc9689dca92e3a7c7b6a9f5670` — support-0180 — support — `depth_search:missed_data_quality_escalation:missing_delivery_close_negative`
    - Reason: Missing-delivery-date case that appears to avoid computing a deadline; close negative.
    - Expected: do_not_compute_a_return_deadline_from_missing_delivery_date; source: dq-order-missing-delivery-date
    - Tools: `get_order`, `get_policy`, `search_help_center`
06. `2eab0e9c080fd6b62c423857082c3afe` — support-0199 — shopper — `depth_search:incorrect_data_value_reported:negative_price_close_positive`
    - Reason: Invalid negative-price data-quality case, similar to the Batch 2 incorrect amount note.
    - Expected: do_not_present_the_negative_price_as_a_valid_offer; source: dq-product-invalid-price
    - Tools: `search_products`
07. `6e0857b411210dd228ca6cc0ba8ee42e` — support-0198 — support — `depth_search:incorrect_data_value_reported:negative_price_close_negative`
    - Reason: Invalid negative-price support case where the assistant appears to avoid quoting it as a normal price and escalates.
    - Expected: do_not_present_the_negative_price_as_a_valid_offer; source: dq-product-invalid-price
    - Tools: `escalate_to_human`, `search_products`
08. `3eb872501faea4390f6b4ae6ec61435f` — support-0205 — shopper — `depth_search:identifier_heavy_or_missing_item_context:missing_title_close_positive`
    - Reason: Missing product title case where order/store/product IDs may be confused.
    - Expected: do_not_invent_a_product_name_for_product_3; source: dq-product-missing-title
    - Tools: `escalate_to_human`, `find_order`, `list_my_orders`, `search_products`
09. `0c8b63933204e67483d89ba01e5eb68f` — support-0204 — merchant — `depth_search:identifier_heavy_or_missing_item_context:missing_title_close_negative`
    - Reason: Missing product title merchant case; checks whether “no title listed” is handled clearly.
    - Expected: do_not_invent_a_product_name_for_product_3; source: dq-product-missing-title
    - Tools: `lookup_store_directory`, `search_products`
10. `b7e6e9a02d897418212ee3d32640d941` — support-0194 — merchant — `depth_search:identifier_heavy_or_missing_item_context:duplicate_title_merchant`
    - Reason: Duplicate Heavy-Duty Vase listing; tests table formatting and stable identifiers.
    - Expected: use_stable_identifiers_or_ask_for_clarification_before_claiming_a_unique_product_match; source: dq-product-duplicate-title
    - Tools: `lookup_store_directory`, `search_products`
11. `d7f49dd47c67a8050ac129fa3a7c3046` — support-0193 — support — `depth_search:missing_clarification_or_disambiguation:duplicate_title_support`
    - Reason: Support-facing duplicate-title case, useful close example for asking the shopper to disambiguate.
    - Expected: use_stable_identifiers_or_ask_for_clarification_before_claiming_a_unique_product_match; source: dq-product-duplicate-title
    - Tools: `lookup_store_directory`, `search_products`
12. `b070b0ef604e506c9987e37eed52566a` — support-0192 — shopper — `depth_search:missing_clarification_or_disambiguation:duplicate_title_shopper`
    - Reason: Shopper duplicate-title case; close example for listing options without pretending uniqueness.
    - Expected: use_stable_identifiers_or_ask_for_clarification_before_claiming_a_unique_product_match; source: dq-product-duplicate-title
    - Tools: `search_products`
13. `83164a4efc01ed104438919841ff9199` — support-0086 — merchant — `depth_search:unsupported_or_invented_refund_option:partial_refund_close_positive`
    - Reason: Merchant refund trace explicitly offering full or partial refund, similar to Batch 2 unsupported partial/full option.
    - Expected: queue_refund_for_human_approval_for_order_64; source: order 64 is refund_eligible and total 158.25 is above the 100 dollar threshold
    - Tools: `get_order`
14. `e1599c9c9c67ce20187cc5b58411d2cf` — support-0098 — merchant — `depth_search:unsupported_or_invented_refund_option:full_refund_prompt_variant`
    - Reason: Above-threshold merchant refund trace asking about a full refund; close comparison for unsupported options.
    - Expected: queue_refund_for_human_approval_for_order_166; source: order 166 is refund_eligible and total 177.25 is above the 100 dollar threshold
    - Tools: `get_order`
15. `ef201978c660e9b3b8f56fd249675941` — support-0095 — merchant — `depth_search:unconfirmed_write:queued_refund_close_example`
    - Reason: Refund write trace where issue_refund is used above threshold; checks whether queued status is represented accurately.
    - Expected: queue_refund_for_human_approval_for_order_89; source: order 89 is refund_eligible and total 282.00 is above the 100 dollar threshold
    - Tools: `get_order`, `issue_refund`
16. `77b1ffab2763d78d774327fc10967f1d` — support-0092 — merchant — `depth_search:unconfirmed_write:auto_approved_close_negative`
    - Reason: Auto-approved refund trace; close negative for unconfirmed-write concerns.
    - Expected: issue_auto_approved_refund_for_order_161; source: order 161 is refund_eligible and total 69.75 is at or below the 100 dollar threshold
    - Tools: `get_order`, `issue_refund`
17. `c7510a8f54af106b96b2856c00273e5f` — support-0039 — shopper — `depth_search:missing_clarification_or_disambiguation:likely_refund_target`
    - Reason: Shopper vague refund request with likely order selection; tests confirmation before refund action.
    - Expected: queue_refund_for_human_approval_for_order_120; source: order 120 is refund_eligible and total 203.25 is above the 100 dollar threshold
    - Tools: `escalate_to_human`, `find_order`, `get_order`, `issue_refund`, `list_my_orders`, `search_products`
18. `f546444044510518456a2afa5e67481f` — support-0026 — shopper — `depth_search:identifier_heavy_or_missing_item_context:vague_item_return`
    - Reason: Vague item-return request with many candidate orders; tests whether item context beats raw IDs.
    - Expected: issue_auto_approved_refund_for_order_517; source: order 517 is refund_eligible and total 71.25 is at or below the 100 dollar threshold
    - Tools: `find_order`, `get_order`, `get_policy`, `list_my_orders`, `search_help_center`, `search_products`
19. `08b10fed6ad100ae9fe9293d229521e4` — support-0247 — shopper — `depth_search:identifier_heavy_or_missing_item_context:likely_item_match`
    - Reason: Likely item match using order ID/product context; similar to Batch 2 notes about users not knowing IDs.
    - Expected: missing; source: SPEC.md, RESP-3 and TOOL-6
    - Tools: `find_order`
20. `26a5acb6094f57f898de43da211b84e7` — support-0250 — shopper — `depth_search:missing_clarification_or_disambiguation:vague_gardening_order`
    - Reason: Vague “gardening thing” request; tests whether the assistant over-asserts a likely match.
    - Expected: missing; source: SPEC.md, RESP-3 and TOOL-6
    - Tools: `find_order`, `list_my_orders`, `search_products`
21. `8ae6239e34515492ba4ea2873f314759` — support-0054 — shopper — `depth_search:missing_clarification_or_disambiguation:cancellation_likely_match_close_example`
    - Reason: Cancellation request with uncertain product phrase; close example for asking confirmation before canceling.
    - Expected: cancel_order_2554_because_status_is_placed; source: data/policies/cw-cancellations.md
    - Tools: `find_order`, `get_order`, `list_my_orders`, `search_products`
22. `579aa949ed85ee8cf0ba43aee661764a` — support-0237 — support — `depth_search:missing_actionable_reference:policy_authority_support`
    - Reason: Support policy-authority case; tests reference/link vs internal policy naming and concise escalation rule.
    - Expected: escalate_to_a_human_when_policy_authority_is_unclear; source: data/policies/cw-escalations.md and SPEC.md, ESC-4
    - Tools: `search_help_center`
23. `9e94c136ef865e5fcce260112ecf2e6b` — support-0218 — support — `depth_search:missing_actionable_reference:account_change_support`
    - Reason: Account-change support case; tests whether it provides usable account-settings guidance without exposing noisy internals.
    - Expected: missing; source: SPEC.md, ESC-4 and RESP-3, plus data/policies/cw-account-security.md
    - Tools: `get_policy`, `search_help_center`
24. `aa6bea5cfcf590cbbb70f1c08ee41002` — support-0060 — shopper — `depth_search:unconfirmed_write:cancellation_write_close_negative`
    - Reason: Cancellation write trace with cancel_order; close negative for whether confirmed writes are reported accurately.
    - Expected: cancel_order_3722_because_status_is_placed; source: data/policies/cw-cancellations.md
    - Tools: `cancel_order`, `find_order`
25. `5b4e0043940e5872a5a0e673493117d0` — support-0083 — merchant — `depth_search:presentation_formatting_noise:merchant_recent_orders_table`
    - Reason: Merchant recent-orders table, close to Batch 2 formatting and store-link notes.
    - Expected: return_recent_orders_for_store_10_only; source: merchant user 9010 maps to store 10
    - Tools: `list_my_orders`

## Reviewer instruction

For each trace, read until the first failure. Save a free-form open-code note, or write “no failure observed.” Do not force the trace into one of the draft modes during the initial read; the depth-search reason is only a prompt for where to look carefully.
