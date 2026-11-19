"""Size differences between the Qwen3 summarizers, with the smallest paired difference five seeds can detect (#36).

`size_table` takes paired per-seed differences (the `aggregate.paired_differences` layout) and keeps the three
size pairs (1.7B minus 0.6B, 4B minus 0.6B, 4B minus 1.7B) for each metric. Each row carries the observed mean,
the 95% Student-t interval, seeds won, the standard deviation of the paired difference over seeds, and the
minimum detectable paired difference (`min_detectable`) at that spread.

`min_detectable` is the usual normal-theory approximation for a paired t-test, with the t quantile in place of the
normal one: (t(1 - alpha/2, n - 1) + t(power, n - 1)) * sd / sqrt(n). `min_detectable_exact` solves the same
question with the noncentral t distribution, as a check. Both take the sample standard deviation of the observed
paired differences as if it were the true one, which with 5 seeds is itself a loose estimate.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import optimize, stats

SIZE_PAIRS = (("1.7B", "0.6B"), ("4B", "0.6B"), ("4B", "1.7B"))
METRICS = ("acc", "nmi", "ari")
COLUMNS = [
    "dataset", "prompt", "larger", "smaller", "metric", "n", "mean_diff", "ci_low", "ci_high", "wins", "ties", "sd",
    "min_detectable", "min_detectable_exact", "below_min_detectable", "ci_excludes_zero",
]  # fmt: skip


def min_detectable(sd: float, n: int, alpha: float = 0.05, power: float = 0.8) -> float:
    """Smallest true mean paired difference a two-sided paired t-test detects with the given power (central-t approximation)."""
    if n < 2 or not np.isfinite(sd):
        return float("nan")
    df = n - 1
    return float((stats.t.ppf(1 - alpha / 2, df) + stats.t.ppf(power, df)) * sd / np.sqrt(n))


def min_detectable_exact(sd: float, n: int, alpha: float = 0.05, power: float = 0.8) -> float:
    """As `min_detectable`, but the noncentrality that gives the power comes from the noncentral t distribution.

    Needs n >= 3 (NaN below that: with 1 df the search bracket does not reach the power). Only the upper rejection
    region is counted; the other one adds about 1.4e-7 at the noncentrality that gives 80% power with 4 df, and
    scipy's lower tail is unstable at large noncentralities.
    """
    if n < 3 or not np.isfinite(sd):
        return float("nan")
    df = n - 1
    crit = stats.t.ppf(1 - alpha / 2, df)
    ncp = optimize.brentq(lambda x: stats.nct.sf(crit, df, x) - power, 0.5, 8.0)
    return float(ncp * sd / np.sqrt(n))


def method_name(size: str, prompt: str) -> str:
    """The label `aggregate.method_label` gives a Qwen3 run: 'k-SLMmeans (Qwen3-4B)', or 'k-SLMmeans-v2 (Qwen3-4B)'."""
    return f"k-SLMmeans{'-v2' if prompt == 'v2' else ''} (Qwen3-{size})"


def size_table(paired: pd.DataFrame, dataset: str, prompt: str, alpha: float = 0.05, power: float = 0.8) -> pd.DataFrame:
    """The size-pair rows of one dataset and prompt from a paired-differences frame (larger minus smaller)."""
    rows = []
    for larger, smaller in SIZE_PAIRS:
        sel = paired[(paired["reference"] == method_name(smaller, prompt)) & (paired["method"] == method_name(larger, prompt))]
        for metric in METRICS:
            hit = sel[sel["metric"] == metric]
            if len(hit) != 1:
                raise ValueError(f"{dataset}/{prompt}: expected one row for {larger} minus {smaller} on {metric}, got {len(hit)}")
            r = hit.iloc[0]
            mdd = min_detectable(r["sd"], int(r["n"]), alpha, power)
            rows.append(
                {
                    "dataset": dataset, "prompt": prompt, "larger": larger, "smaller": smaller, "metric": metric,
                    "n": int(r["n"]), "mean_diff": r["mean_diff"], "ci_low": r["ci_low"], "ci_high": r["ci_high"],
                    "wins": int(r["wins"]), "ties": int(r["ties"]), "sd": r["sd"], "min_detectable": mdd,
                    "min_detectable_exact": min_detectable_exact(r["sd"], int(r["n"]), alpha, power),
                    "below_min_detectable": bool(abs(r["mean_diff"]) < mdd),
                    "ci_excludes_zero": bool(r["ci_low"] > 0 or r["ci_high"] < 0),
                }
            )  # fmt: skip
    return pd.DataFrame(rows, columns=COLUMNS)
