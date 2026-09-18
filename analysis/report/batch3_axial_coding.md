# Batch 3 Axial Coding Draft

This draft groups the human open-code annotations from HW4 Part B Batch 3. Batch 3 was a depth-search batch: traces were selected to test candidate modes and close negative examples, not because an automated predictor labeled them as failures. The grouping is annotation-level: each saved note appears exactly once under a candidate mode or held-out bucket.

- Reviewed counted traces: 25
- Saved Batch 3 annotation notes: 61
- Batch type: depth search for candidate modes and close negatives
- Candidate modes represented in this draft: 9
- Agent-added labels: none; these are candidate groupings of human notes

## What Batch 3 changed

Batch 3 confirmed the presentation, reference, overload, clarification, identifier-context, refund-option, and confusion modes from the first two batches. The main conceptual change is that `missed_data_quality_escalation` should broaden into `unhandled_data_quality_or_record_inconsistency`, because the repeated evidence now includes store mismatches, reversed dates, negative prices, missing product titles, and duplicate product names. Batch 3 also makes `missing_human_review_followup_path` worth tracking separately from generic missing links: several refund/escalation traces say human review is needed but do not tell the user how that review will be tracked or completed.

## Boundary rules after Batch 3

- `unhandled_data_quality_or_record_inconsistency`: the source record is broken or inconsistent, and the assistant treats it as normal.
- `missing_human_review_followup_path`: human review is needed or queued, but the answer lacks a clear path for follow-up.
- `missing_actionable_reference`: a self-service or support reference is missing, such as a product page, store page, order page, viewed-item page, or policy/help article.
- `identifier_heavy_or_missing_item_context`: the answer gives identifiers or bare prices without enough human-recognizable product/order context.
- `unnecessary_detail_overload`: the answer includes extra facts or policy mechanics that distract from the current ask.
- `missing_clarification_or_disambiguation`: the answer should confirm an uncertain target or action before proceeding.
- `confusing_or_contradictory_answer`: the answer text gives the user a conflicting or unclear interpretation.
- `presentation_formatting_noise`: raw Markdown markers or hard-to-read tables make the response visually noisy.

## `unhandled_data_quality_or_record_inconsistency`

Definition: The reply treats corrupted, inconsistent, missing, or duplicate source data as normal instead of flagging the record problem and routing it to a human or repair path.

Boundary: Include false confidence about store mismatches, reversed dates, invalid negative prices, missing titles, and duplicate-title records when the response ignores or normalizes the source-data problem. Exclude ordinary ambiguous product matching without a known data-quality defect.

Relationship to earlier batches: Broadens Batch 2 `missed_data_quality_escalation`; Batch 3 shows the issue is not limited to order/store mismatches.

Requirement source: SPEC.md RESP-3: state missing or inconsistent information rather than inventing or normalizing values; escalation policy for cases the assistant cannot resolve from policy and the order record.

Supporting evidence: 7 notes across 6 traces

