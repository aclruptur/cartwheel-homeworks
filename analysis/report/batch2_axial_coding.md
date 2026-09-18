# Batch 2 Axial Coding Draft

This draft groups the human open-code annotations from HW4 Part B Batch 2. Batch 2 was selected by the product dimension `user_role` before reviewing outcomes, with 10 merchant, 10 shopper, and 10 support traces. The grouping is annotation-level: each note appears under exactly one candidate mode or held-out bucket.

- Reviewed counted traces: 30
- Saved Batch 2 annotation notes: 81
- Product dimension: `user_role`
- Distribution: merchant 10, shopper 10, support 10
- Candidate modes proposed from this batch: 9
- Agent-added labels: none; these are candidate groupings of human notes

## Relationship to Batch 1

Batch 2 confirms several Batch 1 candidates: presentation formatting noise, missing actionable references, unnecessary detail overload, missing clarification/disambiguation, and confusing or contradictory answers. It also suggests three narrower candidates: `identifier_heavy_or_missing_item_context`, `unsupported_or_invented_refund_option`, and `missed_data_quality_escalation`. Those should stay provisional until Batch 3 depth searches find close positives and close negatives.

## Boundary rules refined after Batch 2

- `missing_actionable_reference`: the answer lacks a concrete link/path/article. A note saying “do not show the policy name” is not enough by itself.
- `unnecessary_detail_overload`: the answer gives extra facts or policy exposition beyond the ask.
- `identifier_heavy_or_missing_item_context`: the answer uses IDs or omits item names/context, so the user cannot recognize the thing being discussed.
- `missing_clarification_or_disambiguation`: the answer should ask a clarifying question or confirm an ambiguous target before proceeding.
- `confusing_or_contradictory_answer`: the text itself leaves the user with an unclear or conflicting interpretation, even apart from missing links or excess detail.
- `missed_data_quality_escalation`: the source data is inconsistent and the agent wrongly normalizes or denies that inconsistency.

## `presentation_formatting_noise`

Definition: The response presentation makes the answer harder to read through visible Markdown markers or hard-to-scan table/list formatting.

Boundary: Include visible ** markers and table display complaints. Exclude policy-name preferences and content-level overload unless the reviewer tied the issue to readability.

Requirement source: SPEC.md RESP-5: direct, respectful, useful language. This remains partly a UI/product presentation expectation because the reviewer expects bold styling rather than raw Markdown marks.

Supporting evidence: 16 notes across 15 traces

- Note 01, `392712f2cb2999c90b6f90c06d69b360` (support-0071, merchant): bad formatting - need better table display Quote: “Order ID | Product ID | Qty | Total | Status | Ordered | Shipped | Delivered | Refund eligible”
- Note 04, `202139c415cd79aa65aff53cb6814c9a` (support-0077, merchant): bad formatting - need better table display Quote: “| Order ID | Product ID | Qty | Total | Status | Ordered | Shipped | Delivered |”
- Note 08, `d7ee1d31861ebeb94ab86f38f535245a` (support-0080, merchant): bad formatting - need better table display Quote: “| Order ID | Ordered | Status | Product ID | Qty | Total | Shipped | Delivered |”
- Note 22, `6b0f8edadbf3c111c80f46baa8896fd2` (support-0200, merchant): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “**”
- Note 25, `722a3e707c0ad7ef7cd3c749097a1207` (support-0002, shopper): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “**”
- Note 32, `5ae9d430b85f988b4a42a382374e8fec` (support-0005, shopper): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “**,”
- Note 37, `f6cb5d8760f9c08603caf657f9531bd7` (support-0016, shopper): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “**”
- Note 42, `7a288dcc0ebdd8202bc6625ffc899a1f` (support-0043, shopper): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “**”
- Note 48, `e2c653d360400c4134d7770bd5aaaac8` (support-0044, shopper): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “**”
- Note 56, `bbccf32f3db0f084963242d726d83fe6` (support-0195, shopper): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “**”
- Note 63, `db755472a70eadcd4752cd008d72b302` (support-0154, support): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “**”
- Note 69, `e3d93b15ba9f920783188e4cea85b5ca` (support-0159, support): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “w-escalation”
- Note 74, `ac7b075ca1133a019dfbc48f955c9d03` (support-0164, support): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “**”
- Note 75, `ac7b075ca1133a019dfbc48f955c9d03` (support-0164, support): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “*”
- Note 76, `f99502a3130847a3f6548b8565534922` (support-0168, support): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “*”
- Note 81, `5023b152407f12c113be0006e2ca0315` (support-0240, support): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “*”

