"""The chain from a summary's quality to the final score (issue #50, section 11 and 12 of `docs/results/synthesis.md`).

The per-cluster links (summary quality -> centroid movement -> assignment changes -> purity change) reuse
`synthesis.correlation_table` on the joined frame; this module adds what the synthesis did not have:

- `correlations_by_stratum`: the same rank correlations within the strata of one column (purity before the step);
- `step_final_pairs` and `pair_correlations`: per (run, seed) pair, the step-1 ACC change against plain Lloyd and the final
  ACC difference to k-means, and how they go together (pooled, within a method, within a seed across methods);
- `readable_flags`, `readable_shares` and `readable_contrast`: among summaries that pass every fluency proxy, the share
  that is a poor representative (low coverage or generic) and what happened to their clusters compared with the ones that
  are not.

Every interval has the seed as the unit, as in `kslimeans.synthesis`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from . import synthesis as syn


def fisher_interval(values, level: float = 0.95) -> dict:
    """Mean of per-seed correlations and its interval, both taken on Fisher's z scale and mapped back.

    A plain t-interval on correlations can leave [-1, 1]; this one cannot. NaNs are dropped; fewer than two values give
    NaN bounds, and a correlation of exactly +-1 is clipped to +-0.999999 before the transform.
    """
    v = np.asarray(pd.Series(values, dtype=float).dropna())
    z = np.arctanh(np.clip(v, -0.999999, 0.999999))
    iv = syn.seed_interval(z, level)
    return {"mean": float(np.tanh(iv["mean"])) if iv["n_seeds"] else np.nan,
            "lo": float(np.tanh(iv["lo"])), "hi": float(np.tanh(iv["hi"])), "n_seeds": iv["n_seeds"]}  # fmt: skip


def correlations_by_stratum(
    df: pd.DataFrame, stratum: str, props: list[str], outcomes: list[str], controls: list[str] | None = None
) -> pd.DataFrame:
    """`synthesis.correlation_table` within each value of the column `stratum`, with a `stratum` column added.

    Rows whose stratum is NaN are left out. Within a stratum a seed needs three clusters with defined values for its
    correlation to count, and the cell needs three seeds (`synthesis.summarise_seeds`).
    """
    parts = [
        syn.correlation_table(g, props, outcomes, controls).assign(stratum=str(value))
        for value, g in df.dropna(subset=[stratum]).groupby(stratum, sort=False)
    ]
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


# ------------------------------------------------------------------------------- step 1 against the final score


def step_final_pairs(steps: pd.DataFrame, final: pd.DataFrame, kmeans_acc: pd.Series, step: int = 1) -> pd.DataFrame:
    """One row per (run, seed): the step's ACC change against plain Lloyd and the final ACC difference to k-means.

    `steps` has `run`, `seed`, `step`, `acc_end` (the logged partition after the block) and `acc_cf` (plain Lloyd from the
    same state); `final` has `run`, `seed`, `final_acc`; `kmeans_acc` is indexed by seed (the k-means run of that seed,
    shared by every method). Pairs without a final score are dropped; every (run, seed) of `steps` must be in `final`.
    """
    a = steps[steps["step"] == step][["run", "seed", "acc_end", "acc_cf"]].copy()
    a["d_step_acc"] = a["acc_end"] - a["acc_cf"]
    pairs = a.merge(final[["run", "seed", "final_acc"]], on=["run", "seed"], how="left", validate="one_to_one")
    if pairs["final_acc"].isna().any():
        raise ValueError("a (run, seed) pair with a step-1 outcome has no final score")
    missing = set(pairs["seed"]) - set(kmeans_acc.index)
    if missing:
        raise ValueError(f"no k-means score for seeds {sorted(missing)}")
    pairs["d_final_acc"] = pairs["final_acc"] - pairs["seed"].map(kmeans_acc)
    return pairs[["run", "seed", "d_step_acc", "d_final_acc"]].reset_index(drop=True)


def _rho(x, y) -> float:
    return float(stats.spearmanr(x, y)[0]) if len(x) >= 3 and np.ptp(x) > 0 and np.ptp(y) > 0 else np.nan


def pair_correlations(pairs: pd.DataFrame, exclude: tuple[str, ...] = ("clinc150_lsa",)) -> pd.DataFrame:
    """How the step-1 change and the final difference go together across (run, seed) pairs.

    Rows (`scope`): `pooled` (all pairs; mixes the difference between methods with the one between seeds),
    `pooled without <run>` for each run in `exclude` that is present, `within method` (both columns minus the method's own
    mean, so only the seed-to-seed variation is left) and `within seed` (the correlation across the methods of one seed,
    averaged over seeds on the Fisher scale with its interval). The pooled pairs are not independent (seeds share a
    step-0 partition across methods); no p-value is given.
    """
    x, y = pairs["d_step_acc"].to_numpy(float), pairs["d_final_acc"].to_numpy(float)
    rows = [{"scope": "pooled", "rho": _rho(x, y), "lo": np.nan, "hi": np.nan, "n": len(pairs), "n_seeds": pairs["seed"].nunique()}]
    for run in exclude:
        if run in set(pairs["run"]):
            rest = pairs[pairs["run"] != run]
            rows.append({"scope": f"pooled without {run}", "rho": _rho(rest["d_step_acc"].to_numpy(float), rest["d_final_acc"].to_numpy(float)),
                         "lo": np.nan, "hi": np.nan, "n": len(rest), "n_seeds": rest["seed"].nunique()})  # fmt: skip
    centred = pairs[["d_step_acc", "d_final_acc"]] - pairs.groupby("run")[["d_step_acc", "d_final_acc"]].transform("mean")
    rows.append({"scope": "within method", "rho": _rho(centred["d_step_acc"].to_numpy(float), centred["d_final_acc"].to_numpy(float)),
                 "lo": np.nan, "hi": np.nan, "n": len(pairs), "n_seeds": pairs["seed"].nunique()})  # fmt: skip
    per_seed = [_rho(g["d_step_acc"].to_numpy(float), g["d_final_acc"].to_numpy(float)) for _, g in pairs.groupby("seed")]
    iv = fisher_interval(per_seed)
    rows.append({"scope": "within seed", "rho": iv["mean"], "lo": iv["lo"], "hi": iv["hi"], "n": int(pairs.groupby("seed").size().min()), "n_seeds": iv["n_seeds"]})  # fmt: skip
    return pd.DataFrame(rows)


def leave_one_out(pairs: pd.DataFrame) -> pd.DataFrame:
    """`pair_correlations` with each run left out in turn (`scope` is prefixed `without <run>:`).

    The between-method correlation rests on five methods, so one of them can carry it; this shows which.
    """
    parts = []
    for run in sorted(pairs["run"].unique()):
        rest = pair_correlations(pairs[pairs["run"] != run], exclude=())
        parts.append(rest.assign(scope=f"without {run}: " + rest["scope"]))
    return pd.concat(parts, ignore_index=True)


def method_means(pairs: pd.DataFrame) -> pd.DataFrame:
    """Per run: the mean step-1 change, the mean final difference, and the number of seeds with the same sign in both."""
    out = pairs.groupby("run").agg(d_step_acc=("d_step_acc", "mean"), d_final_acc=("d_final_acc", "mean"), n_seeds=("seed", "nunique"))
    out["same_sign_seeds"] = pairs.assign(same=np.sign(pairs["d_step_acc"]) == np.sign(pairs["d_final_acc"])).groupby("run")["same"].sum()
    return out.reset_index()


# ------------------------------------------------------------------------------- readable but a poor representative


def readable_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Adds `fluent` (passes every fluency proxy), `poor_representative` and `poor_among_fluent` (NaN where not fluent).

    A summary is a poor representative when it fails coverage (`flag_low_coverage`: under half of its members have it
    as their nearest summary) or specificity (`flag_generic`: a duplicate, a near duplicate, a mention of the cluster or a
    margin of 0 or less). Rows without a flag value (not scored) stay NaN.
    """
    out = df.copy()
    known = out["flag_not_fluent"].notna() & out["flag_low_coverage"].notna() & out["flag_generic"].notna()
    out["fluent"] = np.where(known, (out["flag_not_fluent"] == 0).astype(float), np.nan)
    out["poor_representative"] = np.where(known, ((out["flag_low_coverage"] == 1) | (out["flag_generic"] == 1)).astype(float), np.nan)
    out["poor_among_fluent"] = np.where(out["fluent"] == 1.0, out["poor_representative"], np.nan)
    return out


