#!/usr/bin/env python
"""Cost table, cost per unit of benefit and the ACC-against-seconds figure (#82).

Reads the logged runs of CLINC150 (October and v2 prompts), BANKING77 (#20), BBC TF-IDF and dense (#18) and
the arXiv 200k pilot and LSA (#48, seed 0) from `--results` (the checkout that holds `results/`; the runs
are not in git), and writes, into `--out-dir`:

- `cost_justification_table.csv`: one row per (dataset, method[, prompt]) with every column;
- `cost_justification_table.md`: the cost, benefit and cost-per-benefit tables of every dataset;
- `cost_justification_pareto.png`: ACC against summarizer seconds (log), one panel per dataset.

Dollar columns need `--prices` (CSV with `item,unit,usd,source,checked`; see `kslimeans.cost_table`); without
it they are empty, pending #10. CONFIRM(#10): the price items follow this script's convention until
`docs/cost_assumptions.md` exists.

Usage:

    python scripts/cost_table.py --results /path/to/checkout --out-dir docs/results
    python scripts/cost_table.py --results /path/to/checkout --prices prices.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from kslimeans.cost_table import DATASETS, collect, flat_csv, load_prices, render_all, resolve_results_root, short_name

KMEANS_COLOR = "#666666"
FAMILY_COLOR = {"lsa": "#1b9e77", "0.6B": "#d95f02", "1.7B": "#7570b3", "4B": "#e7298a"}


def plot_pareto(frames: dict[str, pd.DataFrame], titles: dict[str, str], path: Path) -> None:
    """ACC (mean ± sd over seeds) against seconds, log x, one panel per dataset; k-means is a dashed horizontal line.

    Filled markers: October / dataset prompt; open markers: v2 prompt; square: LSA. The x axis is the logged
    summarizer seconds where the run has them, else the logged seconds of the whole method (`seconds_basis`).
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(frames)
    fig, axes = plt.subplots(2, 3, figsize=(17, 9), constrained_layout=True)
    flat = axes.ravel()
    for ax, (key, frame) in zip(flat, frames.items()):
        for _, r in frame.iterrows():
            if r["family"] == "kmeans":
                ax.axhline(r["acc_mean"], color=KMEANS_COLOR, linestyle="--", linewidth=1, label="k-means")
                continue
            color = FAMILY_COLOR["lsa" if r["family"] == "lsa" else r["model"]]
            v2 = r["family"] == "slm" and r["prompt"].startswith("v2")
            ax.errorbar(
                r["seconds"], r["acc_mean"], yerr=None if pd.isna(r["acc_sd"]) else r["acc_sd"], color=color,
                marker="s" if r["family"] == "lsa" else "o", markerfacecolor="white" if v2 else color,
                elinewidth=1, capsize=2, linestyle="none",
            )  # fmt: skip
            ax.annotate(
                short_name(r) + (f" [{r['timing_code']}]" if r["timing_code"] in "BCDE" else ""), (r["seconds"], r["acc_mean"]), textcoords="offset points", xytext=(-7, -12) if v2 else (6, 5),
                ha="right" if v2 else "left", fontsize=8, color=color,
            )  # fmt: skip
        ax.set_xscale("log")
        basis = frame["seconds_basis"].iloc[0]
        ax.set_xlabel("summarizer seconds per seed" if basis == "summarizer" else "seconds of the whole method (summarizer seconds not logged)")
        ax.set_ylabel("ACC")
        ax.set_title(titles[key], fontsize=10)
        ax.grid(alpha=0.3)
    for ax in flat[n:]:
        ax.axis("off")
    note = flat[-1]
    note.text(
        0, 0.9,
        "Mean ACC ± sd over seeds (5 seeds; arXiv: 1 seed). The bars\nare across-seed sd, not the paired interval of the gate.\nDashed line: k-means.  Square: LSA.\n"
        "Filled: October / dataset prompt.  Open: v2 prompt.\n\n"
        "Seconds are as logged: the CLINC150 October-prompt\nruns were not idle-checked (step 1 of seed 0 was\n"
        "1.76 / 1.72 / 1.15 times slower than on an idle card\nfor 0.6B / 1.7B / 4B; whole-run inflation not\nmeasured); the v2 1.7B run is not clean.\n"
        "[B] [C] [D] [E]: timing inflated or not clean (timing\ncodes in cost_justification.md).\n"
        "Batch sizes: CLINC150 and BBC 8 / 4 / 1,\nBANKING77 8 / 4 / 2, arXiv 4.",
        va="top", fontsize=9, transform=note.transAxes,
    )  # fmt: skip
    handles = [plt.Line2D([], [], color=c, marker="o", linestyle="none", label=k.upper() if k == "lsa" else k) for k, c in FAMILY_COLOR.items()]
    note.legend(handles=handles, loc="lower left", fontsize=9, title="summarizer")
    fig.suptitle("ACC against summarizer seconds, by dataset (cost: #35 timings and caveats, #82)")
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--results", default=".", help="the checkout that holds results/, or that results/ directory (default: the current directory)"
    )
    parser.add_argument("--out-dir", default="docs/results", help="where the CSV, markdown and figure go (default: %(default)s)")
    parser.add_argument("--prices", help="CSV of item,unit,usd,source,checked rows (#10); without it the dollar columns are empty")
    args = parser.parse_args()

    prices = load_prices(args.prices)
    root = resolve_results_root(args.results)
    frames = {spec.key: collect(spec, root, prices) for spec in DATASETS}
    specs = {spec.key: spec for spec in DATASETS}
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    flat_csv(frames).to_csv(out / "cost_justification_table.csv", index=False)
    (out / "cost_justification_table.md").write_text(render_all(frames, specs, prices))
    plot_pareto(frames, {k: s.title for k, s in specs.items()}, out / "cost_justification_pareto.png")
    print(f"wrote {out}/cost_justification_table.csv, .md and cost_justification_pareto.png")


if __name__ == "__main__":
    main()