## `missing_actionable_reference`

Definition: The reply gives guidance but omits a concrete place the user can go next, such as a merchant store page, order-history page, refund tracker, or support-facing policy/help article.

Boundary: Include notes that explicitly ask for a link, path, or article. Exclude notes that only say not to show the internal policy name; those are held out unless they also request a usable reference.

Requirement source: SPEC.md RESP-5: useful answers; likely needs a product/UI requirement for self-service and support-reference links.

Supporting evidence: 13 notes across 13 traces

- Note 02, `392712f2cb2999c90b6f90c06d69b360` (support-0071, merchant): add a link for the merchant where they can see their store details Quote: “Little Fox Toys orders:”
- Note 05, `202139c415cd79aa65aff53cb6814c9a` (support-0077, merchant): add a link for the merchant where they can see their store details Quote: “Paper Lantern Press orders:”
- Note 07, `d7ee1d31861ebeb94ab86f38f535245a` (support-0080, merchant): add a link for the merchant where they can see their store details Quote: “Bright Socket Electronics orders”
- Note 16, `3c151d9acac3006bcc342650fa357f33` (support-0123, merchant): add a link for the merchant where they can see their store details Quote: “Order 9 for Trailhead Supply:”
- Note 18, `241fd269bffd30d6bb09763f41c5b945` (support-0191, merchant): add a link for the merchant where they can see their store details Quote: “products in your store, Blue Heron Ceramics”
- Note 26, `722a3e707c0ad7ef7cd3c749097a1207` (support-0002, shopper): add a link for the user which can help them to find their orders on their own account. Quote: “already been delivered”
- Note 29, `5ae9d430b85f988b4a42a382374e8fec` (support-0005, shopper): send user to their recent order link if they want to self-validate. Quote: “meant the item bough”
- Note 36, `f6cb5d8760f9c08603caf657f9531bd7` (support-0016, shopper): send user to their recent order link if they want to self-validate. Quote: “send me the”
- Note 39, `d3ecfb30a645f96ce5c354ae2b763dd3` (support-0025, shopper): send them a link where they can track progress of their refund. Quote: “5–10 business days.”
- Note 49, `e2c653d360400c4134d7770bd5aaaac8` (support-0044, shopper): send user to their recent order link if they want to self-validate. Quote: “from **Copperline Tools**, order **#219**”
- Note 52, `fa6bf0e0a85f6de2bb94eb2a1b7106e8` (support-0045, shopper): send user to their recent order link if they want to self-validate. Quote: “If yes, also tell me the reason for the refund”
- Note 68, `e3d93b15ba9f920783188e4cea85b5ca` (support-0159, support): add a policy / help center article link the support user can refer to Quote: “See **cw-account-security*”
- Note 79, `5023b152407f12c113be0006e2ca0315` (support-0240, support): add a policy / help center article link the support user can refer to Quote: “Policy”

## `unnecessary_detail_overload`

Definition: The reply includes extra policy/order/refund/security detail that distracts from the current ask or answers beyond what the user needs at that moment.

Boundary: Include policy exposition, irrelevant facts, extra ticket/refund details, and overexplaining when the ask is narrower. Exclude ID-heavy answers where the main problem is that the user cannot recognize the item; those are grouped separately.

Requirement source: SPEC.md RESP-5: clear, useful, concise responses.

Supporting evidence: 14 notes across 8 traces

