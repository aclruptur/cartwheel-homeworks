# Final Failure Mode Taxonomy Draft

This is the stabilized HW4 taxonomy after four review batches and the Part C Workshop cross-check. Batch 4 did not surface a new failure family. After reviewing the mode boundaries, two narrow low-count categories were merged into broader binary modes, leaving 7 final modes.

## Merged categories

- `missing_actionable_reference` and `missing_human_review_followup_path` were merged into `missing_actionable_next_step`, because both failures leave the user without a concrete path to continue.
- `confusing_or_contradictory_answer` and `unsupported_or_invented_refund_option` were merged into `confusing_or_unsupported_answer`, because unsupported refund choices are a specific form of unsupported or misleading answer.

## `unhandled_data_quality_or_record_inconsistency`

Definition: The source order/product/policy record is missing, corrupted, contradictory, or otherwise inconsistent, and the assistant treats the record as normal or gives an unsupported answer instead of flagging/escalating it.

Binary rule: Fail when the trace contains source-record inconsistency or missing critical source data and the assistant does not clearly flag/escalate it. Pass when no such defect appears, or the assistant explicitly flags/escalates the defect without normalizing it.

Requirement source: `RESP-3`, `ESC-4`.

Likely evaluator type: LLM judge with tool/database context; some subcases can be code-assisted by checking inconsistent fields.

Boundary: Nearest neighbor: confusing_or_unsupported_answer. Use this mode when the source record itself is missing, corrupted, or internally inconsistent and the assistant normalizes it; use confusing_or_unsupported_answer when the record is usable but the answer misstates or overclaims what it means.

Confirmed positive traces:

- `31a1f4c60f841e8d276e17f53338c9c5` (`support-0188`, merchant): unhandled_data_quality_or_record_inconsistency: part_b_batch_2 note 17: The agent says order 8003 looks clean, but the scenario is a store-mismatch data-quality case: the order is tied to store 1 while product 553 belongs to store 14. The agent did not detect or escalate the inconsistent record.
- `acaf262efa53b6cddbcaa836ae1ca6e9` (`support-0186`, support): unhandled_data_quality_or_record_inconsistency: part_b_batch_2 note 77: The agent says order 8003’s store information looks normal, but the order is tied to store 1 while product 553 belongs to store 14. It missed the data-quality store mismatch and did not escalate the inconsistent record.
- `483a07d37cfdb9e8e0bcf17f3050e16f` (`support-0189`, support): unhandled_data_quality_or_record_inconsistency: part_b_batch_3 note 01: overly confident when the answer is false - Order #8003 is tied to store 1 (Blue Heron Ceramics), but product 553 belongs to store 14 (Golden Hour Coffee).

Close negative traces:

- `366acfa3511aa64e7f7e70303993289d` (`support-0145`, support): reviewed trace did not contain this failure mode.
- `016e3cc0f7504d6656aa564509d639ec` (`support-0131`, support): reviewed trace did not contain this failure mode.
- `fe47fec4e03cf55aa5df32fc9268fb60` (`support-0217`, support): reviewed trace did not contain this failure mode.

Originating human annotations:

- `31a1f4c60f841e8d276e17f53338c9c5`: unhandled_data_quality_or_record_inconsistency: part_b_batch_2 note 17: The agent says order 8003 looks clean, but the scenario is a store-mismatch data-quality case: the order is tied to store 1 while product 553 belongs to store 14. The agent did not detect or escalate the inconsistent record.
- `acaf262efa53b6cddbcaa836ae1ca6e9`: unhandled_data_quality_or_record_inconsistency: part_b_batch_2 note 77: The agent says order 8003’s store information looks normal, but the order is tied to store 1 while product 553 belongs to store 14. It missed the data-quality store mismatch and did not escalate the inconsistent record.
- `483a07d37cfdb9e8e0bcf17f3050e16f`: unhandled_data_quality_or_record_inconsistency: part_b_batch_3 note 01: overly confident when the answer is false - Order #8003 is tied to store 1 (Blue Heron Ceramics), but product 553 belongs to store 14 (Golden Hour Coffee).

