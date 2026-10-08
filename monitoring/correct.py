"""Bias-corrected prevalence, applied on a monitoring schedule.

A judge's raw flag rate on the sample is biased by the judge's own error
rates: a judge with TPR 0.83 and TNR 0.95 both misses real failures and
flags clean traces. Module 2.5 introduced the Rogan-Gladen correction;
monitoring applies the same calculation on a cadence over the
live sample, using the frozen judge's TEST-split labels and predictions
(its measured TPR and TNR) exactly as Module 2 measured them.
"""

from __future__ import annotations

from typing import Any, Sequence


def corrected_mode_prevalence(
    sample_preds: Sequence[int],
    test_labels: Sequence[int],
    test_preds: Sequence[int],
    confidence: float = 0.95,
    bootstrap_iterations: int = 20000,
    seed: int | None = 7,
) -> dict[str, Any]:
    """Bias-corrected live prevalence for one mode from sampled verdicts.

    The contract, precisely:

      1. ``raw`` is the uncorrected flag rate: ``mean(sample_preds)``.
      2. Compute the frozen judge's TPR and TNR from ``test_labels`` and
         ``test_preds`` (failure-positive convention: 1 = failure present).
         TPR is the flagged fraction of true failures; TNR is the unflagged
         fraction of true passes.
      3. Compute the Rogan-Gladen point estimate, then resample the held-out
         records and sampled predictions to obtain a percentile-bootstrap
         interval. Use a seeded NumPy generator so the committed result is
         reproducible.
      4. ``validity_warning`` is a non-empty string when ``tpr + tnr <=
         1.05``: the correction divides by (TPR + TNR - 1), so a judge near
         that boundary produces an unstable estimate nobody should act on.
         Otherwise it is "". A judge with TPR + TNR <= 1 is no better than
         chance; the warning covers the sliver just
         above that, where the math works but the number is not actionable.)

    Args:
        sample_preds: the judge's 0/1 verdicts over the UNIFORM BASE sample
            only (never the risk strata; they are biased toward failure by
            design).
        test_labels: human labels for the judge's test split (from the
            frozen Module 2 judge).
        test_preds: the frozen judge's predictions on that test split.
        confidence: interval confidence level.
        bootstrap_iterations: number of percentile-bootstrap replicates.
        seed: numpy seed for a reproducible interval; None leaves the RNG
            untouched.

    Returns:
        {"raw", "corrected", "ci_low", "ci_high", "confidence",
         "test_tpr", "test_tnr", "n_sample", "validity_warning"}
        with "corrected" clamped to [0, 1] and rates rounded to 4 places.

    Raises:
        ValueError: if sample_preds or test_labels is empty.
    """
    import numpy as np

    if not sample_preds:
        raise ValueError("sample_preds must not be empty")
    if not test_labels:
        raise ValueError("test_labels must not be empty")
    if len(test_labels) != len(test_preds):
        raise ValueError("test_labels and test_preds must have the same length")

    sample = np.asarray(sample_preds, dtype=int)
    labels = np.asarray(test_labels, dtype=int)
    preds = np.asarray(test_preds, dtype=int)

    def _rates(label_arr: np.ndarray, pred_arr: np.ndarray) -> tuple[float, float]:
        positives = label_arr == 1
        negatives = label_arr == 0
        if not positives.any() or not negatives.any():
            raise ValueError("test data must contain both failures and passes")
        tpr_value = float((pred_arr[positives] == 1).mean())
        tnr_value = float((pred_arr[negatives] == 0).mean())
        return tpr_value, tnr_value

    def _correct(raw_rate: float, tpr_value: float, tnr_value: float) -> float:
        denominator = tpr_value + tnr_value - 1.0
        if denominator <= 0:
            return float("nan")
        return min(1.0, max(0.0, (raw_rate + tnr_value - 1.0) / denominator))

    raw = float(sample.mean())
    tpr, tnr = _rates(labels, preds)
    corrected = _correct(raw, tpr, tnr)

    rng = np.random.default_rng(seed)
    boot: list[float] = []
    sample_n = len(sample)
    test_n = len(labels)
    for _ in range(bootstrap_iterations):
        sample_idx = rng.integers(0, sample_n, sample_n)
        test_idx = rng.integers(0, test_n, test_n)
        boot_raw = float(sample[sample_idx].mean())
        try:
            boot_tpr, boot_tnr = _rates(labels[test_idx], preds[test_idx])
        except ValueError:
            continue
        boot_corrected = _correct(boot_raw, boot_tpr, boot_tnr)
        if not np.isnan(boot_corrected):
            boot.append(boot_corrected)

    alpha = 1.0 - confidence
    if boot:
        ci_low, ci_high = np.quantile(boot, [alpha / 2.0, 1.0 - alpha / 2.0])
    else:
        ci_low = ci_high = corrected

    warning = ""
    if tpr + tnr <= 1.05:
        warning = "judge calibration is close to chance; corrected prevalence is unstable"

    return {
        "raw": round(raw, 4),
        "corrected": round(corrected, 4),
        "ci_low": round(float(ci_low), 4),
        "ci_high": round(float(ci_high), 4),
        "confidence": confidence,
        "test_tpr": round(tpr, 4),
        "test_tnr": round(tnr, 4),
        "n_sample": int(sample_n),
        "validity_warning": warning,
    }