- Note 11, `905a5619a856cb3de0c8b5fe1378cea2` (support-0104, merchant): unnecessary data and information Quote: “Unopened items cannot be charged a restocking fee. See `store-cascade-audio-policy` and `cw-restocking-fees`.”
- Note 12, `905a5619a856cb3de0c8b5fe1378cea2` (support-0104, merchant): too much information Quote: “because Cascade Audio’s store policy allows it and Cartwheel permits restocking fees on opened items when disclosed”
- Note 14, `905a5619a856cb3de0c8b5fe1378cea2` (support-0104, merchant): too much information Quote: “For order 22 specifically: it was delivered on May 20, 2026, and the system shows it is not refund-eligible. Cascade Audio’s return window is 30 days from delivery (`store-cascade-audio-policy`). So if this is a standard return request, it’s outside the return window.”
- Note 34, `f6cb5d8760f9c08603caf657f9531bd7` (support-0016, shopper): unnecessary information - user is asking for phone charger Quote: “ut your most recent order is”
- Note 44, `7a288dcc0ebdd8202bc6625ffc899a1f` (support-0043, shopper): too much information - real ask is about returning the product they bought and get help, not policiy specific details. Quote: “not purchase date (**cw-returns**)”
- Note 45, `7a288dcc0ebdd8202bc6625ffc899a1f` (support-0043, shopper): too much information about policy details - use policy link instead. Quote: “but because the order total is **$267.75**, it needs human review before a return/refund can be completed”
- Note 46, `7a288dcc0ebdd8202bc6625ffc899a1f` (support-0043, shopper): support ticket id is not helpful for the user. too much data Quote: “I’ve opened a support ticket for you: **#152**”
- Note 50, `e2c653d360400c4134d7770bd5aaaac8` (support-0044, shopper): too much informatuon about policy details. Quote: “Cartwheel’s return policy says items can be returned within **30 days of delivery** and must be in the condition described in the store listing (**cw-returns**). Your order is currently showing as **refund-eligible**, but because the refund amount is **$116**, it needs human review.”
- Note 53, `fa6bf0e0a85f6de2bb94eb2a1b7106e8` (support-0045, shopper): too much information Quote: “- Order #245 from Petal & Stem   - Total: $212.50   - Status: delivered   - Delivered: 2026-06-01   - Refund eligible: yes”
- Note 64, `db755472a70eadcd4752cd008d72b302` (support-0154, support): internal policy documents and names do not need to be exposed. too much and irrelevant information Quote: “Policy: **cw-disputes”
- Note 65, `db755472a70eadcd4752cd008d72b302` (support-0154, support): unnecessary data - user is only asking for the duration of post-delivery dispute Quote: “Disputes are handled by a human support agent”
- Note 66, `e3d93b15ba9f920783188e4cea85b5ca` (support-0159, support): unnecessary data Quote: “we won’t ask for full card numbers”
- Note 70, `e3d93b15ba9f920783188e4cea85b5ca` (support-0159, support): too much information - we do not need to pass internal policy names there as they are not helpful. Quote: “See *”
- Note 80, `5023b152407f12c113be0006e2ca0315` (support-0240, support): no need to add this extra detail Quote: “A human responds within 24 hours”

## `missing_clarification_or_disambiguation`

Definition: The reply proceeds or answers without resolving ambiguity about timeframe, product/order identity, user intent, or support context.

Boundary: Include unclear timeframe, likely-match uncertainty, missing confirmation before refund/cancel, and support-context assumptions. Exclude missing product names/order-context when the answer already chose an item but presented it poorly; that is identifier-heavy context.

Requirement source: SPEC.md RESP-3: state missing or inconsistent information rather than inventing values; RESP-5: useful next-step guidance.

Supporting evidence: 11 notes across 10 traces

- Note 03, `202139c415cd79aa65aff53cb6814c9a` (support-0077, merchant): ambiguity - how recent is that? the agent should say which dates it decided to cover for the merchant. Quote: “your recent”
- Note 06, `d7ee1d31861ebeb94ab86f38f535245a` (support-0080, merchant): ambiguity - how recent is that? the agent should say which dates it decided to cover for the merchant. Quote: “are your recent”
- Note 19, `241fd269bffd30d6bb09763f41c5b945` (support-0191, merchant): add a follow up to the merchant which product id they need further informatuon on. Lacking clarity that can be made by the agent Quote: “found these “Heavy-Duty Vase””
- Note 31, `5ae9d430b85f988b4a42a382374e8fec` (support-0005, shopper): ambiguous wording - likely Quote: “it’s likely”
- Note 33, `5ae9d430b85f988b4a42a382374e8fec` (support-0005, shopper): ambiguous language - orders close to but gives exact dates below Quote: “close”
- Note 40, `d3ecfb30a645f96ce5c354ae2b763dd3` (support-0025, shopper): confirm with the user first as they do not seem to remember the product they want a refund for. Quote: “found the May 30”
- Note 47, `e2c653d360400c4134d7770bd5aaaac8` (support-0044, shopper): agent using ambiguous language - creates confusion Quote: “what looks like the order:”
- Note 54, `fa6bf0e0a85f6de2bb94eb2a1b7106e8` (support-0045, shopper): ask user for clarification and approval before jumping directly into the refund - maybe the user is remembering a different product they bought from somewhere else. Quote: “recent garden-related order that may be it:”
- Note 55, `b33faa6800728f347de5d4136d8067bc` (support-0057, shopper): ask user for approval about the product they want to cancel first. which bag is the user talking about is not clear. Quote: “anceled order #3416”
- Note 67, `e3d93b15ba9f920783188e4cea85b5ca` (support-0159, support): ambiguous subject, language - your vs customer's Quote: “your account settings”
- Note 72, `fe06cd1306890e4414a291780b343080` (support-0163, support): agent making assumptions that it's AI Agent support. SHould have clarified with the user first. Quote: “It should be escalated to a human support agent.”

