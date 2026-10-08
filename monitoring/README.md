# Homework 7 monitoring summary

The monitor tracks `unsupported_policy_claim-v3` using the frozen Homework 5 judge. The random sample is the only source used for the failure-rate estimate; risk groups are kept separate because they are intentionally enriched for suspicious traces.

## Did the corrected failure estimate move between the two periods?

No. The random sample raw rate was 1 failure in 10 sampled conversations in both periods. After correcting for the judge's measured test performance, both periods have the same corrected estimate: `0.0607`.

## Do the intervals support a conclusion, or is the result uncertain?

The result is uncertain. Both periods have a 95% interval of `[0.0, 0.36]`, which is wide because each period uses only 10 random-sample conversations. The point estimate is below the configured threshold of `0.15`, but the interval is too wide to conclude that the monitored failure is safely below the threshold.

## What did the risk groups reveal that the random estimate did not?

The risk groups surfaced a targeted after-period issue that the random estimate does not represent as prevalence. The `above_threshold_refund` group had 1 flagged trace out of 1 selected trace in the after period, while the before period had no selected traces for that group. The `override_policy_question` group had no flagged traces in either period.

## What action should happen if the estimate crosses the threshold?

A threshold crossing should trigger error analysis on the flagged traces. Confirmed failures should be added back into the Homework 6 evaluation suite as new regression or capability cases, depending on whether the behavior is expected to be reliable already or is still an emerging capability.
