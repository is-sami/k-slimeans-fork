#!/usr/bin/env python
"""Numeric check of the objective identity behind the replacement (issue #81, `replacement_diagnostic.md` section 3).

For a fixed assignment C of the data X to k clusters with means x̄_k and sizes n_k, and any centers Z,

    J(C, Z) = sum_i ||x_i - z_{c_i}||^2 = J(C, X̄) + sum_k n_k ||z_k - x̄_k||^2,

where J(C, X̄) is the objective at the means. Hence, for the pre-replacement centers M and the summary embeddings S,

    J(C, S) - J(C, M) = sum_k n_k (||s_k - x̄_k||^2 - ||m_k - x̄_k||^2),

and when M are the means (up to the block's convergence tolerance) this is about sum_k n_k ||s_k - x̄_k||^2.
Empty clusters (n_k = 0) add nothing to either side.

For every step-1 replay the logged runs allow (the four #31 CLINC150 runs and the v2 4B, seeds 0-4) this script
replays the exact step-0 fit (the pre-replacement partition C and centers M, which the logs do not hold; checked
against the logged step-0 labels) and reports, from C, M, the logged summaries' embeddings S and the data X:

    a  J(C, S) - J(C, M)
    b  sum_k n_k (||s_k - x̄_k||^2 - ||m_k - x̄_k||^2)         (a and b agree to float precision)
    c  sum_k n_k ||m_k - x̄_k||^2                              (how far M is from the means)
    d  sum_k n_k ||s_k - x̄_k||^2                              (the size-weighted squared centroid movement)

and the logged "old assignment" minus "before" objectives of `replacement_diagnostic_steps.csv` (the same quantity as a).

No language model, no encoding of summaries (the embeddings come from `scripts/embed_logged_summaries.py`), CPU only.

Usage:

    CUDA_VISIBLE_DEVICES="" python scripts/check_objective_identity.py RUN_DIR... --cache-dir cache \\
        --summary-embeddings results/replacement_diagnostic/summary_embeddings_cuda.npz \\
            results/v2_embed/summary_embeddings_cuda_v2_4b.npz \\
        --steps-csv docs/results/replacement_diagnostic_steps.csv --out docs/results/replacement_objective_identity.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from kslimeans.replay import SummaryEmbeddings, fit_initial
from kslimeans.runlog import load_run, load_run_dataset


def cluster_means(X: np.ndarray, labels: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Cluster sizes `n_k` and means `x̄_k` in float64. An empty cluster has size 0 and a zero mean (never used)."""
    X = np.asarray(X, dtype=np.float64)
    sizes = np.bincount(labels, minlength=k).astype(np.float64)
    sums = np.zeros((k, X.shape[1]))
    np.add.at(sums, labels, X)
    means = np.divide(sums, sizes[:, None], out=np.zeros_like(sums), where=sizes[:, None] > 0)
    return sizes, means


def assignment_objective(X: np.ndarray, labels: np.ndarray, centers: np.ndarray) -> float:
    """`J(C, Z) = sum_i ||x_i - z_{c_i}||^2` for the fixed assignment `labels` (no re-assignment), in float64."""
    diff = np.asarray(X, dtype=np.float64) - np.asarray(centers, dtype=np.float64)[labels]
    return float(np.sum(diff**2))


def weighted_gap(sizes: np.ndarray, means: np.ndarray, centers: np.ndarray) -> float:
    """`sum_k n_k ||z_k - x̄_k||^2`; empty clusters (n_k = 0) contribute nothing."""
    return float(np.sum(sizes * np.sum((np.asarray(centers, dtype=np.float64) - means) ** 2, axis=1)))


