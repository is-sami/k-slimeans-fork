"""`kslimeans.synthesis_chain` on tiny hand-made frames with known answers (no models, no files, no clocks)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from kslimeans import synthesis_chain as chain


def test_fisher_interval_stays_inside_the_correlation_range():
    iv = chain.fisher_interval([0.0, 0.9, 0.9, 0.9, 0.4])
    assert 0 < iv["lo"] < iv["mean"] < iv["hi"] < 1
    assert iv["mean"] == pytest.approx(np.tanh(np.mean(np.arctanh([0.0, 0.9, 0.9, 0.9, 0.4]))))
    assert iv["n_seeds"] == 5


def test_fisher_interval_handles_perfect_and_missing_values():
    iv = chain.fisher_interval([1.0, 1.0, np.nan, -1.0])
    assert iv["n_seeds"] == 3 and -1 <= iv["lo"] <= iv["hi"] <= 1
    empty = chain.fisher_interval([np.nan])
    assert np.isnan(empty["mean"]) and empty["n_seeds"] == 0


def _clusters():
    """Two seeds, two purity strata; the loss helps the low-purity clusters and hurts the high-purity ones."""
    rows = []
    for seed in (0, 1, 2):
        for i, (purity, lost, d) in enumerate([(0.2, 0.1, 0.01), (0.2, 0.5, 0.05), (0.2, 0.9, 0.2), (0.95, 0.1, -0.01), (0.95, 0.5, -0.1), (0.95, 0.9, -0.3)]):
            rows.append({"method_id": "m", "seed": seed, "cluster": i, "bin_purity": "low" if purity < 0.5 else "high", "lost_share": lost, "d": d})
    return pd.DataFrame(rows)


def test_correlations_by_stratum_gives_opposite_signs_per_stratum():
    table = chain.correlations_by_stratum(_clusters(), "bin_purity", ["lost_share"], ["d"])
    by = table.set_index("stratum")
    assert by.loc["low", "rho"] == pytest.approx(1.0) and by.loc["high", "rho"] == pytest.approx(-1.0)
    assert set(table["n_seeds"]) == {3}


def test_correlations_by_stratum_skips_rows_without_a_stratum():
    df = _clusters()
    df.loc[df["bin_purity"] == "high", "bin_purity"] = np.nan
    assert set(chain.correlations_by_stratum(df, "bin_purity", ["lost_share"], ["d"])["stratum"]) == {"low"}


def _steps(runs=("a", "b"), seeds=(0, 1, 2)):
    rows = []
    for r, run in enumerate(runs):
        for s in seeds:
            rows.append({"run": run, "seed": s, "step": 1, "acc_end": 0.5 + 0.01 * r, "acc_cf": 0.5})
            rows.append({"run": run, "seed": s, "step": 2, "acc_end": 0.0, "acc_cf": 0.9})
    return pd.DataFrame(rows)


def test_step_final_pairs_uses_the_requested_step_and_the_seeds_kmeans():
    steps = _steps()
    final = pd.DataFrame({"run": ["a"] * 3 + ["b"] * 3, "seed": [0, 1, 2] * 2, "final_acc": [0.55, 0.56, 0.57, 0.60, 0.61, 0.62]})
    km = pd.Series([0.5, 0.5, 0.5], index=[0, 1, 2])
    pairs = chain.step_final_pairs(steps, final, km)
    assert len(pairs) == 6
    b0 = pairs[(pairs["run"] == "b") & (pairs["seed"] == 0)].iloc[0]
    assert b0["d_step_acc"] == pytest.approx(0.01) and b0["d_final_acc"] == pytest.approx(0.10)


def test_step_final_pairs_refuses_a_missing_final_score_or_kmeans_seed():
    steps = _steps(runs=("a",))
    final = pd.DataFrame({"run": ["a", "a"], "seed": [0, 1], "final_acc": [0.5, 0.5]})
    with pytest.raises(ValueError, match="no final score"):
        chain.step_final_pairs(steps, final, pd.Series([0.5] * 3, index=[0, 1, 2]))
    final = pd.DataFrame({"run": ["a"] * 3, "seed": [0, 1, 2], "final_acc": [0.5] * 3})
    with pytest.raises(ValueError, match="no k-means score"):
        chain.step_final_pairs(steps, final, pd.Series([0.5], index=[0]))


def test_pair_correlations_separates_between_method_from_within_method_variation():
    # Methods differ in both columns together; within a method the two columns run in opposite directions.
    rows = []
    for run, base in (("clinc150_lsa", 0.0), ("a", 1.0), ("b", 2.0), ("c", 3.0)):
        for seed, jitter in enumerate((0.0, 0.1, 0.2)):
            rows.append({"run": run, "seed": seed, "d_step_acc": base + jitter, "d_final_acc": base - jitter})
    table = chain.pair_correlations(pd.DataFrame(rows)).set_index("scope")
    assert table.loc["pooled", "rho"] > 0.8
    assert table.loc["pooled without clinc150_lsa", "rho"] > 0.7
    assert table.loc["within method", "rho"] < -0.9  # ties from float noise keep it just above -1
    assert table.loc["within seed", "rho"] > 0.9 and table.loc["within seed", "hi"] <= 1.0


def test_pair_correlations_excludes_only_runs_that_are_present():
    pairs = pd.DataFrame({"run": ["a"] * 3 + ["b"] * 3, "seed": [0, 1, 2] * 2, "d_step_acc": np.arange(6.0), "d_final_acc": np.arange(6.0)})
    assert list(chain.pair_correlations(pairs, exclude=("lsa", "a"))["scope"]) == ["pooled", "pooled without a", "within method", "within seed"]


def test_method_means_counts_seeds_with_the_same_sign():
    pairs = pd.DataFrame({"run": ["a"] * 3, "seed": [0, 1, 2], "d_step_acc": [0.01, -0.02, 0.03], "d_final_acc": [0.02, -0.01, -0.04]})
    out = chain.method_means(pairs).iloc[0]
    assert out["d_step_acc"] == pytest.approx(0.02 / 3) and out["same_sign_seeds"] == 2 and out["n_seeds"] == 3


def _summaries(seeds=range(4), per_seed=10):
    """Per seed: 4 fluent poor, 4 fluent fine, 2 not fluent (one of them poor). Poor ones lose 0.8, the fine ones 0.1."""
    rows = []
    for seed in seeds:
        for i in range(per_seed):
            fluent = i < 8
            poor = i < 4 or i == 9
            rows.append({"method_id": "m", "seed": seed, "cluster": i, "flag_not_fluent": 0.0 if fluent else 1.0,
                         "flag_low_coverage": 1.0 if poor else 0.0, "flag_generic": 1.0 if i < 2 else 0.0,
                         "lost_share": 0.8 if poor else 0.1, "d": 0.05 * seed + (0.0 if poor else 0.02)})  # fmt: skip
    return pd.DataFrame(rows)


def test_readable_flags_only_mark_fluent_poor_summaries():
    out = chain.readable_flags(_summaries(seeds=[0]))
    assert out["fluent"].sum() == 8
    assert out["poor_among_fluent"].dropna().sum() == 4 and out["poor_among_fluent"].notna().sum() == 8
    assert out.loc[out["cluster"] == 9, "poor_representative"].iloc[0] == 1.0 and np.isnan(out.loc[out["cluster"] == 9, "poor_among_fluent"].iloc[0])


def test_readable_flags_keep_unscored_rows_unknown():
    df = _summaries(seeds=[0])
    df.loc[0, "flag_generic"] = np.nan
    out = chain.readable_flags(df)
    assert np.isnan(out.loc[0, "fluent"]) and np.isnan(out.loc[0, "poor_representative"])


def test_readable_shares_among_fluent_summaries():
    row = chain.readable_shares(_summaries()).iloc[0]
    assert row["n_fluent"] == 32 and row["n_poor_fluent"] == 16
    assert row["share_poor"] == pytest.approx(0.5) and row["share_generic"] == pytest.approx(0.25) and row["share_low_coverage"] == pytest.approx(0.5)
    assert row["share_fluent"] == pytest.approx(0.8)


def test_readable_contrast_poor_minus_pass_per_seed():
    out = chain.readable_contrast(_summaries(), ["lost_share", "d"]).set_index("outcome")
    assert out.loc["lost_share", "diff"] == pytest.approx(0.7) and out.loc["lost_share", "mean_poor"] == pytest.approx(0.8)
    assert out.loc["d", "diff"] == pytest.approx(-0.02) and out.loc["d", "lo"] == pytest.approx(-0.02)  # no spread between seeds
    assert out.loc["d", "n_poor"] == 16 and out.loc["d", "n_pass"] == 16 and out.loc["d", "n_seeds"] == 4


def test_readable_contrast_within_strata_and_with_too_few_clusters():
    df = pd.concat([_summaries()] * 2, ignore_index=True)
    df["bin"] = np.where(df["cluster"] % 2 == 0, "x", "y")
    out = chain.readable_contrast(df, ["lost_share"], ["bin"]).iloc[0]
    assert out["adjustment"] == "bin" and out["diff"] == pytest.approx(0.7)
    few = chain.readable_contrast(_summaries(per_seed=10).query("cluster < 6"), ["lost_share"]).iloc[0]  # 2 fine clusters per seed
    assert np.isnan(few["diff"])


def test_fisher_interval_with_five_values_matches_a_hand_value():
    from scipy import stats

    z = np.arctanh([0.0, 0.9, 0.9, 0.9, 0.4])
    half = stats.t.ppf(0.975, 4) * z.std(ddof=1) / np.sqrt(5)
    iv = chain.fisher_interval([0.0, 0.9, 0.9, 0.9, 0.4])
    assert iv["mean"] == pytest.approx(np.tanh(z.mean()), abs=1e-9)
    assert iv["lo"] == pytest.approx(np.tanh(z.mean() - half), abs=1e-9) and iv["hi"] == pytest.approx(np.tanh(z.mean() + half), abs=1e-9)
    assert iv["mean"] == pytest.approx(0.7478, abs=1e-3)  # the within-seed value of synthesis.md section 11 has the same form


def _carried_by_one_run():
    """Four runs, three seeds: run "x" is low on both axes and carries the between-method correlation; the others are flat noise."""
    rows = []
    noise = {"a": [(0.0, 0.1), (0.1, 0.0), (0.2, -0.1)], "b": [(0.1, 0.0), (0.0, -0.1), (0.2, 0.1)], "c": [(0.2, 0.1), (0.1, 0.2), (0.0, 0.0)]}
    for run, vals in noise.items():
        for seed, (x, y) in enumerate(vals):
            rows.append({"run": run, "seed": seed, "d_step_acc": x, "d_final_acc": y})
    for seed in range(3):
        rows.append({"run": "x", "seed": seed, "d_step_acc": -1.0 - 0.1 * seed, "d_final_acc": -1.0 - 0.1 * seed})
    return pd.DataFrame(rows)


def test_leave_one_out_shows_which_run_carries_the_correlation():
    out = chain.leave_one_out(_carried_by_one_run()).set_index("scope")
    assert chain.pair_correlations(_carried_by_one_run()).set_index("scope").loc["pooled", "rho"] > 0.6
    assert out.loc["without x: pooled", "rho"] < 0.4  # the carrier removed: nothing is left
    assert out.loc["without a: pooled", "rho"] > 0.6  # another run removed: the carrier still holds
    assert out.loc["without x: pooled", "n"] == 9 and len(out) == 4 * 3  # pooled, within method, within seed per left-out run


def _joined_for_chain(seeds=range(3), n=12):
    rng = np.random.default_rng(0)
    rows = []
    for method in ("m1", "m2"):
        for seed in seeds:
            for c in range(n):
                cov = rng.uniform()
                rows.append({"method_id": method, "seed": seed, "cluster": c, "step": 1, "has_diag": True, "coverage_nearest": cov,
                             "specificity_margin": cov - 0.3 + rng.normal(0, 0.1), "unsupported_lemma_share": rng.uniform(),
                             "drift": 2 - cov + rng.normal(0, 0.1), "own_nearest": float(cov > 0.5), "lost_share": 1 - cov,
                             "gained_share": rng.uniform(), "purity": rng.uniform(0.2, 1.0), "n_members": 50 + c, "log_n_members": np.log(50 + c),
                             "d_member_purity": rng.normal(0, 0.05), "d_member_purity_vs_cf": rng.normal(0, 0.05),
                             "d_member_purity_vs_null": rng.normal(0.1, 0.05), "flag_not_fluent": float(c % 5 == 0),
                             "flag_low_coverage": float(cov < 0.5), "flag_generic": float(c % 4 == 0)})
    return pd.DataFrame(rows)


def test_build_chain_and_build_readable_on_small_inputs():
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location("synthesis_chain_script", Path(__file__).parents[1] / "scripts" / "synthesis_chain.py")
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    df = _joined_for_chain()
    pairs = pd.DataFrame({"run": ["a"] * 3 + ["b"] * 3 + ["c"] * 3, "seed": [0, 1, 2] * 3, "d_step_acc": np.arange(9.0), "d_final_acc": np.arange(9.0) ** 2})
    table = script.build_chain(df, pairs)
    assert {"1 quality to movement", "2 movement to assignment changes", "3 assignment changes to purity change", "4 step-1 partition to final score"} <= set(table["link"])
    row = table[(table["link"] == "1 quality to movement") & (table["x"] == "coverage_nearest") & (table["y"] == "drift") & (table["controls"] == "none")]
    assert (row["estimate"] < -0.5).all() and len(row) == 2
    assert table["stratum"].str.startswith("without a:").sum() >= 3  # leave-one-out rows are written
    readable = script.build_readable(df)
    assert set(readable["kind"]) == {"share", "contrast"} and set(readable["method_id"]) == {"m1", "m2"}
    share = readable[readable["kind"] == "share"].set_index("method_id")
    assert share.loc["m1", "n_fluent"] == 27 and 0 < share.loc["m1", "share_poor"] <= 1


def test_pick_takes_the_largest_gain_and_the_largest_loss_among_fluent_poor_clusters():
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location("examples_script", Path(__file__).parents[1] / "scripts" / "synthesis_chain_examples.py")
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    df = pd.DataFrame({"run_config": "r", "seed": 0, "step": 1, "cluster": range(5), "n_members": [60, 60, 60, 60, 10],
                       "flag_not_fluent": [0.0, 0.0, 0.0, 1.0, 0.0], "flag_low_coverage": 1.0, "flag_generic": 0.0,
                       "d_member_purity_vs_cf": [0.1, -0.3, 0.4, -0.9, 0.9]})
    picked = script.pick(df, "r", 0, 50)
    assert picked["best"]["cluster"] == 2 and picked["worst"]["cluster"] == 1  # 3 is not fluent, 4 is too small
