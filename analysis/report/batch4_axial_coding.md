# Batch 4 Axial Coding and Saturation Check

This draft groups the human open-code annotations from HW4 Part B Batch 4. Batch 4 was the final post-taxonomy uniform sample used to check whether new modes continued to appear. The grouping is annotation-level: each saved note appears exactly once under a candidate mode or held-out bucket.

- Reviewed counted traces: 15
- Saved Batch 4 annotation notes: 52
- Batch type: post-taxonomy uniform random saturation check
- New candidate modes observed: 0
- Saturation read: the existing taxonomy covered the Batch 4 notes; no genuinely new failure family appeared.

## Saturation result

Batch 4 did not produce a new mode. It reinforced the modes already visible by Batch 3, especially formatting noise, missing actionable references, identifier-heavy answers, unnecessary detail overload, unsupported refund options, unclear human-review follow-up, confusing/contradictory answers, clarification failures, and unhandled data-quality or record inconsistency. This is a good sign that the taxonomy is stabilizing enough to move from open/axial coding toward final structured labeling.

## Final taxonomy implication

The main Batch 3 proposals should be retained: broaden `missed_data_quality_escalation` into `unhandled_data_quality_or_record_inconsistency`, and keep `missing_human_review_followup_path` separate from generic `missing_actionable_reference`. Batch 4 found fresh examples of both, including unclear human follow-up and missing shipping/delivery evidence.

## `presentation_formatting_noise`

Definition: The response presentation makes the answer harder to read through visible Markdown markers or hard-to-scan table formatting.

Boundary: Include visible ** markers and table-display complaints. Exclude policy-name preferences unless the concern is visual readability.

Saturation result: Confirmed again in the post-taxonomy uniform sample.

Supporting evidence: 8 notes across 7 traces

- Note 01, `a71488354ca1baeaf1b21922ea7e2b84` (support-0082, merchant): bad formatting - need better table display Quote: “| Order ID | Ordered | Status | Product ID | Qty | Total | Shipped | Delivered | Refund eligible |”
- Note 15, `d0bb277ed8f0e0b6512dc65c9abfc768` (support-0178, merchant): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “*”
- Note 19, `ea6e3000625f8101f7cb47593fd10c4b` (support-0015, shopper): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “*”
- Note 23, `8349f54d768a0267670b5d843dee58f9` (support-0084, merchant): bad formatting - need better table display Quote: “Order ID | Ordered | Status | Total | Shipped | Delivered | Refund eligible |”
- Note 25, `8349f54d768a0267670b5d843dee58f9` (support-0084, merchant): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “*”
- Note 34, `b06db19fb5a824cebca88263550154d1` (support-0089, merchant): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “**”
- Note 48, `1794eb35c6229c24e95219e1f0aec773` (support-0155, support): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “*”
- Note 52, `80ef7b26d661134e6da1f0eaedfdeef6` (support-0216, support): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “**”

## `identifier_heavy_or_missing_item_context`

Definition: The answer relies on internal IDs or omits user-recognizable item/order context, so the user cannot tell which product, order, refund, or cancellation is being discussed.

Boundary: Include missing product names, raw order IDs, refund fields presented without user value, or requests for item-specific link/picture/name context. Exclude generic self-service links.

Saturation result: Confirmed again; this is one of the strongest recurring modes across the final sample.

Supporting evidence: 9 notes across 5 traces

- Note 02, `a71488354ca1baeaf1b21922ea7e2b84` (support-0082, merchant): missing product name in the order summary Quote: “7936 |”
- Note 24, `8349f54d768a0267670b5d843dee58f9` (support-0084, merchant): product name is missing in the data Quote: “| 6213”
- Note 31, `7a39f43b0cd190cc28686900523affb5` (support-0065, shopper): order id is unnecessary detail Quote: “**Order #7**”
- Note 36, `800fec280f9b74181b123b1d06a2f78d` (support-0068, shopper): order id is unnecessary detail Quote: “**Order #11*”
- Note 37, `800fec280f9b74181b123b1d06a2f78d` (support-0068, shopper): refund data is not needed Quote: “**Refund eligible:** No”
- Note 39, `3e97db1ec16ea5d347fca6da752c388b` (support-0064, shopper): order id is unnecessary detail - and not helpful\ Quote: “**order #1145** in more detail.”
- Note 41, `3e97db1ec16ea5d347fca6da752c388b` (support-0064, shopper): order id is unnecessary detail Quote: “**Order #6**”
- Note 43, `3e97db1ec16ea5d347fca6da752c388b` (support-0064, shopper): refund data is not needed Quote: “- **Return/refund eligible:** Yes”
- Note 44, `3e97db1ec16ea5d347fca6da752c388b` (support-0064, shopper): product name is missing in the data Quote: “- **Delivered:** June 22, 2026”

## `missing_actionable_reference`

Definition: The reply does not give a concrete link, page, account path, order page, store page, or policy/help-center reference the user can follow.

Boundary: Include explicit requests for merchant store links, account settings, recent-order links, order links, and policy/help-center links. Exclude internal policy-name complaints without a requested reference.

