"""Agreement between the hand ratings of the summary audit and the automatic flags (issue #34).

Reads a filled `summary_audit_sheet_<dataset>.csv` and its `summary_audit_key_<dataset>.csv` (which stores the
automatic flags of the same summaries; made by `make_audit_sheet.py --write-key`, not kept in the repo) and prints, per property, the 2 x 2 table, the raw agreement and Cohen's
kappa. One rater. Empty rating cells are dropped. The hand labels and their rules are in
`docs/summary_audit_rubric.md`.

    python scripts/audit_agreement.py docs/results/summary_audit_sheet_clinc150_intent.csv \\
        results/audit_keys/summary_audit_key_clinc150_intent.csv
"""

from __future__ import annotations

import argparse

import pandas as pd

from kslimeans.summary_audit import agreement_markdown, compare_with_key

compare = compare_with_key
to_markdown = agreement_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sheet", help="the filled sheet CSV")
    parser.add_argument("key", help="the matching key CSV")
    args = parser.parse_args()
    print(to_markdown(compare(pd.read_csv(args.sheet), pd.read_csv(args.key))))


if __name__ == "__main__":
    main()
