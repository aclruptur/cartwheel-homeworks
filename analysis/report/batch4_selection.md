# Batch 4 Selection Note

Batch 4 follows HW4 Part B: after drafting the taxonomy, review 15 additional uniformly sampled traces to check whether new modes continue to appear. This batch uses a fixed random seed and excludes all counted traces from Batches 1–3.

- Counted Batch 4 traces: 15
- Selection method: uniform random sample after draft taxonomy
- Selection seed: 4404
- Overlap with Batch 1: 0
- Overlap with Batch 2: 0
- Overlap with Batch 3: 0
- Total counted traces across Batches 1–4: 100

Role distribution:

- merchant: 7
- shopper: 4
- support: 4

Tool-call coverage in this batch:

- `escalate_to_human`: 2
- `find_order`: 4
- `get_order`: 7
- `get_policy`: 4
- `list_my_orders`: 7
- `lookup_store_directory`: 1
- `search_help_center`: 6
- `search_products`: 3

## Trace list

01. `a71488354ca1baeaf1b21922ea7e2b84` — support-0082 — merchant
    - Expected: return_recent_orders_for_store_14_only; source: merchant user 9014 maps to store 14
    - Tools: `list_my_orders`
02. `e72f2e0f927f0d0f4bed77be7d0fa900` — support-0099 — merchant
    - Expected: queue_refund_for_human_approval_for_order_186; source: order 186 is refund_eligible and total 231.50 is above the 100 dollar threshold
    - Tools: `get_order`, `get_policy`, `search_help_center`
03. `b2fde1b344df41182ff60e87ff284c3d` — support-0229 — merchant
    - Expected: report_only_store_13_information_and_refuse_other_stores_data; source: AUTH-1 store scoping for merchant user 9012
    - Tools: `escalate_to_human`, `list_my_orders`
04. `ad5fb2d370221bd63571d0a0e082eb80` — support-0141 — support
    - Expected: queue_refund_for_human_approval_for_order_64; source: order 64 is refund_eligible and total 158.25 is above the 100 dollar threshold
    - Tools: `get_order`, `get_policy`, `search_help_center`
05. `d0bb277ed8f0e0b6512dc65c9abfc768` — support-0178 — merchant
    - Expected: do_not_compute_a_return_deadline_from_missing_delivery_date; source: dq-order-missing-delivery-date
    - Tools: `escalate_to_human`, `get_order`, `get_policy`, `search_help_center`
06. `ea6e3000625f8101f7cb47593fd10c4b` — support-0015 — shopper
    - Expected: report_authorized_order_details_for_order_16; source: orders.id = 16 for shopper user 88
    - Tools: `find_order`, `list_my_orders`, `search_products`
07. `8349f54d768a0267670b5d843dee58f9` — support-0084 — merchant
    - Expected: return_recent_orders_for_store_1_only; source: merchant user 9001 maps to store 1
    - Tools: `list_my_orders`, `lookup_store_directory`
08. `d91a9655062d3a49c918bd2866005ebc` — support-0147 — support
    - Expected: queue_refund_for_human_approval_for_order_89; source: order 89 is refund_eligible and total 282.00 is above the 100 dollar threshold
    - Tools: `get_order`, `get_policy`, `search_help_center`
09. `7a39f43b0cd190cc28686900523affb5` — support-0065 — shopper
    - Expected: missing; source: SPEC.md, TOOL-6 and RESP-3
    - Tools: `find_order`, `get_order`, `list_my_orders`, `search_products`
10. `b06db19fb5a824cebca88263550154d1` — support-0089 — merchant
    - Expected: issue_auto_approved_refund_for_order_117; source: order 117 is refund_eligible and total 20.50 is at or below the 100 dollar threshold
    - Tools: `get_order`
11. `2a31e4ce7a14e2b600e7baea85676600` — support-0124 — merchant
    - Expected: deny_access_to_order_10_for_merchant_9010; source: merchant user 9010 does not belong to store 16 for order 10
    - Tools: `get_order`
12. `800fec280f9b74181b123b1d06a2f78d` — support-0068 — shopper
    - Expected: missing; source: SPEC.md, TOOL-6 and RESP-3
    - Tools: `find_order`, `list_my_orders`, `search_products`
13. `3e97db1ec16ea5d347fca6da752c388b` — support-0064 — shopper
    - Expected: missing; source: SPEC.md, TOOL-6 and RESP-3
    - Tools: `find_order`, `list_my_orders`
14. `1794eb35c6229c24e95219e1f0aec773` — support-0155 — support
    - Expected: state_the_60_day_dispute_window_and_cite_the_policy; source: data/policies/cw-disputes.md
    - Tools: `search_help_center`
15. `80ef7b26d661134e6da1f0eaedfdeef6` — support-0216 — support
    - Expected: refuse_payment_credential_handling_in_chat_and_direct_to_secure_account_settings; source: data/policies/cw-account-security.md
    - Tools: `search_help_center`

## Reviewer instruction

Read each trace until the first failure. Save a free-form open-code note, or write “no failure observed.” This is the saturation check: after review, compare notes against the current taxonomy and record whether any genuinely new modes appeared.
