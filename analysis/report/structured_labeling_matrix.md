# Structured Labeling Matrix Draft

This file summarizes the structured labeling pass over the 100 reviewed traces. Each final mode has one present/absent judgment per trace. These labels are seeded from the saved human open-code annotations and axial-coding drafts; they should be treated as a reviewable draft, not an independent second human pass.

- Reviewed traces: 100
- Final modes: 7
- Label judgments: 700
- Label source: human open-code notes mapped through axial coding, with two approved mode merges

## Failure counts by mode

- `unhandled_data_quality_or_record_inconsistency`: 12 / 100
- `missing_actionable_next_step`: 52 / 100
- `identifier_heavy_or_missing_item_context`: 17 / 100
- `unnecessary_detail_overload`: 31 / 100
- `missing_clarification_or_disambiguation`: 25 / 100
- `confusing_or_unsupported_answer`: 24 / 100
- `presentation_formatting_noise`: 48 / 100

## Files

- `analysis/state/structured_labels_matrix.csv`
- `analysis/state/structured_labels_matrix.json`
- `analysis/state/final_taxonomy.json`
- `analysis/state/patterns.json`
- `analysis/state/labels/<mode>.jsonl` for each final mode

## Interpretation note

A `Pass` means no saved annotation mapped to that mode for the trace. Because the open-coding pass stopped at the first failure by design, these draft labels may undercount additional late-occurring modes. The matrix is the right artifact to audit next before using the labels for prevalence or judge development.
