#!/usr/bin/env python
"""Worked examples of readable summaries that are poor representatives (issue #50, section 12), chosen by a rule.

Rule (no hand-picking). In one run at one seed and its first summary step, among the clusters whose summary passes every
fluency proxy and is a poor representative (low coverage or generic, `kslimeans.synthesis_chain.readable_flags`) and that
have at least `--min-members` members, take the one whose members' purity fell the most against the no-replacement
counterfactual (`worst`) and the one where it rose the most (`best`). For each print the summary, its scores, the gold
intents of the members, where the lost members went (the majority intent of the destination clusters) and the purity
before and after. CPU only; the run's embeddings come from the cache.

    python scripts/synthesis_chain_examples.py RUN_DIR results/synthesis/synthesis_per_cluster.csv \\
        --cache-dir ../k-slimeans/cache --seed 0
"""

from __future__ import annotations

import argparse
from collections import Counter

import numpy as np
import pandas as pd

from kslimeans import synthesis as syn
from kslimeans import synthesis_chain as chain
from kslimeans.runlog import load_run, load_run_dataset


def pick(df: pd.DataFrame, run_config: str, seed: int, min_members: int) -> dict[str, pd.Series]:
    """The `worst` and `best` rows by `d_member_purity_vs_cf` among the fluent poor representatives of step 1."""
    rows = chain.readable_flags(df)
    rows = rows[(rows["run_config"] == run_config) & (rows["seed"] == seed) & (rows["step"] == 1) & (rows["poor_among_fluent"] == 1.0)
                & (rows["n_members"] >= min_members)].dropna(subset=["d_member_purity_vs_cf"])  # fmt: skip
    ordered = rows.sort_values(["d_member_purity_vs_cf", "cluster"])
    return {"worst": ordered.iloc[0], "best": ordered.sort_values(["d_member_purity_vs_cf", "cluster"], ascending=[False, True]).iloc[0]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dir")
    parser.add_argument("joined_csv")
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--min-members", type=int, default=50)
    args = parser.parse_args()

    runlog = load_run(args.run_dir)
    config = runlog.config["name"]
    df = syn.add_derived(pd.read_csv(args.joined_csv, low_memory=False))
    chosen = pick(df[df["dataset"] == "clinc150_intent"], config, args.seed, args.min_members)
    ds, _ = load_run_dataset(runlog, cache_dir=args.cache_dir)
    method = next(m for m in runlog.methods if m != "kmeans")
    record = runlog.record(method, args.seed)
    src, after = record.source_partition(0), record.partition_after(0)  # #34 numbers the first summary step 0
    names = lambda ids: Counter(ds.label_names[g] for g in ds.labels[ids]).most_common(4)  # noqa: E731
    for kind, row in chosen.items():
        c = int(row["cluster"])
        members = np.flatnonzero(src == c)
        assert len(members) == int(row["n_members"]), "the logged partition does not match the joined row"
        print(f"\n== {kind}: {config} seed {args.seed} step 1 cluster {c}: {row['summary']!r}")
        print(f"members {len(members)}; purity before {row['purity']:.3f}; nearest-summary share {row['coverage_nearest']:.2f}; intent coverage "
              f"{row['coverage_intents']:.2f}; margin {row['specificity_margin']:.3f}; generic={int(row['flag_generic'])} "
              f"unsupported={int(row['flag_unsupported'])}")
        print(f"lost share {row['lost_share']:.3f}; member-purity change {row['d_member_purity']:+.3f}; "
              f"minus the counterfactual {row['d_member_purity_vs_cf']:+.3f}")
        print("gold intents of the members:", names(members))
        lost = members[after[members] != c]
        stayed = members[after[members] == c]
        print("kept:", len(stayed), names(stayed), "| lost:", len(lost), names(lost))
        dest = Counter(after[lost].tolist()).most_common(3)
        for cluster, n in dest:
            print(f"  {n} went to cluster {cluster}, whose members (source) are mostly", names(np.flatnonzero(src == cluster))[:2])


if __name__ == "__main__":
    main()
