# Batch 1 Axial Coding Draft

This draft groups the human open-code annotations from HW4 Part B Batch 1. It is still a draft taxonomy, but the grouping is now annotation-level: a note appears under a candidate mode only when that exact note supports that mode.

- Reviewed counted traces: 30
- Saved Batch 1 annotation notes: 82
- Candidate modes proposed: 6
- Agent-added labels: none; these are candidate groupings of human notes

## Boundary rules for the four easy-to-confuse modes

- `missing_actionable_reference`: the answer lacks a link, article, policy line, account-settings path, or order-history self-service reference. “No need to call out policy name” is not enough by itself.
- `unnecessary_detail_overload`: the answer contains extra order/product/refund/policy detail or action that distracts from the current ask. Example: giving return-policy detail when the item was not found.
- `missing_clarification_or_disambiguation`: the answer moves forward when the product/order/action is ambiguous, asks for an unnecessarily hard identifier, or fails to ask the user to confirm a likely match.
- `confusing_or_contradictory_answer`: the answer contradicts itself or mixes concepts such as refund status and refund eligibility, leaving the user unclear even if the answer were shorter.

## `presentation_formatting_noise`

Definition: The response presentation makes the answer harder to read through visible Markdown markers, poor table/list formatting, or repetitive wording.

Boundary: Include visible ** markers, table/list formatting complaints, and repetitive wording. Exclude tone or word-choice notes such as “override” being too strong unless the reviewer explicitly ties them to readability/formatting.

Requirement source: SPEC.md RESP-5: direct and respectful language; this may become a clearer formatting/display requirement.

Supporting evidence: 22 notes across 19 traces

- Note 01, `366acfa3511aa64e7f7e70303993289d`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 14, `3879d32468ca34fb9e43df6f162197a2`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 15, `a8d38a551dce6c17faa55af6d1704108`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 18, `a8d38a551dce6c17faa55af6d1704108`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 19, `4c5f4cc3afb3608ca1951bf339a987a5`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 25, `39c29018745ef39229596313743c2e67`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 28, `08c47004530a13ea061e9f5390011b18`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 29, `08c47004530a13ea061e9f5390011b18`: bad formatting - need better table display
- Note 31, `eea73132c90033aedac645d2df31cfe4`: repetitive wording
- Note 33, `03293b341bd64bcbd20d10ec41865ae9`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 36, `6396cf5a49521d14eca5298573dda90b`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 37, `6396cf5a49521d14eca5298573dda90b`: bad formatting - need better table display
- Note 47, `711f10764478d49b30f0fe3a15317649`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 53, `4970b9c3abfadd21f6a5db83f791506a`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 54, `e9f48e6de3778a6f7d5356943df48268`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 56, `6d1fe5cbffc957525774784137281ada`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 63, `9f2ca35491d1cebb8777dd5643bfec5e`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 69, `744d9f6a8a47ae71e1f5821621f06e6e`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 75, `e3e7e2776ea3196de7acdca7d450bbc0`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 76, `c48547e6341ce5472616c70a2412646d`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 79, `4d5f7611cdb1aeec2fde1580ed151132`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.
- Note 81, `2a58d59844efc14cfc1f5a8fb2489d74`: no need to use ** marks. Noisy signs that makes it harder to read. Should use bold font instead.

## `missing_actionable_reference`

Definition: The reply gives guidance but omits the concrete reference/path the user or support agent can follow, such as a help-center article, policy link, account-settings path, or order-history self-service link.

Boundary: Include notes that ask for a link, article, policy line, account-settings path, or self-service order link. Exclude “no need to call out policy name” when it does not also ask for a usable reference. Exclude excessive policy detail; that belongs under unnecessary_detail_overload.

Requirement source: SPEC.md RESP-1 for policy identifiers and RESP-5 for useful responses; link/path expectations may need a SPEC revision.

Supporting evidence: 17 notes across 15 traces