## `identifier_heavy_or_missing_item_context`

Definition: The answer relies on internal identifiers or omits user-recognizable item context, making it hard for the shopper, merchant, or support agent to tell which order/product/refund is being discussed.

Boundary: Include order IDs, product IDs, refund IDs, or missing product names when the reviewer says those identifiers are not useful or need user-friendly context. Exclude ordinary extra detail where the user can still understand the target.

Requirement source: SPEC.md RESP-5; this may need a separate final label if later batches continue showing users cannot act on raw IDs.

Supporting evidence: 10 notes across 6 traces

- Note 23, `722a3e707c0ad7ef7cd3c749097a1207` (support-0002, shopper): add which user id order the order id. Quote: “find_order()”
- Note 24, `722a3e707c0ad7ef7cd3c749097a1207` (support-0002, shopper): add prodcut name to the list Quote: “"product_id"”
- Note 28, `5ae9d430b85f988b4a42a382374e8fec` (support-0005, shopper): unclear message for the user - user does not know the order ids. Quote: “**Order #5*”
- Note 30, `5ae9d430b85f988b4a42a382374e8fec` (support-0005, shopper): add product name rather than order id - unclear data for user Quote: “*Order #3413** — ordered **Nov 17, 2025**”
- Note 35, `f6cb5d8760f9c08603caf657f9531bd7` (support-0016, shopper): unhelpful ask - users do not remember order ids. Quote: “**order number**”
- Note 38, `d3ecfb30a645f96ce5c354ae2b763dd3` (support-0025, shopper): users do not need refund id and order id Quote: “Refund ID: #575”
- Note 41, `d3ecfb30a645f96ce5c354ae2b763dd3` (support-0025, shopper): add exact product name to the details to clarify the ambiguity Quote: “Order: #246”
- Note 43, `7a288dcc0ebdd8202bc6625ffc899a1f` (support-0043, shopper): order id is unnecessary detail Quote: “Order #200”
- Note 57, `bbccf32f3db0f084963242d726d83fe6` (support-0195, shopper): product ids are not needed Quote: “**”
- Note 58, `bbccf32f3db0f084963242d726d83fe6` (support-0195, shopper): irrelevant information - show visual data to the user instead of prices and product ids. users do not remember product ids. Quote: “Product ID **19** — **$281.00**”

## `confusing_or_contradictory_answer`

Definition: The reply leaves the user unclear because it mixes concepts, uses alarming wording, fails to answer the actual request, or gives contradictory framing.

Boundary: Include direct confusion/contradiction notes and wording that creates the wrong impression. Exclude simple ambiguity that could be fixed by one clarifying question; those belong under missing clarification.

Requirement source: SPEC.md RESP-5; possibly RESP-3 when confusing wording hides uncertainty.

Supporting evidence: 4 notes across 4 traces

- Note 13, `905a5619a856cb3de0c8b5fe1378cea2` (support-0104, merchant): confusing answer - restocking fee is covered in policy but here we talk about exceptions. Quote: “If you choose to make an exception and accept the opened item anyway, the maximum restocking fee on this $196.75 order would be 15% = $29.51.”
- Note 27, `722a3e707c0ad7ef7cd3c749097a1207` (support-0002, shopper): unclear support - the user's ask for help does not seem to be answered. We listed the order and it look delivered - but the user still asking. Quote: “ooks like the order has”
- Note 51, `fa6bf0e0a85f6de2bb94eb2a1b7106e8` (support-0045, shopper): confusing language which may panic the user. Quote: “I don’t want to refund the wrong order. Please confirm: is order #245 the one you want refunded?”
- Note 71, `e3d93b15ba9f920783188e4cea85b5ca` (support-0159, support): ambiguity and contradiction - account settings host the account changes but also escalte to a human, creates confusion for the support user. Quote: “If an account-change issue needs help beyond that, we can escalate it to a human support agent.”

## `unsupported_or_invented_refund_option`

Definition: The reply presents a refund option, amount, or partial/full refund choice as available even though the reviewed policy/tool evidence does not support that option.

Boundary: Include invented partial/full refund authority and missing tool evidence for that choice. Exclude cases where a tool or policy explicitly confirms the refund option.

