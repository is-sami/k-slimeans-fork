#!/usr/bin/env python
"""Size differences and the minimum detectable paired difference at 5 seeds (#36), from committed numbers only.

Reads, from `--results-dir` (default `docs/results`): `prompt_test_paired.csv` (CLINC150, October and clearer
prompt), `prelim_bank77_per_seed.csv` (BANKING77, paired here with `aggregate.paired_differences`),
`bbc_tfidf_paired.csv` and `bbc_dense_paired.csv`. Writes `size_result_table.csv` there. No run directory is needed.

Usage:

    python scripts/size_result.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from kslimeans.aggregate import paired_differences
from kslimeans.size_result import method_name, size_table

BANK77_REFERENCES = [method_name(s, "old") for s in ("0.6B", "1.7B")]


def build(results_dir: Path) -> pd.DataFrame:
    """All size rows: CLINC150 old and v2, BANKING77, BBC TF-IDF and dense."""
    prompt_test = pd.read_csv(results_dir / "prompt_test_paired.csv")
    bank = paired_differences(pd.read_csv(results_dir / "prelim_bank77_per_seed.csv"), BANK77_REFERENCES)
    parts = [
        size_table(prompt_test, "CLINC150", "old"),
        size_table(prompt_test, "CLINC150", "v2"),
        size_table(bank, "BANKING77", "old"),
        size_table(pd.read_csv(results_dir / "bbc_tfidf_paired.csv"), "BBC TF-IDF", "old"),
        size_table(pd.read_csv(results_dir / "bbc_dense_paired.csv"), "BBC dense", "old"),
    ]
    return pd.concat(parts, ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--results-dir", type=Path, default=Path("docs/results"))
    args = parser.parse_args()
    table = build(args.results_dir)
    out = args.results_dir / "size_result_table.csv"
    table.to_csv(out, index=False, float_format="%.6f")
    print(f"wrote {out} ({len(table)} rows)")


if __name__ == "__main__":
    main()