- Note 02, `366acfa3511aa64e7f7e70303993289d`: calling policy name is not necessary. Add policy link as a reference.
- Note 07, `d2fdbbb39bb1aa2c13674d5e379037af`: add a link for the user which can help them to find their orders on their own account.
- Note 11, `fe47fec4e03cf55aa5df32fc9268fb60`: send them to the relevant help center / policy article so that they can read and learn more
- Note 12, `379b97d2d2ab40d9f88dda2d9da2b217`: add a link for the policy line for the support to read
- Note 16, `a8d38a551dce6c17faa55af6d1704108`: add link to the policy or help center link the user can read.
- Note 20, `4c5f4cc3afb3608ca1951bf339a987a5`: add a policy / help center article link the support user can refer to
- Note 21, `4c5f4cc3afb3608ca1951bf339a987a5`: missing instruction - add a section how users can find their account settings or add a help center article page that guides users
- Note 30, `08c47004530a13ea061e9f5390011b18`: send the merchant to an account setting link where they can see their recent store movements.
- Note 38, `6396cf5a49521d14eca5298573dda90b`: send the merchant to an account setting link where they can see their recent store movements.\
- Note 42, `e75ac79481909be1b048b94f3df5b60b`: send them to the relevant help center / policy article so that they can read and learn more
- Note 46, `711f10764478d49b30f0fe3a15317649`: send user to their recent order link if they want to self-validate.
- Note 49, `c7c918336747a818730e6bf1ca3506fc`: add a link for the user which can help them to find their orders on their own accou\nt.
- Note 59, `9f2ca35491d1cebb8777dd5643bfec5e`: add a link for the user which can help them to find their orders on their own account.
- Note 71, `744d9f6a8a47ae71e1f5821621f06e6e`: add a link for the user which can help them to find their orders on their own account.
- Note 74, `e3e7e2776ea3196de7acdca7d450bbc0`: send them to the relevant help center / policy article so that they can read and learn more
- Note 77, `c48547e6341ce5472616c70a2412646d`: add a link for the policy line for the support to read
- Note 78, `c48547e6341ce5472616c70a2412646d`: add a policy / help center article link the support user can refer to in their comms with the user

## `unnecessary_detail_overload`

Definition: The reply includes details or actions that distract from the current ask or appear before the user has confirmed what they need.

Boundary: Include unnecessary order IDs, product details, refund details, policy detail when the item was not found, unnecessary confirmations, and unnecessary actions. Exclude cases where the problem is the absence of a link/path; those belong under missing_actionable_reference.

Requirement source: SPEC.md RESP-5: answer clearly and usefully; may need a concise task-focused response requirement.

Supporting evidence: 13 notes across 12 traces

- Note 03, `d2fdbbb39bb1aa2c13674d5e379037af`: no need to give detail on the return policy if the item is not found\
- Note 26, `39c29018745ef39229596313743c2e67`: no need to give product details as the user is asking about refund.
- Note 32, `376a003be2fb346b0a9817dc09a9c9fe`: order id, status, refund details are all unnecessary and confusing details. Ask the user first what they need help with after confirming that their order has been located.
- Note 34, `03293b341bd64bcbd20d10ec41865ae9`: explain why it was not refunded. No detauls are needed except the refund status and why it can not be refunded.
- Note 43, `e75ac79481909be1b048b94f3df5b60b`: too much data - this direct response can be put upfront
- Note 44, `711f10764478d49b30f0fe3a15317649`: unnecessary confirmation
- Note 48, `711f10764478d49b30f0fe3a15317649`: too much information. the real ask is about the store, not the product exactly.
- Note 50, `c7c918336747a818730e6bf1ca3506fc`: order id is unnecessary detail
- Note 55, `e9f48e6de3778a6f7d5356943df48268`: unnecessary data
- Note 61, `9f2ca35491d1cebb8777dd5643bfec5e`: too much information
- Note 65, `af367466feb718768b14045b02bbd7b0`: order id is unnecessary detail
- Note 68, `744d9f6a8a47ae71e1f5821621f06e6e`: order id is unnecessary detail
- Note 73, `e3e7e2776ea3196de7acdca7d450bbc0`: unnecessary action

## `missing_clarification_or_disambiguation`

Definition: The reply proceeds despite ambiguity, asks for an unnecessarily hard identifier, or fails to ask the user to confirm the candidate order/product/action before moving forward.

Boundary: Include notes about asking for product name instead of order ID, confirming a likely match, assumptions, and missing next-step clarification. Exclude extra details after a known target; those belong under unnecessary_detail_overload.

Requirement source: SPEC.md RESP-3: state missing/inconsistent information rather than inventing values; may need a stronger disambiguation rule.

Supporting evidence: 9 notes across 8 traces

- Note 04, `d2fdbbb39bb1aa2c13674d5e379037af`: drop "exact product name" - product name should be enough\
- Note 22, `c8f92db31ccff89e08b51949908df3fe`: use exact product name instead - users do not remember or know the order ids
- Note 23, `c8f92db31ccff89e08b51949908df3fe`: could have confirmed with the user first because user does not seem to remember what they order and when they had order it. After the confirmation, they can cancel/
- Note 32, `376a003be2fb346b0a9817dc09a9c9fe`: order id, status, refund details are all unnecessary and confusing details. Ask the user first what they need help with after confirming that their order has been located.
- Note 45, `711f10764478d49b30f0fe3a15317649`: agent making assumptions and guiding the user through a bumpy road
- Note 58, `6d1fe5cbffc957525774784137281ada`: no clarification made about next steps and help offered to fix the problem
- Note 60, `9f2ca35491d1cebb8777dd5643bfec5e`: making assumptions
- Note 66, `af367466feb718768b14045b02bbd7b0`: could have confirmed with the user first because user does not seem to remember what they order and when they had order it. After the confirmation, they can cancel/
- Note 70, `744d9f6a8a47ae71e1f5821621f06e6e`: should have listed closest match to what user asked and ask them to confirm