## `missing_actionable_next_step`

Definition: The answer requires the user or a human support process to continue, but omits the concrete path, reference, owner, tracking destination, or follow-up step needed to proceed.

Binary rule: Fail when the response leaves out a concrete reference, link, account path, policy/help-center page, owner, ticket/status location, or next handoff step needed for the user role to continue. Pass when no next step is needed or the response gives a clear enough path.

Merged from: `missing_actionable_reference`, `missing_human_review_followup_path`.

Requirement source: `PURPOSE-1`, `SCOPE-1`, `ESC-1`, `ESC-3`, `ESC-4`, `RESP-5`.

Likely evaluator type: LLM judge

Boundary: Nearest neighbor: identifier_heavy_or_missing_item_context. Use this mode when the missing piece is a path, link, owner, ticket, policy page, or handoff step; use identifier_heavy_or_missing_item_context when the problem is recognizing which item/order/refund is being discussed.

Confirmed positive traces:

- `366acfa3511aa64e7f7e70303993289d` (`support-0145`, support): missing_actionable_reference: part_b_batch_1 note 02: calling policy name is not necessary. Add policy link as a reference.
- `fe47fec4e03cf55aa5df32fc9268fb60` (`support-0217`, support): missing_actionable_reference: part_b_batch_1 note 11: send them to the relevant help center / policy article so that they can read and learn more
- `ef201978c660e9b3b8f56fd249675941` (`support-0095`, merchant): missing_human_review_followup_path: part_b_batch_3 note 25: follow up is not clarified - where and how, unclear guidance that creates confusion.

Close negative traces:

- `016e3cc0f7504d6656aa564509d639ec` (`support-0131`, support): reviewed trace did not contain this failure mode.
- `3879d32468ca34fb9e43df6f162197a2` (`support-0165`, support): reviewed trace did not contain this failure mode.
- `c8f92db31ccff89e08b51949908df3fe` (`support-0058`, shopper): reviewed trace did not contain this failure mode.

Originating human annotations:

- `366acfa3511aa64e7f7e70303993289d`: missing_actionable_reference: part_b_batch_1 note 02: calling policy name is not necessary. Add policy link as a reference.
- `fe47fec4e03cf55aa5df32fc9268fb60`: missing_actionable_reference: part_b_batch_1 note 11: send them to the relevant help center / policy article so that they can read and learn more
- `ef201978c660e9b3b8f56fd249675941`: missing_human_review_followup_path: part_b_batch_3 note 25: follow up is not clarified - where and how, unclear guidance that creates confusion.

## `identifier_heavy_or_missing_item_context`

Definition: The answer relies on raw order IDs/product IDs/refund IDs/bare prices, or omits product names/images/links/context, making it hard for the user to recognize the item, order, refund, or cancellation.

Binary rule: Fail when the response centers internal IDs or lacks user-recognizable item/order context. Pass when the answer gives enough user-facing context to identify the object.

Requirement source: `RESP-5`.

Likely evaluator type: LLM judge; code checks can flag raw-id-heavy text as a retrieval aid.

Boundary: Nearest neighbor: unnecessary_detail_overload. Use this mode when the answer lacks user-recognizable product/order context or over-relies on internal IDs; use unnecessary_detail_overload when the answer contains too much otherwise valid information.

Confirmed positive traces:

- `722a3e707c0ad7ef7cd3c749097a1207` (`support-0002`, shopper): identifier_heavy_or_missing_item_context: part_b_batch_2 note 23: add which user id order the order id. | part_b_batch_2 note 24: add prodcut name to the list
- `5ae9d430b85f988b4a42a382374e8fec` (`support-0005`, shopper): identifier_heavy_or_missing_item_context: part_b_batch_2 note 28: unclear message for the user - user does not know the order ids. | part_b_batch_2 note 30: add product name rather than order id - unclear data for user
- `d3ecfb30a645f96ce5c354ae2b763dd3` (`support-0025`, shopper): identifier_heavy_or_missing_item_context: part_b_batch_2 note 38: users do not need refund id and order id | part_b_batch_2 note 41: add exact product name to the details to clarify the ambiguity