Saturation result: Confirmed again with merchant, shopper, and support examples.

Supporting evidence: 13 notes across 12 traces

- Note 03, `a71488354ca1baeaf1b21922ea7e2b84` (support-0082, merchant): add a link for the merchant where they can see their store details Quote: “Here are Golden Hour Coffee’s 20 most recent orders:”
- Note 06, `e72f2e0f927f0d0f4bed77be7d0fa900` (support-0099, merchant): add a policy / help center article link the merchant can refer to for refund and return conditions Quote: “Policy”
- Note 14, `ad5fb2d370221bd63571d0a0e082eb80` (support-0141, support): add policy link for the support user to refer back to the shopper Quote: “Policy: **cw-refunds**.”
- Note 16, `d0bb277ed8f0e0b6512dc65c9abfc768` (support-0178, merchant): add a link for the policy line for the support to read Quote: “cw-returns”
- Note 20, `ea6e3000625f8101f7cb47593fd10c4b` (support-0015, shopper): send user to their recent order link if they want to self-validate. Quote: “an order that looks related”
- Note 26, `8349f54d768a0267670b5d843dee58f9` (support-0084, merchant): send the merchant to an account setting link where they can see their recent store movements. Quote: “Here are the latest orders”
- Note 29, `d91a9655062d3a49c918bd2866005ebc` (support-0147, support): add a link for the policy line for the support to read Quote: “Policy”
- Note 33, `7a39f43b0cd190cc28686900523affb5` (support-0065, shopper): send user to their recent order link if they want to self-validate. Quote: “I found a likely match:”
- Note 38, `800fec280f9b74181b123b1d06a2f78d` (support-0068, shopper): send a direct link to the order as additional support - supporting evidence is useful to clearify. Quote: “It’s not showing near the top because it’s older than your more recent 2026 orders.”
- Note 40, `3e97db1ec16ea5d347fca6da752c388b` (support-0064, shopper): send user to their recent order link if they want to self-validate. Quote: “Cartwheel orders:”
- Note 47, `1794eb35c6229c24e95219e1f0aec773` (support-0155, support): add a policy / help center article link the support user can refer to Quote: “Policy”
- Note 49, `80ef7b26d661134e6da1f0eaedfdeef6` (support-0216, support): add a link for the user which can help them to find their account details on their own. Quote: “account settings”
- Note 51, `80ef7b26d661134e6da1f0eaedfdeef6` (support-0216, support): add a policy / help center article link the support user can refer to Quote: “Policy:”

## `unnecessary_detail_overload`

Definition: The reply includes extra calculations, policy mechanics, status facts, or order data that distract from the current ask.

Boundary: Include proactive calculations, extra policy detail, irrelevant order lists, repeated status facts, and unnecessary refund/shipping fields. Exclude identifier-heavy context where the central issue is recognizability.

Saturation result: Confirmed again; no split needed beyond the existing identifier-context bucket.

Supporting evidence: 8 notes across 6 traces

- Note 04, `e72f2e0f927f0d0f4bed77be7d0fa900` (support-0099, merchant): too much information Quote: “Cartwheel policy says refunds over $100 are queued for human review before any money moves, and approved refunds go back to the buyer’s original payment method in **5–10 business days**”
- Note 07, `e72f2e0f927f0d0f4bed77be7d0fa900` (support-0099, merchant): too much data Quote: “a full refund would be **above $100**, so it won’t process automatically.”
- Note 10, `b2fde1b344df41182ff60e87ff284c3d` (support-0229, merchant): unnecessary data and confusing for user Quote: “I did calculate your store’s refund rate from the recent orders available to me:”
- Note 11, `b2fde1b344df41182ff60e87ff284c3d` (support-0229, merchant): too much calculation and explanation - these detaiuls can be given per offer from the agent. Not proactively. Quote: “If you exclude cancelled orders, your refund rate is:”
- Note 13, `ad5fb2d370221bd63571d0a0e082eb80` (support-0141, support): repetitive information which causes overload Quote: “Order 64 is refund-eligible. It was delivered, total is **$158.25**, and the refund eligibility check passed.  Because the amount is **over $100**, the refund should **not be auto-paid immediately**. It should be submitted for refund and then **queued for human support review before any money moves**.”
- Note 21, `ea6e3000625f8101f7cb47593fd10c4b` (support-0015, shopper): too much information which are irrelevant and unnecessary Quote: “I didn’t find a recent order matching “pole set.” Your most recent orders are currently **shipped but not marked delivered yet**: orders **#3099** and **#6280**.”
- Note 27, `8349f54d768a0267670b5d843dee58f9` (support-0084, merchant): unnecessary data Quote: “I found **20 recent orders** total.”
- Note 30, `7a39f43b0cd190cc28686900523affb5` (support-0065, shopper): too much information - unnecessary details are not needed. Quote: “f you meant **March 2026** instead, I see two March orders, but neither appears to be a puzzle from the order details”

## `unsupported_or_invented_refund_option`

Definition: The reply presents refund choices, especially full versus partial refund, as available when the reviewed policy/tool evidence does not define that option.

Boundary: Include invented refund options. Exclude true tool-confirmed status details.