def objective_identity(X: np.ndarray, labels: np.ndarray, M: np.ndarray, S: np.ndarray) -> dict:
    """Both sides of the identity for the assignment `labels`, old centers `M` and new centers `S`.

    Returns `lhs` (J(C, S) - J(C, M)), `rhs` (sum_k n_k (||s_k - x̄_k||^2 - ||m_k - x̄_k||^2)), their absolute and
    relative residual, `center_gap` (sum_k n_k ||m_k - x̄_k||^2), `summary_gap` (sum_k n_k ||s_k - x̄_k||^2), and
    `j_before` = J(C, M) and `j_old` = J(C, S).
    """
    k = len(M)
    sizes, means = cluster_means(X, labels, k)
    j_before, j_old = assignment_objective(X, labels, M), assignment_objective(X, labels, S)
    center_gap, summary_gap = weighted_gap(sizes, means, M), weighted_gap(sizes, means, S)
    lhs, rhs = j_old - j_before, summary_gap - center_gap
    return {
        "n_empty_pre": int(np.sum(sizes == 0)),
        "j_before": j_before,
        "j_old": j_old,
        "lhs": lhs,
        "rhs": rhs,
        "abs_resid": abs(lhs - rhs),
        "rel_resid": abs(lhs - rhs) / abs(lhs) if lhs else abs(lhs - rhs),
        "center_gap": center_gap,
        "center_gap_rel": center_gap / j_before if j_before else 0.0,
        "summary_gap": summary_gap,
    }


def check_run(run_dir: str, emb: SummaryEmbeddings, cache_dir: str, steps: pd.DataFrame | None) -> list[dict]:
    """One row per (method, seed) of `run_dir`: the identity at summary step 1, and the logged objectives."""
    log = load_run(run_dir)
    run = log.config["name"]
    _, X = load_run_dataset(log, cache_dir=cache_dir)
    rows = []
    for (method, seed), record in sorted(log.records.items()):
        if record.summary_source_steps is None or not record.trace:
            continue  # the k-means baseline has no summaries
        by_step = {row["step"]: row for row in record.trace}
        pre, _ = fit_initial(X, len(record.summaries_evolution[0]), by_step[0]["last_max_iter"], seed)
        if not np.array_equal(pre.labels, record.assignments_evolution[0]):
            raise RuntimeError(f"{run} {method} seed {seed}: the step-0 replay differs from the logged partition")
        S = emb.steps(run, method, seed)[0]
        row = {"run": run, "method": method, "seed": seed, "n_clusters": len(S)}
        row.update(objective_identity(X, pre.labels, pre.centers, S))
        if steps is not None:
            logged = steps[(steps["run"] == run) & (steps["seed"] == seed) & (steps["step"] == 1)]
            if len(logged) != 1:
                raise RuntimeError(f"{run} seed {seed}: expected one step-1 row in the steps CSV, found {len(logged)}")
            logged = logged.iloc[0]
            row["logged_j_before"] = float(logged["j_before"])
            row["logged_old_minus_before"] = float(logged["j_old_assign"] - logged["j_before"])
            row["lhs_vs_logged_rel"] = abs(row["lhs"] - row["logged_old_minus_before"]) / abs(row["lhs"])
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dirs", nargs="+")
    parser.add_argument("--cache-dir", default="cache")
    parser.add_argument("--summary-embeddings", nargs="+", required=True)
    parser.add_argument("--steps-csv", default=None, help="replacement_diagnostic_steps.csv, for the logged objectives")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    emb = SummaryEmbeddings.load_many(args.summary_embeddings)
    steps = pd.read_csv(args.steps_csv) if args.steps_csv else None
    rows = []
    for run_dir in args.run_dirs:
        rows.extend(check_run(run_dir, emb, args.cache_dir, steps))
    df = pd.DataFrame(rows)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False, float_format="%.10g")

    print(f"{len(df)} replays ({df['run'].nunique()} runs)")
    print(f"identity: max abs residual {df['abs_resid'].max():.3e}, max relative residual {df['rel_resid'].max():.3e}")
    print(f"centers vs means: max sum_k n_k||m_k - x̄_k||^2 / J(C,M) = {df['center_gap_rel'].max():.3e}")
    if "lhs_vs_logged_rel" in df:
        print(f"a vs logged old-assignment minus before: max relative difference {df['lhs_vs_logged_rel'].max():.3e}")
    print(df.groupby("run")[["j_before", "lhs", "summary_gap", "center_gap", "n_empty_pre"]].mean().to_string())


if __name__ == "__main__":
    main()