## `confusing_or_contradictory_answer`

Definition: The reply contradicts itself, mixes distinct concepts, or leaves the user unclear about the actual status, decision, or reason.

Boundary: Include direct contradiction notes, unclear full-vs-partial refund wording, and mixing refund status with refund eligibility. Exclude too much but otherwise interpretable detail; that belongs under unnecessary_detail_overload.

Requirement source: SPEC.md RESP-5; may need a SPEC revision about separating status, eligibility, reason, and next step.

Supporting evidence: 9 notes across 9 traces

- Note 05, `d2fdbbb39bb1aa2c13674d5e379037af`: contradiction to what was said in the beginning of the conversation
- Note 13, `379b97d2d2ab40d9f88dda2d9da2b217`: confusing message, contradicting with what's asked and answered in other lines.
- Note 27, `39c29018745ef39229596313743c2e67`: explain why it can not be refunded. Unclear message for the shopper\
- Note 35, `03293b341bd64bcbd20d10ec41865ae9`: confusing answer - checking refund status and refund eligibility in the same query is confusing.
- Note 51, `c7c918336747a818730e6bf1ca3506fc`: confusing message - less clear.
- Note 52, `4eb3bf043f6b4d5013a4e0d5fdd0464e`: unclear message - full refund vs partial refund
- Note 57, `6d1fe5cbffc957525774784137281ada`: add additional details why missing product details could be bad
- Note 67, `744d9f6a8a47ae71e1f5821621f06e6e`: confusing message, contradicting with what's asked and answered in other lines.
- Note 82, `2a58d59844efc14cfc1f5a8fb2489d74`: confusing answer - checking refund status and refund eligibility in the same query is confusing.

## `missed_escalation_or_invented_rule`

Definition: The reply should acknowledge uncertainty, route to a human/channel, or avoid making a rule up, but instead leaves the user without the needed handoff or invents authority.

Boundary: Include notes explicitly asking for escalation, a support/merchant channel, or saying the agent should not invent rules. Exclude ordinary missing links.

Requirement source: SPEC.md ESC-3, ESC-4, RESP-3.

Supporting evidence: 2 notes across 2 traces

- Note 64, `9f2ca35491d1cebb8777dd5643bfec5e`: human escalation is needed - the agent is unsure, should not invent rules.
- Note 80, `4d5f7611cdb1aeec2fde1580ed151132`: offer a channel between support and the merchant because it's missing data. Support and Merchant should clarify this.

## Held-out notes, not currently candidate failure modes

These notes are kept so the reasoning remains inspectable, but they should not be mixed into the modes above unless a human decision promotes them.

### `no_failure_observed`

Reviewed trace with no failure observed.

- Note 39, `9ccf8cffd0d78254b85a7a1023980429`: no failures

### `review_infrastructure_or_schema_gap`

Review UI, ground-truth, or schema gaps rather than assistant behavior.

- Note 08, `016e3cc0f7504d6656aa564509d639ec`: ground truth tab does not show the order id
- Note 24, `c8f92db31ccff89e08b51949908df3fe`: we could add a section about "cancel_eligible" so the agent can read the data directly from there
- Note 40, `e75ac79481909be1b048b94f3df5b60b`: can not find order 42 in ground truth data
- Note 62, `9f2ca35491d1cebb8777dd5643bfec5e`: product ids are missing in ground truth data.

### `not_promoted_policy_name_preference`

Preference to omit explicit policy names. This is not the same as missing an actionable reference unless the note also asks for a link/path.

- Note 06, `d2fdbbb39bb1aa2c13674d5e379037af`: no need to call out specific policy name
- Note 10, `fe47fec4e03cf55aa5df32fc9268fb60`: no need to call out specific policy name
- Note 41, `e75ac79481909be1b048b94f3df5b60b`: no need to call out specific policy name
- Note 72, `e3e7e2776ea3196de7acdca7d450bbc0`: no need to call out specific policy name

### `word_choice_tone_issue_needs_more_examples`

Tone/word-choice concern with too little evidence to become a mode yet.

- Note 17, `a8d38a551dce6c17faa55af6d1704108`: "override" is a strong language to use externally.

### `scenario_authorization_context_question`

Scenario/auth-context question that may need separate product guidance before it becomes a failure mode.

- Note 09, `016e3cc0f7504d6656aa564509d639ec`: which shopper id asked for that? We do not know if the shopper is authatorized to check the status.\

## Human decisions needed

- Accept, rename, split, or reject each candidate mode.
- Decide whether link/path expectations should become SPEC revisions before final structured labeling.
- Re-check only the traces whose conversation context was fixed before using them as stable examples.
