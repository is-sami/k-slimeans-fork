#!/usr/bin/env python
"""The chain from summary quality to the final score, and the readable-but-poor summaries (issue #50, sections 11 and 12).

Reads the joined per-cluster CSV that `scripts/synthesis.py` writes (CLINC150, step 1) and #33's committed step and outcome
tables, and writes two long-format CSVs:

- `synthesis_chain.csv`: links 1 to 4 of the chain (rank correlations per method with an interval over seeds, and the
  step-1 to final pairs across methods);
- `synthesis_readable.csv`: among fluent summaries, the share that is a poor representative and what happened to the
  members of those clusters against the fluent ones that are not.

    python scripts/synthesis_chain.py results/synthesis/synthesis_per_cluster.csv --out-dir docs/results
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from kslimeans import synthesis as syn
from kslimeans import synthesis_chain as chain

DATASET = "clinc150_intent"
CONTROLS = ["purity", "log_n_members"]
QUALITY = ["coverage_nearest", "specificity_margin", "unsupported_lemma_share"]
MOVEMENT = ["drift", "own_nearest"]
CHANGES = ["lost_share", "gained_share"]
PURITY_CHANGE = ["d_member_purity", "d_member_purity_vs_cf"]
READABLE_OUTCOMES = ["lost_share", "d_member_purity", "d_member_purity_vs_cf", "d_member_purity_vs_null"]


def correlation_rows(link: str, table: pd.DataFrame) -> pd.DataFrame:
    table = table.rename(columns={"method_id": "method", "property": "x", "outcome": "y", "rho": "estimate"})
    table["link"], table["scope"], table["statistic"] = link, "step 1", "spearman, mean over seeds"
    if "stratum" not in table:
        table["stratum"] = "all"
    return table[["link", "scope", "method", "stratum", "x", "y", "controls", "statistic", "estimate", "lo", "hi", "n_seeds", "n_clusters"]]


def build_chain(step1: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for controls in (None, CONTROLS):
        parts.append(correlation_rows("1 quality to movement", syn.correlation_table(step1, QUALITY, MOVEMENT, controls)))
        parts.append(correlation_rows("2 movement to assignment changes", syn.correlation_table(step1, MOVEMENT, CHANGES, controls)))
        parts.append(correlation_rows("1b quality to purity change", syn.correlation_table(step1, QUALITY + MOVEMENT, PURITY_CHANGE, controls)))
    parts.append(correlation_rows("3 assignment changes to purity change", syn.correlation_table(step1, CHANGES, PURITY_CHANGE, CONTROLS)))
    parts.append(correlation_rows("3 assignment changes to purity change", syn.correlation_table(step1, CHANGES, PURITY_CHANGE, None)))
    by_purity = chain.correlations_by_stratum(syn.add_bins(step1), "bin_purity", ["lost_share"], ["d_member_purity_vs_cf"], ["log_n_members"])
    parts.append(correlation_rows("3 assignment changes to purity change", by_purity))
    rows = pd.concat(parts, ignore_index=True)

    pair_stats = chain.pair_correlations(pairs).rename(columns={"rho": "estimate", "n": "n_clusters"})
    pair_stats = pair_stats.assign(link="4 step-1 partition to final score", method="all five runs", stratum=pair_stats["scope"],
                                   x="d_step_acc", y="d_final_acc", controls="none", statistic="spearman over (run, seed) pairs")  # fmt: skip
    pair_stats["scope"] = "step 1 to final"
    means = chain.method_means(pairs)
    mean_rows = pd.concat(
        [means.assign(x="d_step_acc", y="d_final_acc", estimate=means["d_step_acc"], statistic="mean over seeds"),
         means.assign(x="d_final_acc", y="d_final_acc", estimate=means["d_final_acc"], statistic="mean over seeds")],
        ignore_index=True,
    ).rename(columns={"run": "method"})  # fmt: skip
    mean_rows = mean_rows.assign(link="4 step-1 partition to final score", scope="step 1 to final", stratum="method mean", controls="none",
                                 lo=float("nan"), hi=float("nan"), n_clusters=mean_rows["n_seeds"])  # fmt: skip
    cols = list(rows.columns)
    return pd.concat([rows, pair_stats[cols], mean_rows[cols]], ignore_index=True)


def build_readable(step1: pd.DataFrame) -> pd.DataFrame:
    shares = chain.readable_shares(step1).assign(kind="share", scope="step 1")
    with_outcomes = syn.add_bins(step1[step1["has_diag"]])
    contrasts = [chain.readable_contrast(with_outcomes, READABLE_OUTCOMES), chain.readable_contrast(with_outcomes, READABLE_OUTCOMES, ["bin_purity"])]
    return pd.concat([shares, pd.concat(contrasts, ignore_index=True).assign(kind="contrast", scope="step 1")], ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("joined_csv")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--steps", default="docs/results/replacement_diagnostic_steps.csv")
    parser.add_argument("--outcome", default="docs/results/replacement_diagnostic_outcome.csv")
    args = parser.parse_args()

    df = syn.add_derived(pd.read_csv(args.joined_csv, low_memory=False))
    df = df[df["dataset"] == DATASET]
    step1 = df[df["step1"]]
    with_diag = step1[step1["has_diag"]]

    steps = pd.read_csv(args.steps)
    outcome = pd.read_csv(args.outcome)
    kmeans = outcome.groupby("seed")["kmeans_acc"].agg(["first", "nunique"])
    assert (kmeans["nunique"] == 1).all(), "k-means ACC differs between runs of one seed"
    final = df.drop_duplicates(["run_config", "seed"])[["run_config", "seed", "final_acc"]].rename(columns={"run_config": "run"})
    pairs = chain.step_final_pairs(steps, final, kmeans["first"])

    out = Path(args.out_dir)
    table = build_chain(with_diag, pairs)
    table.to_csv(out / "synthesis_chain.csv", index=False, float_format="%.6g")
    readable = build_readable(step1)
    readable.to_csv(out / "synthesis_readable.csv", index=False, float_format="%.6g")
    print(chain.pair_correlations(pairs).to_string(index=False))
    print(chain.method_means(pairs).to_string(index=False))
    print(readable[readable["kind"] == "share"].dropna(axis=1, how="all").to_string(index=False))


if __name__ == "__main__":
    main()