Requirement source: SPEC.md RESP-3: do not invent values or unsupported facts; refund policy files do not define a merchant partial/full refund choice in the evidence reviewed so far.

Supporting evidence: 2 notes across 1 traces

- Note 09, `d2885fe8f25ec0e4dad15f9e8b39e0fb` (support-0097, merchant): inventing rules - no partial vs full refund rules\ Quote: “full refund of $203.25, or a partial amount”
- Note 10, `d2885fe8f25ec0e4dad15f9e8b39e0fb` (support-0097, merchant): no tool calls indicating that there is a partial vs full refund option Quote: “Reason for the refund”

## `missed_data_quality_escalation`

Definition: The reply says a record looks normal even though the scenario/source data contains an inconsistency that should be detected and escalated.

Boundary: Include data-quality cases where the order/product/store record is inconsistent and the answer misses or denies the mismatch. Exclude ordinary uncertainty or missing data that does not have a concrete source-record inconsistency.

Requirement source: SPEC.md RESP-3 and escalation policy: inconsistent records should be stated/escalated rather than normalized away.

Supporting evidence: 2 notes across 2 traces

- Note 17, `31a1f4c60f841e8d276e17f53338c9c5` (support-0188, merchant): The agent says order 8003 looks clean, but the scenario is a store-mismatch data-quality case: the order is tied to store 1 while product 553 belongs to store 14. The agent did not detect or escalate the inconsistent record. Quote: “Order 8003 looks clean on the store side.”
- Note 77, `acaf262efa53b6cddbcaa836ae1ca6e9` (support-0186, support): The agent says order 8003’s store information looks normal, but the order is tied to store 1 while product 553 belongs to store 14. It missed the data-quality store mismatch and did not escalate the inconsistent record. Quote: “I don’t see a store/name mismatch in the order record.”

## `incorrect_data_value_reported`

Definition: The reply reports a materially wrong value from the record, such as an incorrect amount, in a way that changes the outcome.

Boundary: Keep separate from formatting or overload. This should become a final mode only if additional examples confirm a repeated pattern rather than a one-off trace.

Requirement source: SPEC.md RESP-3: do not invent or misstate values.

Supporting evidence: 1 notes across 1 traces

- Note 20, `6b0f8edadbf3c111c80f46baa8896fd2` (support-0200, merchant): incorrect amount, fatal mistake Quote: “**-$5.00** in your store”

## Held-out notes, not currently candidate failure modes

### `no_failure_observed`

Reviewed traces where the saved note says no failure/no failures.

Evidence kept aside: 5 notes across 5 traces

- Note 15, `ab94406ad046b4d85ddd7b2cfb694b7d` (support-0120, merchant): no failures Quote: “our recent store orders.”
- Note 59, `818e66d637558541d120e98a8137927c` (support-0235, shopper): no failures Quote: “e range”
- Note 60, `74da08cdd0866eacf95330dd752b8e3e` (support-0134, support): no failures Quote: “shows”
- Note 61, `1910c11d4de81a7b45ba542880435b83` (support-0136, support): no failures Quote: “etail”
- Note 62, `522b125e9d00f15c2d0c7d126dbbd648` (support-0137, support): no failures Quote: “12 shows:”

### `policy_name_preference_without_reference_request`

Preference to avoid exposing internal policy names. Held out unless paired with a request for a usable policy/help-center reference.

Evidence kept aside: 2 notes across 2 traces

- Note 73, `fe06cd1306890e4414a291780b343080` (support-0163, support): no need to call out specific policy name Quote: “Policy: `cw-escalations`”
- Note 78, `5023b152407f12c113be0006e2ca0315` (support-0240, support): no need to call out specific policy name Quote: “*cw-escalations*”

### `next_step_specificity_needs_more_examples`

A vague-next-step concern with too little independent evidence to promote yet.

Evidence kept aside: 1 notes across 1 traces

- Note 21, `6b0f8edadbf3c111c80f46baa8896fd2` (support-0200, merchant): vague language - help merchant how to fix the issue. Quote: “That looks unusual for a product price, so you may want to review the listing”

## Human decisions needed before Batch 3

- Decide whether to keep `identifier_heavy_or_missing_item_context` as its own candidate or merge it back into clarification/overload.
- Treat `unsupported_or_invented_refund_option` and `missed_data_quality_escalation` as high-value depth-search seeds because they have crisp source evidence and close negatives should be findable.
- Use Batch 3 to search for close positives and close negatives for data-quality escalation, refund-option invention, and identifier-heavy answers.
