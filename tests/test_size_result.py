"""`kslimeans.size_result` on tiny hand-made paired tables, and the committed CSV against the committed paired files."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from kslimeans import size_result as sr
from kslimeans.aggregate import paired_differences

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "docs" / "results"


def _paired(prompt: str = "old", sd: float = 0.01, mean: float = 0.02) -> pd.DataFrame:
    rows = []
    for larger, smaller in sr.SIZE_PAIRS:
        for metric in sr.METRICS:
            rows.append(
                {
                    "reference": sr.method_name(smaller, prompt), "method": sr.method_name(larger, prompt),
                    "metric": metric, "n": 5, "mean_diff": mean, "sd": sd, "ci_low": mean - 0.012,
                    "ci_high": mean + 0.012, "wins": 4, "ties": 0,
                }
            )  # fmt: skip
    return pd.DataFrame(rows)


def test_min_detectable_matches_the_formula():
    expected = (stats.t.ppf(0.975, 4) + stats.t.ppf(0.8, 4)) * 0.01 / np.sqrt(5)
    assert sr.min_detectable(0.01, 5) == pytest.approx(expected)
    assert sr.min_detectable(0.01, 5) == pytest.approx(1.6625 * 0.01, rel=1e-3)


def test_min_detectable_scales_with_sd_and_shrinks_with_n():
    assert sr.min_detectable(0.02, 5) == pytest.approx(2 * sr.min_detectable(0.01, 5))
    assert sr.min_detectable(0.01, 10) < sr.min_detectable(0.01, 5)


def test_min_detectable_exact_is_close_to_the_approximation_and_reaches_the_power():
    sd, n = 0.01, 5
    exact = sr.min_detectable_exact(sd, n)
    assert exact == pytest.approx(sr.min_detectable(sd, n), rel=0.03)
    crit = stats.t.ppf(0.975, n - 1)
    assert stats.nct.sf(crit, n - 1, exact * np.sqrt(n) / sd) == pytest.approx(0.8, abs=1e-6)


@pytest.mark.parametrize("fn", [sr.min_detectable, sr.min_detectable_exact])
def test_min_detectable_is_nan_without_a_spread(fn):
    assert np.isnan(fn(float("nan"), 5))
    assert np.isnan(fn(0.01, 1))


def test_size_table_rows_and_flags():
    table = sr.size_table(_paired(sd=0.01, mean=0.02), "Toy", "old")
    assert len(table) == 9
    assert set(table["larger"] + "/" + table["smaller"]) == {"1.7B/0.6B", "4B/0.6B", "4B/1.7B"}
    row = table.iloc[0]
    assert row["min_detectable"] == pytest.approx(sr.min_detectable(0.01, 5))
    assert not row["below_min_detectable"]  # 0.02 > 0.0166
    assert row["ci_excludes_zero"]
    small = sr.size_table(_paired(sd=0.01, mean=0.005), "Toy", "old")
    assert small["below_min_detectable"].all()
    assert not small["ci_excludes_zero"].any()  # ci_low = -0.007


def test_size_table_uses_the_v2_labels():
    table = sr.size_table(_paired("v2"), "Toy", "v2")
    assert (table["prompt"] == "v2").all()
    with pytest.raises(ValueError, match="expected one row"):
        sr.size_table(_paired("old"), "Toy", "v2")


def _script():
    spec = importlib.util.spec_from_file_location("size_result_script", ROOT / "scripts" / "size_result.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_table_matches_the_committed_inputs():
    built = _script().build(RESULTS)
    committed = pd.read_csv(RESULTS / "size_result_table.csv")
    assert len(built) == len(committed) == 45
    pd.testing.assert_frame_equal(built.reset_index(drop=True), committed, check_exact=False, atol=1e-6)


def test_bank77_rows_come_from_the_per_seed_file():
    per_seed = pd.read_csv(RESULTS / "prelim_bank77_per_seed.csv")
    paired = paired_differences(per_seed, _script().BANK77_REFERENCES)
    table = sr.size_table(paired, "BANKING77", "old")
    row = table[(table["larger"] == "4B") & (table["smaller"] == "1.7B") & (table["metric"] == "acc")].iloc[0]
    four = per_seed[per_seed["method"] == sr.method_name("4B", "old")].set_index("seed")["acc"]
    one = per_seed[per_seed["method"] == sr.method_name("1.7B", "old")].set_index("seed")["acc"]
    assert row["mean_diff"] == pytest.approx((four - one).mean())
    assert row["wins"] == int(((four - one) > 0).sum())