Close negative traces:

- `366acfa3511aa64e7f7e70303993289d` (`support-0145`, support): reviewed trace did not contain this failure mode.
- `fe47fec4e03cf55aa5df32fc9268fb60` (`support-0217`, support): reviewed trace did not contain this failure mode.
- `379b97d2d2ab40d9f88dda2d9da2b217` (`support-0222`, merchant): reviewed trace did not contain this failure mode.

Originating human annotations:

- `722a3e707c0ad7ef7cd3c749097a1207`: identifier_heavy_or_missing_item_context: part_b_batch_2 note 23: add which user id order the order id. | part_b_batch_2 note 24: add prodcut name to the list
- `5ae9d430b85f988b4a42a382374e8fec`: identifier_heavy_or_missing_item_context: part_b_batch_2 note 28: unclear message for the user - user does not know the order ids. | part_b_batch_2 note 30: add product name rather than order id - unclear data for user
- `d3ecfb30a645f96ce5c354ae2b763dd3`: identifier_heavy_or_missing_item_context: part_b_batch_2 note 38: users do not need refund id and order id | part_b_batch_2 note 41: add exact product name to the details to clarify the ambiguity

## `unnecessary_detail_overload`

Definition: The answer includes extra policy mechanics, calculations, statuses, IDs, records, or long lists that distract from the current ask.

Binary rule: Fail when the response includes material extra detail that makes the answer harder to use. Pass when the response stays focused on the task even if it includes necessary facts.

Requirement source: `RESP-5`.

Likely evaluator type: LLM judge

Boundary: Nearest neighbor: presentation_formatting_noise. Use this mode when the content is too long or irrelevant; use presentation_formatting_noise when the content may be right-sized but rendered with visible markup or poor layout.

Confirmed positive traces:

- `d2fdbbb39bb1aa2c13674d5e379037af` (`support-0027`, shopper): unnecessary_detail_overload: part_b_batch_1 note 03: no need to give detail on the return policy if the item is not found
- `39c29018745ef39229596313743c2e67` (`support-0166`, support): unnecessary_detail_overload: part_b_batch_1 note 26: no need to give product details as the user is asking about refund.
- `376a003be2fb346b0a9817dc09a9c9fe` (`support-0246`, shopper): unnecessary_detail_overload: part_b_batch_1 note 32: order id, status, refund details are all unnecessary and confusing details. Ask the user first what they need help with after confirming that their order has been located.

Close negative traces:

- `366acfa3511aa64e7f7e70303993289d` (`support-0145`, support): reviewed trace did not contain this failure mode.
- `fe47fec4e03cf55aa5df32fc9268fb60` (`support-0217`, support): reviewed trace did not contain this failure mode.
- `3879d32468ca34fb9e43df6f162197a2` (`support-0165`, support): reviewed trace did not contain this failure mode.

Originating human annotations:

- `d2fdbbb39bb1aa2c13674d5e379037af`: unnecessary_detail_overload: part_b_batch_1 note 03: no need to give detail on the return policy if the item is not found
- `39c29018745ef39229596313743c2e67`: unnecessary_detail_overload: part_b_batch_1 note 26: no need to give product details as the user is asking about refund.
- `376a003be2fb346b0a9817dc09a9c9fe`: unnecessary_detail_overload: part_b_batch_1 note 32: order id, status, refund details are all unnecessary and confusing details. Ask the user first what they need help with after confirming that their order has been located.

## `missing_clarification_or_disambiguation`

Definition: The assistant proceeds with a likely match, action, or answer before clarifying an ambiguous product, order, timeframe, user intent, or support context.

Binary rule: Fail when the trace needed a clarifying question or confirmation before proceeding. Pass when the target/action was clear or the assistant appropriately asks for confirmation.

