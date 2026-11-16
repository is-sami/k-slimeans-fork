"""Same model, two prompts (issue #50): the old-prompt and the clearer-prompt Qwen3-4B on the same clusters at step 1.

Both runs start from the same step-0 partitions, so cluster `c` of seed `s` has the same members in each. Reads the joined
per-cluster CSV that `scripts/synthesis.py` writes and prints / writes, per subset of clusters, the per-seed means of
summary properties and outcomes for both runs and their paired difference with a 95% t-interval over seeds.

    python scripts/synthesis_prompt_contrast.py results/synthesis/synthesis_per_cluster.csv \\
        --out docs/results/synthesis_prompt_contrast.csv
"""

from __future__ import annotations

import argparse

import pandas as pd

from kslimeans import synthesis as syn

DATASET = "clinc150_intent"
OLD, NEW = "k-SLMmeans (Qwen3-4B)", "k-SLMmeans-v2 (Qwen3-4B)"
COLUMNS = ["flag_duplicate", "flag_mentions", "flag_generic", "flag_low_coverage", "flag_unsupported", "flu_copy", "flu_no_question",
           "flag_not_fluent", "coverage_nearest", "specificity_margin", "unsupported_lemma_share", "empty_replacement", "drift", "cosine",
           "lost_share", "d_member_purity", "helped", "harmed"]  # fmt: skip
SUBSETS = {
    "all clusters": lambda a: a["purity"] >= 0,
    "generic in the old run": lambda a: a["flag_generic"] == 1,
    "not generic in the old run": lambda a: a["flag_generic"] == 0,
    "purity before <= 0.4": lambda a: a["purity"] <= 0.4,
    "purity before (0.4, 0.8]": lambda a: (a["purity"] > 0.4) & (a["purity"] <= 0.8),
    "purity before > 0.8": lambda a: a["purity"] > 0.8,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("joined_csv")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    df = pd.read_csv(args.joined_csv, low_memory=False)
    df = df[df["dataset"] == DATASET]
    table = syn.paired_contrast(df, OLD, NEW, COLUMNS, SUBSETS)
    table.to_csv(args.out, index=False, float_format="%.6g")
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