def readable_shares(df: pd.DataFrame) -> pd.DataFrame:
    """Per method: how many summaries are fluent and the share of them that fails coverage, specificity or either.

    Shares are means over the seeds of the per-seed share among the seed's fluent summaries, with the interval over seeds.
    """
    rows = []
    for mid, g in readable_flags(df).groupby("method_id", sort=False):
        fluent = g[g["fluent"] == 1.0]
        row = {"method_id": mid, "n_clusters": len(g), "n_fluent": len(fluent), "share_fluent": len(fluent) / len(g) if len(g) else np.nan}
        for name, col in (("poor", "poor_representative"), ("low_coverage", "flag_low_coverage"), ("generic", "flag_generic")):
            iv = syn.seed_interval(fluent.groupby("seed")[col].mean())
            row.update({f"share_{name}": iv["mean"], f"share_{name}_lo": iv["lo"], f"share_{name}_hi": iv["hi"]})
        row["n_poor_fluent"] = int((fluent["poor_representative"] == 1.0).sum())
        rows.append(row)
    return pd.DataFrame(rows)


def readable_contrast(df: pd.DataFrame, outcomes: list[str], strata: list[str] | None = None) -> pd.DataFrame:
    """Among fluent summaries: poor representatives minus the others, per method and outcome, seeds as the unit.

    Per row the means of both groups (over seeds), their difference (`synthesis.stratified_difference`, optionally within
    the `strata` columns, so the groups are compared at equal purity) and its interval; `n_poor` and `n_pass` count
    clusters. Methods with fewer than `MIN_SEEDS` seeds that have `MIN_PER_SEED` clusters in both groups give NaN.
    """
    rows = []
    for mid, g in readable_flags(df).groupby("method_id", sort=False):
        fluent = g[g["fluent"] == 1.0]
        for outcome in outcomes:
            diff = syn.stratified_difference(fluent, "poor_among_fluent", outcome, strata)
            per_group = fluent.groupby(["seed", "poor_among_fluent"])[outcome].mean().unstack("poor_among_fluent")
            rows.append({"method_id": mid, "outcome": outcome, "adjustment": "+".join(strata) if strata else "none",
                         "n_poor": int((fluent["poor_among_fluent"] == 1.0).sum()), "n_pass": int((fluent["poor_among_fluent"] == 0.0).sum()),
                         "mean_poor": per_group.get(1.0, pd.Series(dtype=float)).mean(), "mean_pass": per_group.get(0.0, pd.Series(dtype=float)).mean(),
                         "diff": diff["mean"], "lo": diff["lo"], "hi": diff["hi"], "n_seeds": diff["n_seeds"]})  # fmt: skip
    return pd.DataFrame(rows)