- Note 01, `483a07d37cfdb9e8e0bcf17f3050e16f` (support-0189, support): overly confident when the answer is false - Order #8003 is tied to store 1 (Blue Heron Ceramics), but product 553 belongs to store 14 (Golden Hour Coffee). Quote: “I don’t see a store ID/name mismatch on the order.”
- Note 02, `e2a0a77813a5b9277c1788dfd7722bb1` (support-0187, shopper): overly confident when the answer is false. Quote: “Details:”
- Note 03, `e2a0a77813a5b9277c1788dfd7722bb1` (support-0187, shopper): escalating path to human agent is missing - the broken records needs fixing. Quote: “The jam-related order I found is order **#8003**.”
- Note 05, `94671b82200254e8e6b773d106cec477` (support-0183, merchant): incorrectly confident even though the case should have been flagged to a human for further investigation. Agent needs to be more vary about the incosistencies Quote: “**June 23, 2026*”
- Note 08, `2eab0e9c080fd6b62c423857082c3afe` (support-0199, shopper): fatal mistake -> missing data problem and ignoring it completely - should have escalated this to a human agent. Quote: “**-$5.00**”
- Note 12, `0c8b63933204e67483d89ba01e5eb68f` (support-0204, merchant): no flag for the missing data to the merchant. Agent ignores the problem completely. Quote: “**Title:** No title listed”
- Note 15, `b7e6e9a02d897418212ee3d32640d941` (support-0194, merchant): flag same name issue - duplicates. `agent ignores that Quote: “Heavy-Duty Vase from Blue Heron Ceramics. Placeholder dev-scale listing; the full-scale catalog is sampled from the Amazon Reviews 2023 metadata.”

## `presentation_formatting_noise`

Definition: The response presentation makes the answer harder to read through visible Markdown markers or hard-to-scan table formatting.

Boundary: Include visible ** markers and table-display complaints. Exclude content overload unless the note is about visual readability.

Relationship to earlier batches: Confirmed from Batches 1 and 2.

Requirement source: SPEC.md RESP-5: direct and useful language; also a product/UI formatting expectation.

Supporting evidence: 7 notes across 7 traces

- Note 04, `714fbe9bedbfd275e6539b165de3d60b` (support-0181, support): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “*”
- Note 09, `6e0857b411210dd228ca6cc0ba8ee42e` (support-0198, support): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “*.”
- Note 14, `b7e6e9a02d897418212ee3d32640d941` (support-0194, merchant): bad formatting - need better table display Quote: “| Product ID | Title | Category | Price | Description |”
- Note 24, `ef201978c660e9b3b8f56fd249675941` (support-0095, merchant): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “**.”
- Note 28, `c7510a8f54af106b96b2856c00273e5f` (support-0039, shopper): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “*”
- Note 51, `26a5acb6094f57f898de43da211b84e7` (support-0250, shopper): no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. Quote: “*”
- Note 61, `5b4e0043940e5872a5a0e673493117d0` (support-0083, merchant): bad formatting - need better table display Quote: “| Order ID | Product ID | Qty | Total | Status | Ordered | Shipped | Delivered | Refund eligible |”

## `unnecessary_detail_overload`

Definition: The reply includes extra status, ticket/refund IDs, policy names, policy mechanics, or long order lists that distract from the current ask.

Boundary: Include facts the user does not need at this step. Exclude cases where the main problem is missing user-recognizable item context; those belong under `identifier_heavy_or_missing_item_context`.

Relationship to earlier batches: Confirmed from Batches 1 and 2.

Requirement source: SPEC.md RESP-5: clear, useful, task-focused responses.

Supporting evidence: 8 notes across 5 traces

- Note 07, `309ebfbc9689dca92e3a7c7b6a9f5670` (support-0180, support): do not need call out the opposite - already clarified the conditions in the previous sentence Quote: “not the purchase date”
- Note 11, `3eb872501faea4390f6b4ae6ec61435f` (support-0205, shopper): no need to share the ticket id with the user as they do not need it. Quote: “**Ticket #160**”
- Note 26, `77b1ffab2763d78d774327fc10967f1d` (support-0092, merchant): no need to call out specific status about auto-approvals Quote: “Status: auto-approved”
- Note 30, `c7510a8f54af106b96b2856c00273e5f` (support-0039, shopper): too much information - refund request id is not needed Quote: “**Refund request ID:** 577”
- Note 31, `c7510a8f54af106b96b2856c00273e5f` (support-0039, shopper): too much information - support ticket id is not relevant Quote: “**Support ticket:** 151”
- Note 32, `c7510a8f54af106b96b2856c00273e5f` (support-0039, shopper): too much information about policies. Quote: “Because the amount is over the auto-approval threshold, it’s been queued for human review.”
- Note 37, `f546444044510518456a2afa5e67481f` (support-0026, shopper): too much information - policy names do not need to be called out. Quote: “*cw-cancellations**”
- Note 39, `f546444044510518456a2afa5e67481f` (support-0026, shopper): too much data, user is only asking aboiut cards and we unload data about all the orders. Irrelevant and confusing data for the user Quote: “return/refund eligible”

## `missing_clarification_or_disambiguation`

Definition: The reply proceeds despite uncertainty about the intended product, order, timeframe, or support action instead of confirming the target first.

Boundary: Include vague wording, likely-match assertions, missing confirmation before refund/cancellation, and support workflows where the next action should be clarified. Exclude known data-quality defects; those belong under `unhandled_data_quality_or_record_inconsistency`.

Relationship to earlier batches: Confirmed from Batches 1 and 2.

Requirement source: SPEC.md RESP-3 and RESP-5.

Supporting evidence: 7 notes across 6 traces

- Note 13, `0c8b63933204e67483d89ba01e5eb68f` (support-0204, merchant): vague language - appears to be vs is Quote: “appears to be”
- Note 17, `d7f49dd47c67a8050ac129fa3a7c3046` (support-0193, support): unhelpful - support user could provide the list to get confirmation. Quote: “a link so you can confirm the exact price.”
- Note 27, `c7510a8f54af106b96b2856c00273e5f` (support-0039, shopper): making assumptions - needs clarity to understand what needs to be refunde first. agent is too quick to decide. Quote: “so I submitted the refund request”
- Note 34, `f546444044510518456a2afa5e67481f` (support-0026, shopper): too confident - I can help but then adding bombardment of information that confuses the user further. Quote: “I can help.”
- Note 44, `08b10fed6ad100ae9fe9293d229521e4` (support-0247, shopper): confusing message - likely the plate set is not clear enougnt for the user Quote: “**Item:** likely the plate set”
- Note 45, `08b10fed6ad100ae9fe9293d229521e4` (support-0247, shopper): agent making assumptions and guiding the user through a bumpy road Quote: “found one”
- Note 49, `26a5acb6094f57f898de43da211b84e7` (support-0250, shopper): vague language - "looks like" Quote: “It looks like the gardening”

## `identifier_heavy_or_missing_item_context`

Definition: The answer relies on internal IDs or bare prices, or omits product names/images/links, so the user cannot recognize the item, order, refund, or cancellation being discussed.

Boundary: Include raw order IDs/product IDs, missing product names, price lists without item context, and requests for visual/product links. Exclude general self-service links; those belong under `missing_actionable_reference`.

Relationship to earlier batches: New in Batch 2 and strongly confirmed in Batch 3.

Requirement source: SPEC.md RESP-5; likely needs a product requirement for user-recognizable order/product references.

Supporting evidence: 10 notes across 6 traces

- Note 16, `d7f49dd47c67a8050ac129fa3a7c3046` (support-0193, support): price listings without product names and product links is ambiguous. Quote: “Tell the shopper the available prices are:”
- Note 19, `b070b0ef604e506c9987e37eed52566a` (support-0192, shopper): unhelpful and not clear - send product links, images together with the price data. Quote: “- $9.00 - $134.75 - $149.50 - $254.75 - $281.00”
- Note 38, `f546444044510518456a2afa5e67481f` (support-0026, shopper): order id is unnecessary detail Quote: “*Order #8134**”
- Note 40, `f546444044510518456a2afa5e67481f` (support-0026, shopper): should have listed the exact product name - product name is there, instead of product ids and order ids Quote: “Wooden Whale Workshop”
- Note 42, `08b10fed6ad100ae9fe9293d229521e4` (support-0247, shopper): order id is unnecessary detail Quote: “**Order #323**”
- Note 46, `08b10fed6ad100ae9fe9293d229521e4` (support-0247, shopper): irrelevant data - users do not remember order 323 Quote: “order #323.”
- Note 47, `08b10fed6ad100ae9fe9293d229521e4` (support-0247, shopper): missing product name in the order summary Quote: “- **Status:** Delivered”
- Note 48, `26a5acb6094f57f898de43da211b84e7` (support-0250, shopper): order id is unnecessary detail Quote: “**Order #8777**”
- Note 57, `aa6bea5cfcf590cbbb70f1c08ee41002` (support-0060, shopper): order id is unnecessary detail Quote: “#3722.”
- Note 59, `aa6bea5cfcf590cbbb70f1c08ee41002` (support-0060, shopper): missing information in out output - add picture, link and exact product name of the cancelled order so that user is fully aware Quote: “Done”

## `missing_actionable_reference`

Definition: The reply does not give a concrete link, account path, policy page, store page, viewed-item page, order page, or other self-service reference the user can follow.

Boundary: Include explicit requests for links or pages. Exclude “do not call out policy name” preferences unless they also ask for a usable reference.

Relationship to earlier batches: Confirmed from Batches 1 and 2.

Requirement source: SPEC.md RESP-5; likely needs a product/UI requirement for usable references.

Supporting evidence: 9 notes across 8 traces

- Note 18, `b070b0ef604e506c9987e37eed52566a` (support-0192, shopper): send a link to the user with their "viewed items" Quote: “Prices include:”
- Note 29, `c7510a8f54af106b96b2856c00273e5f` (support-0039, shopper): add a link for the user which can help them to find their orders on their own account. Quote: “Order #120”
- Note 35, `f546444044510518456a2afa5e67481f` (support-0026, shopper): send user to their recent order link if they want to self-validate. Quote: “couldn’t find an order matching “playcards” exactly,”
- Note 36, `f546444044510518456a2afa5e67481f` (support-0026, shopper): certainty is missing - send user to return policy page to get full confirmation. Quote: “can likely be”
- Note 43, `08b10fed6ad100ae9fe9293d229521e4` (support-0247, shopper): send user to their recent order link if they want to self-validate. Quote: “matching order”
- Note 50, `26a5acb6094f57f898de43da211b84e7` (support-0250, shopper): add a link for the user which can help them to find their orders on their own account. Quote: “item was:”
- Note 53, `8ae6239e34515492ba4ea2873f314759` (support-0054, shopper): add a link for the user which can help them to find their orders on their own account. Quote: “find an order matching “snack bag””
- Note 58, `aa6bea5cfcf590cbbb70f1c08ee41002` (support-0060, shopper): add a link for the user which can help them to find their orders on their own account. Quote: “I cancelled your dry bag order”
- Note 60, `5b4e0043940e5872a5a0e673493117d0` (support-0083, merchant): add a link for the merchant where they can see their store details Quote: “Here are Meridian Cycles’ 20 recent orders:”

## `unsupported_or_invented_refund_option`

Definition: The reply presents a refund choice, such as full versus partial refund, as available even though the reviewed policy/tool evidence does not define that option.

Boundary: Include invented refund-option language. Exclude legitimate queued or auto-approved refund statuses when the tool confirms them.

Relationship to earlier batches: New in Batch 2 and confirmed again in Batch 3.

Requirement source: SPEC.md RESP-3: do not invent unsupported facts or values.

Supporting evidence: 2 notes across 2 traces

- Note 20, `83164a4efc01ed104438919841ff9199` (support-0086, merchant): partial refund or full refund are not separate options. agent seems to invent rules. Quote: “**full refund of $158.25**, or a partial refund?”
- Note 22, `e1599c9c9c67ce20187cc5b58411d2cf` (support-0098, merchant): refund options are non-existent - inventing options. Quote: “**full refund of $177.25**?”

## `missing_human_review_followup_path`

Definition: The reply says or implies human review is needed, but does not explain how the user or merchant can track, trigger, or complete that human follow-up.

Boundary: Include queued refunds and above-threshold human-review cases where the path is unclear. Exclude source-record defects unless the note specifically asks for a human path for fixing the record.

Relationship to earlier batches: Sharper split from `missing_actionable_reference`; Batch 3 supplied repeated refund/escalation-path evidence.

Requirement source: Escalation policy and SPEC.md RESP-5: escalation should leave the user with a clear next step.

Supporting evidence: 3 notes across 3 traces

- Note 21, `83164a4efc01ed104438919841ff9199` (support-0086, merchant): no escalation is being called as human agent involvement is needed. Quote: “The order total is **$158.25**.”
- Note 23, `e1599c9c9c67ce20187cc5b58411d2cf` (support-0098, merchant): human escalation path is not called Quote: “The order total is **$177.25**.”
- Note 25, `ef201978c660e9b3b8f56fd249675941` (support-0095, merchant): follow up is not clarified - where and how, unclear guidance that creates confusion. Quote: “follow up.”

## `confusing_or_contradictory_answer`

Definition: The reply leaves the user with an unclear or conflicting interpretation because the chosen match, status, or policy explanation contradicts the ask or earlier framing.

Boundary: Include confusing irrelevant matches, refund-eligible-versus-human-review confusion, and account-change contradictions. Exclude simple missing confirmation, which belongs under clarification.

Relationship to earlier batches: Confirmed from Batches 1 and 2.

Requirement source: SPEC.md RESP-5 and RESP-3 when the confusion hides uncertainty.

Supporting evidence: 5 notes across 5 traces

- Note 10, `3eb872501faea4390f6b4ae6ec61435f` (support-0205, shopper): inventing an irrelevant entry - confusing data for the user Quote: “The closest match is an order from **store 3**:  - **Order #8666** - **Product ID:** 109 - **Status:** delivered - **Ordered:** 2025-02-05”
- Note 33, `c7510a8f54af106b96b2856c00273e5f` (support-0039, shopper): contradicting and confusing data - marked refund-eligible and then human follow up in 24 hrs is confusing Quote: “A human support agent should follow up within **24 hours**.”
- Note 41, `f546444044510518456a2afa5e67481f` (support-0026, shopper): lacking matching capability - Woven Card Game is the name of the product. Confusing data for the user Quote: “but I do see a few June orders on your account:”
- Note 52, `8ae6239e34515492ba4ea2873f314759` (support-0054, shopper): irrelevant data - snack bag has nothing to do with Coffee. Quote: “I did find one order that can likely still be canceled because it hasn’t shipped yet”
- Note 56, `9e94c136ef865e5fcce260112ecf2e6b` (support-0218, support): contradiction to what was said in the beginning of the conversation Quote: “If they can’t access the account or the change needs staff handling, escalate to a human support agent; account changes go to a human”

## Held-out notes, not currently candidate failure modes

### `policy_name_preference_without_reference_request`

Preference to avoid exposing internal policy names. Held out unless paired with a request for a usable policy/help-center link.

Evidence kept aside: 3 notes across 3 traces

- Note 06, `309ebfbc9689dca92e3a7c7b6a9f5670` (support-0180, support): no need to call out specific policy name Quote: “cw-returns”
- Note 54, `579aa949ed85ee8cf0ba43aee661764a` (support-0237, support): no need to call out specific policy name Quote: “**cw-escalations*”
- Note 55, `9e94c136ef865e5fcce260112ecf2e6b` (support-0218, support): no need to call out specific policy name Quote: “cw-account-security”

## Human decisions before Batch 4

- Decide whether to accept the broader `unhandled_data_quality_or_record_inconsistency` name, replacing the narrower Batch 2 `missed_data_quality_escalation`.
- Decide whether `missing_human_review_followup_path` should remain separate from `missing_actionable_reference` in the final taxonomy.
- Batch 4 should be a fresh uniform sample of 15 traces to test whether new modes continue to appear after these depth-search refinements.
