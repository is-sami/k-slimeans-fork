"""`scripts/check_objective_identity.py` (#81): the fixed-assignment objective identity on tiny random arrays."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_objective_identity.py"
spec = importlib.util.spec_from_file_location("check_objective_identity", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def _data(seed: int, n: int = 40, d: int = 5, k: int = 6, empty: tuple[int, ...] = ()):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, d))
    pool = np.array([c for c in range(k) if c not in empty])
    labels = rng.choice(pool, size=n)
    labels[: len(pool)] = pool  # every non-empty cluster has at least one member
    return X, labels, rng.normal(size=(k, d)), rng.normal(size=(k, d))


@pytest.mark.parametrize("empty", [(), (2,), (0, 5)])
def test_identity_holds_for_arbitrary_centers_with_and_without_empty_clusters(empty):
    X, labels, M, S = _data(0, empty=empty)  # M is not the means: the identity needs no such assumption
    out = check.objective_identity(X, labels, M, S)
    assert out["n_empty_pre"] == len(empty)
    assert out["lhs"] == pytest.approx(out["rhs"], rel=1e-12, abs=1e-12)
    assert out["abs_resid"] < 1e-10
    assert out["center_gap"] > 0  # random centers are far from the means


def test_means_minimise_the_objective_and_centers_at_the_means_have_no_gap():
    X, labels, _, S = _data(1, empty=(3,))
    sizes, means = check.cluster_means(X, labels, 6)
    assert sizes[3] == 0 and np.all(means[3] == 0)
    out = check.objective_identity(X, labels, means, S)
    assert out["center_gap"] == pytest.approx(0, abs=1e-12)
    # the rise equals the size-weighted squared distance of the new centers from the means
    assert out["lhs"] == pytest.approx(out["summary_gap"], rel=1e-12)
    assert out["lhs"] >= 0
    # J(C, Z) = J(C, means) + sum_k n_k ||z_k - mean_k||^2 for any Z
    base = check.assignment_objective(X, labels, means)
    assert check.assignment_objective(X, labels, S) == pytest.approx(base + out["summary_gap"], rel=1e-12)


def test_empty_cluster_centers_do_not_change_either_side():
    X, labels, M, S = _data(2, empty=(1,))
    M2, S2 = M.copy(), S.copy()
    M2[1] += 100.0
    S2[1] -= 100.0
    a, b = check.objective_identity(X, labels, M, S), check.objective_identity(X, labels, M2, S2)
    assert a["lhs"] == pytest.approx(b["lhs"], rel=1e-12)
    assert a["rhs"] == pytest.approx(b["rhs"], rel=1e-12)


def test_float32_input_is_handled_in_float64():
    X, labels, M, S = _data(3)
    out = check.objective_identity(X.astype(np.float32), labels, M.astype(np.float32), S.astype(np.float32))
    assert out["rel_resid"] < 1e-12