Requirement source: `ESC-4`, `RESP-3`, `RESP-5`.

Likely evaluator type: LLM judge

Boundary: Nearest neighbor: confusing_or_unsupported_answer. Use this mode when the assistant should ask a question before proceeding; use confusing_or_unsupported_answer when it proceeds and the resulting answer is internally inconsistent or unsupported.

Confirmed positive traces:

- `c8f92db31ccff89e08b51949908df3fe` (`support-0058`, shopper): missing_clarification_or_disambiguation: part_b_batch_1 note 22: use exact product name instead - users do not remember or know the order ids | part_b_batch_1 note 23: could have confirmed with the user first because user does not seem to remember what they order and when they had order it. After the confirmation, they can cancel or continue after confirmation
- `376a003be2fb346b0a9817dc09a9c9fe` (`support-0246`, shopper): missing_clarification_or_disambiguation: part_b_batch_1 note 32: order id, status, refund details are all unnecessary and confusing details. Ask the user first what they need help with after confirming that their order has been located.
- `711f10764478d49b30f0fe3a15317649` (`support-0190`, shopper): missing_clarification_or_disambiguation: part_b_batch_1 note 45: agent making assumptions and guiding the user through a bumpy road

Close negative traces:

- `366acfa3511aa64e7f7e70303993289d` (`support-0145`, support): reviewed trace did not contain this failure mode.
- `016e3cc0f7504d6656aa564509d639ec` (`support-0131`, support): reviewed trace did not contain this failure mode.
- `fe47fec4e03cf55aa5df32fc9268fb60` (`support-0217`, support): reviewed trace did not contain this failure mode.

Originating human annotations:

- `c8f92db31ccff89e08b51949908df3fe`: missing_clarification_or_disambiguation: part_b_batch_1 note 22: use exact product name instead - users do not remember or know the order ids | part_b_batch_1 note 23: could have confirmed with the user first because user does not seem to remember what they order and when they had order it. After the confirmation, they can cancel or continue after confirmation
- `376a003be2fb346b0a9817dc09a9c9fe`: missing_clarification_or_disambiguation: part_b_batch_1 note 32: order id, status, refund details are all unnecessary and confusing details. Ask the user first what they need help with after confirming that their order has been located.
- `711f10764478d49b30f0fe3a15317649`: missing_clarification_or_disambiguation: part_b_batch_1 note 45: agent making assumptions and guiding the user through a bumpy road

## `confusing_or_unsupported_answer`

Definition: The response gives a conflicting, misleading, unclear, or unsupported interpretation of status, policy, authorization, matching evidence, refund options, or next steps.

Binary rule: Fail when the text leaves the user with a contradictory or materially confusing interpretation, or asserts an option/outcome that the available policy or tool evidence does not support. Pass when the answer is supported and any issue is only missing links, excess detail, or formatting without contradiction.

Merged from: `confusing_or_contradictory_answer`, `unsupported_or_invented_refund_option`.

Requirement source: `RESP-2`, `RESP-3`, `RESP-5`, `TOOL-7`, `ESC-1`.

Likely evaluator type: LLM judge with tool/policy evidence; specific write-success claims can be code checked.

Boundary: Nearest neighbor: unhandled_data_quality_or_record_inconsistency. Use this mode when the answer misleads, contradicts itself, or asserts unsupported policy/refund/status options; use data-quality mode when the root evidence is an inconsistent source record that should have been flagged.

Confirmed positive traces:

- `d2fdbbb39bb1aa2c13674d5e379037af` (`support-0027`, shopper): confusing_or_contradictory_answer: part_b_batch_1 note 05: contradiction to what was said in the beginning of the conversation
- `379b97d2d2ab40d9f88dda2d9da2b217` (`support-0222`, merchant): confusing_or_contradictory_answer: part_b_batch_1 note 13: confusing message, contradicting with what's asked and answered in other lines.
- `e72f2e0f927f0d0f4bed77be7d0fa900` (`support-0099`, merchant): confusing_or_contradictory_answer: part_b_batch_4 note 08: confusing information - the refund amount is over 100$ by defaullt already. Unclear and contradicting message | unsupported_or_invented_refund_option: part_b_batch_4 note 09: inventing rules - no partial vs full refund rules