Saturation result: Confirmed again in the uniform sample; this is no longer only a depth-search artifact.

Supporting evidence: 1 notes across 1 traces

- Note 09, `e72f2e0f927f0d0f4bed77be7d0fa900` (support-0099, merchant): inventing rules - no partial vs full refund rules Quote: “full **$231.50** or a partial amount”

## `missing_human_review_followup_path`

Definition: The reply says human review/follow-up is needed but does not specify who follows up, where the case can be tracked, or what the user/merchant should expect next.

Boundary: Include unclear human follow-up statements and missing approval/confirmation paths. Exclude generic missing links unless the missing link specifically concerns a human review or follow-up path.

Saturation result: Confirmed again; this should remain separate from generic missing references for now.

Supporting evidence: 2 notes across 2 traces

- Note 17, `d0bb277ed8f0e0b6512dc65c9abfc768` (support-0178, merchant): missing information about the follow up. Who will follow up with whom and where it will be followed up is missing. Quote: “A human will follow up within **24 hours**.”
- Note 22, `ea6e3000625f8101f7cb47593fd10c4b` (support-0015, shopper): follow up is needed for user to approve Quote: “order **#16**.”

## `confusing_or_contradictory_answer`

Definition: The reply gives a conflicting or unclear interpretation of status, policy, authorization, or matching evidence.

Boundary: Include contradictions, wrong routing despite closed authorization, unclear refund/human-review framing, and invented product matches that increase confusion. Exclude simple missing self-service links.

Saturation result: Confirmed again; several examples overlap conceptually with overload but the reviewer notes emphasize contradiction/confusion.

Supporting evidence: 2 notes across 2 traces

- Note 08, `e72f2e0f927f0d0f4bed77be7d0fa900` (support-0099, merchant): confusing information - the refund amount is over 100$ by defaullt already. Unclear and contradicting message Quote: “. I can submit it; if it’s over $100, it will be queued for human approval.”
- Note 12, `b2fde1b344df41182ff60e87ff284c3d` (support-0229, merchant): contradicting - authorization is closed by default. Incorrect routing of the help. Quote: “I opened a human support ticket to review whether approved platform-wide aggregate benchmarking can be shared: ticket #163. A human will follow up within about 24 hours.”

## `missing_clarification_or_disambiguation`

Definition: The reply proceeds with a likely match or action when it should first ask for confirmation or clarify the intended product/order.

Boundary: Include likely-match and approval-needed notes. Exclude wrong data-quality handling and identifier-heavy display problems.

Saturation result: Confirmed, but with fewer examples than in the depth batch.

Supporting evidence: 1 notes across 1 traces

- Note 45, `3e97db1ec16ea5d347fca6da752c388b` (support-0064, shopper): inventing a product match and creating more confusion. Quote: “found a likely match in you”

## `unhandled_data_quality_or_record_inconsistency`

Definition: The reply treats missing or inconsistent source data as normal instead of flagging the problem or routing it for investigation.

Boundary: Include missing delivery/shipping data or inconsistent return-deadline framing when the source data cannot support the claim.

Saturation result: Confirmed in the uniform sample, supporting the broader Batch 3 name.

Supporting evidence: 3 notes across 3 traces

- Note 18, `d0bb277ed8f0e0b6512dc65c9abfc768` (support-0178, merchant): confusing and contradicting - delivery date is missing but we seem to still offer a date. Vague language is being used. Quote: “Cartwheel’s return window is **30 days from the delivery date, not the purchase date*”
- Note 32, `7a39f43b0cd190cc28686900523affb5` (support-0065, shopper): shipping data is not available Quote: “**Total:** $168.00”
- Note 42, `3e97db1ec16ea5d347fca6da752c388b` (support-0064, shopper): no shipping data visible Quote: “**Return/refund eligible:** No”

## Held-out notes, not currently candidate failure modes

### `policy_name_preference_without_reference_request`

Preference to avoid exposing internal policy names. Held out unless paired with a request for a usable reference.

Evidence kept aside: 4 notes across 4 traces

- Note 05, `e72f2e0f927f0d0f4bed77be7d0fa900` (support-0099, merchant): no need to call out specific policy name Quote: “cw-refunds*”
- Note 28, `d91a9655062d3a49c918bd2866005ebc` (support-0147, support): policy names are not needed to be called out directly Quote: “**cw-refunds**”
- Note 46, `1794eb35c6229c24e95219e1f0aec773` (support-0155, support): no need to call out specific policy name Quote: “cw-disputes”
- Note 50, `80ef7b26d661134e6da1f0eaedfdeef6` (support-0216, support): no need to call out specific policy name Quote: “cw-account-security”

### `no_failure_observed`

Reviewed trace where the saved note says no failure/no failures.

Evidence kept aside: 1 notes across 1 traces

- Note 35, `2a31e4ce7a14e2b600e7baea85676600` (support-0124, merchant): no failures Quote: “duct name.”

## Next step

Move to final structured labeling: define the final binary mode list and label every reviewed trace with present/absent for each final mode. The open-code notes remain as history; the structured pass creates the labeling matrix needed for prevalence and later judge development.