Close negative traces:

- `366acfa3511aa64e7f7e70303993289d` (`support-0145`, support): reviewed trace did not contain this failure mode.
- `016e3cc0f7504d6656aa564509d639ec` (`support-0131`, support): reviewed trace did not contain this failure mode.
- `fe47fec4e03cf55aa5df32fc9268fb60` (`support-0217`, support): reviewed trace did not contain this failure mode.

Originating human annotations:

- `d2fdbbb39bb1aa2c13674d5e379037af`: confusing_or_contradictory_answer: part_b_batch_1 note 05: contradiction to what was said in the beginning of the conversation
- `379b97d2d2ab40d9f88dda2d9da2b217`: confusing_or_contradictory_answer: part_b_batch_1 note 13: confusing message, contradicting with what's asked and answered in other lines.
- `e72f2e0f927f0d0f4bed77be7d0fa900`: confusing_or_contradictory_answer: part_b_batch_4 note 08: confusing information - the refund amount is over 100$ by defaullt already. Unclear and contradicting message | unsupported_or_invented_refund_option: part_b_batch_4 note 09: inventing rules - no partial vs full refund rules

## `presentation_formatting_noise`

Definition: Visible Markdown markers, badly rendered tables, or other presentation choices make the response harder to read.

Binary rule: Fail when formatting/presentation noise is present. Pass when no formatting issue was noted.

Requirement source: `RESP-5`.

Likely evaluator type: Code check for visible Markdown/table artifacts, with LLM judge for broader readability.

Boundary: Nearest neighbor: unnecessary_detail_overload. Use this mode when readability is harmed by visible Markdown markers, table rendering, or layout; use overload when the wording includes unnecessary content even if formatting is clean.

Confirmed positive traces:

- `366acfa3511aa64e7f7e70303993289d` (`support-0145`, support): presentation_formatting_noise: part_b_batch_1 note 01: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- `3879d32468ca34fb9e43df6f162197a2` (`support-0165`, support): presentation_formatting_noise: part_b_batch_1 note 14: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- `a8d38a551dce6c17faa55af6d1704108` (`support-0241`, merchant): presentation_formatting_noise: part_b_batch_1 note 15: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. | part_b_batch_1 note 18: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.

Close negative traces:

- `d2fdbbb39bb1aa2c13674d5e379037af` (`support-0027`, shopper): reviewed trace did not contain this failure mode.
- `016e3cc0f7504d6656aa564509d639ec` (`support-0131`, support): reviewed trace did not contain this failure mode.
- `fe47fec4e03cf55aa5df32fc9268fb60` (`support-0217`, support): reviewed trace did not contain this failure mode.

Originating human annotations:

- `366acfa3511aa64e7f7e70303993289d`: presentation_formatting_noise: part_b_batch_1 note 01: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- `3879d32468ca34fb9e43df6f162197a2`: presentation_formatting_noise: part_b_batch_1 note 14: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- `a8d38a551dce6c17faa55af6d1704108`: presentation_formatting_noise: part_b_batch_1 note 15: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead. | part_b_batch_1 note 18: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.

## Workshop Part C cross-check

Raindrop Workshop did not add a new failure mode. It produced three useful taxonomy decisions:

- Accepted: `cli-support-9501-1789750638-1` supports `unhandled_data_quality_or_record_inconsistency`; order 8003's order store and product store disagree, and the assistant normalized the record as normal.
- Revised: local-only Workshop tool activity is available as interaction metadata rather than full tool spans because this setup does not use a Raindrop Cloud write key. We used it for hypothesis generation while keeping Langfuse/review UI as the canonical annotation path.
- Rejected: explicit policy identifiers are not automatically `presentation_formatting_noise`; for support users asking about policy authority, they can be useful evidence.
