"""`kslimeans.review_packets` on tiny hand-made inputs with known answers."""

from __future__ import annotations

import csv
import io

import numpy as np
import pandas as pd
import pytest

from kslimeans import review_packets as rp


def _scores(rows):
    return pd.DataFrame(rows, columns=["method", "cluster", "score"])


# ------------------------------------------------------------------ selection (packet A)


def test_select_cases_takes_extremes_per_side():
    scores = _scores([("a", 0, 0.5), ("a", 1, 0.3), ("b", 2, -0.4), ("b", 3, -0.9), ("a", 4, 0.0)])
    picks = rp.select_cases(scores, per_side=2, per_method_cap=2, method_order=["a", "b"])
    helped = picks[picks["side"] == "helped"]
    hurt = picks[picks["side"] == "hurt"]
    assert list(zip(helped["method"], helped["cluster"])) == [("a", 0), ("a", 1)]
    assert list(zip(hurt["method"], hurt["cluster"])) == [("b", 3), ("b", 2)]  # most negative first
    assert list(picks["rank"]) == [1, 2, 1, 2]


def test_select_cases_per_method_cap():
    scores = _scores([("a", c, 1.0 - 0.1 * c) for c in range(5)] + [("b", 10 + c, 0.1 - 0.01 * c) for c in range(3)])
    picks = rp.select_cases(scores, per_side=4, per_method_cap=2, method_order=["a", "b"])
    helped = picks[picks["side"] == "helped"]
    assert list(helped["method"]) == ["a", "a", "b", "b"]
    assert list(helped["cluster"]) == [0, 1, 10, 11]


def test_select_cases_prefers_distinct_cluster_ids_then_falls_back():
    scores = _scores([("a", 7, 0.9), ("b", 7, 0.8), ("a", 8, 0.1), ("b", 9, 0.05)])
    picks = rp.select_cases(scores, per_side=3, per_method_cap=3, method_order=["a", "b"])
    helped = picks[picks["side"] == "helped"]
    assert list(zip(helped["method"], helped["cluster"], helped["pass"])) == [("a", 7, 1), ("a", 8, 1), ("b", 9, 1)]
    # with only three distinct ids needed but four slots, the repeated id is used in pass 2
    more = rp.select_cases(scores, per_side=4, per_method_cap=3, method_order=["a", "b"])
    last = more[more["side"] == "helped"].iloc[-1]
    assert (last["method"], last["cluster"], last["pass"]) == ("b", 7, 2)


def test_select_cases_ties_and_nan_and_sign():
    scores = _scores([("b", 1, 0.5), ("a", 2, 0.5), ("a", 1, 0.5), ("a", 3, np.nan), ("b", 4, 0.0)])
    picks = rp.select_cases(scores, per_side=10, per_method_cap=10, method_order=["a", "b"])
    helped = picks[picks["side"] == "helped"]
    assert list(zip(helped["method"], helped["cluster"])) == [("a", 1), ("a", 2), ("b", 1)]  # ties: method order, id
    assert picks[picks["side"] == "hurt"].empty  # zero and NaN are neither helped nor hurt


def test_select_cases_unknown_method_raises():
    with pytest.raises(ValueError, match="method_order"):
        rp.select_cases(_scores([("z", 0, 1.0)]), 1, 1, ["a"])


# ------------------------------------------------------------------ same partition (packet B)


def test_check_same_partition_accepts_identical():
    labels = np.array([0, 1, 1, 0])
    rp.check_same_partition({"a": labels, "b": labels.copy()}, {"a": "x", "b": "x", "c": None})


def test_check_same_partition_fails_on_mismatched_assignments():
    with pytest.raises(ValueError, match="1 documents differ"):
        rp.check_same_partition({"a": np.array([0, 1, 1, 0]), "b": np.array([0, 1, 0, 0])})
    with pytest.raises(ValueError, match="different lengths"):
        rp.check_same_partition({"a": np.array([0, 1]), "b": np.array([0, 1, 1])})


def test_check_same_partition_fails_on_mismatched_sha1():
    labels = np.array([0, 1])
    with pytest.raises(ValueError, match="step0_sha1"):
        rp.check_same_partition({"a": labels, "b": labels}, {"a": "x", "b": "y"})


# ------------------------------------------------------------------ measures and sampling


def test_step_change_known_values():
    gold = np.array([0, 0, 1, 1, 1, 0])
    source = np.array([0, 0, 0, 1, 1, 1])
    after = np.array([0, 0, 1, 1, 1, 1])
    change = rp.step_change(source, after, gold, 2)
    # cluster 0 = {0,0,1} (purity 2/3): afterwards doc 2 (gold 1) joins cluster 1, whose majority is 1, so all 3 agree.
    # cluster 1 = {1,1,0}: it keeps all of them, and the majority of its new members is still 1 (purity 2/3 unchanged).
    assert change["purity"].tolist() == pytest.approx([2 / 3, 2 / 3])
    assert change["d_member_purity"].tolist() == pytest.approx([1 - 2 / 3, 2 / 3 - 2 / 3])


def test_stratified_sample_is_seeded_and_covers_bins():
    purity = np.array([0.2] * 8 + [0.5] * 8 + [0.7] * 2 + [0.85] * 8 + [0.95] * 8 + [np.nan])
    first = rp.stratified_sample(purity, 3, seed=1)
    assert first == rp.stratified_sample(purity, 3, seed=1)
    assert first != rp.stratified_sample(purity, 3, seed=2)
    bins = rp.purity_bins(purity[first])
    assert np.bincount(bins, minlength=5).tolist() == [3, 3, 2, 3, 3]  # the (0.6, 0.8] bin has only 2 clusters
    assert len(set(first)) == len(first) and 32 not in first  # the empty cluster is never drawn


def test_purity_bins_edges():
    assert rp.purity_bins(np.array([0.4, 0.41, 0.6, 0.8, 0.9, 0.91, 1.0])).tolist() == [0, 1, 1, 2, 3, 4, 4]


def test_movers_and_intents():
    gold = np.array([0, 0, 1, 1, 2, 2])
    source = np.array([0, 0, 0, 1, 1, 1])
    after = np.array([0, 1, 0, 1, 1, 0])
    mv = rp.movers(source, after, gold, 0, 2)
    assert mv["left"].tolist() == [1] and mv["arrived"].tolist() == [5]
    assert mv["left_majority"].tolist() == [0]  # cluster 1 after = docs 1,3,4 (gold 0,1,2): lowest-id majority is 0
    comp = rp.intent_composition(np.array([2, 2, 1, 0]), ["a", "b", "c"], top=2)
    assert comp == [("c", 2), ("a", 1)]  # the tie between a and b goes to the lower id
    assert rp.sample_ids(np.arange(3), 10, np.random.default_rng(0)) == [0, 1, 2]
    assert len(rp.sample_ids(np.arange(30), 10, np.random.default_rng(0))) == 10


# ------------------------------------------------------------------ formatting and the tagging template


def test_md_escape_and_fenced():
    assert rp.md_escape("a *b*\n _c_ [d](e) | f <g> $5") == "a \\*b\\* \\_c\\_ \\[d\\](e) \\| f \\<g\\> \\$5"
    block = rp.fenced("say ``` hi\nand `x`")
    assert block.startswith("````text\n") and block.endswith("\n````")


def test_tagging_rows_are_clusters_times_six():
    models, prompts = ["m1", "m2", "m3"], ["old", "clearer"]
    clusters = [4, 9, 12]
    summaries = {(c, m, p): f"s{c}{m}{p}" for c in clusters for m in models for p in prompts}
    rows = rp.tagging_rows(clusters, {c: 100 + c for c in clusters}, summaries, models, prompts)
    assert len(rows) == len(clusters) * 6
    assert len({(r[0], r[2], r[3]) for r in rows}) == 18
    text = rp.csv_text(["cluster", "size", "model", "prompt", "summary", *rp.TAG_COLUMNS], rows)
    parsed = list(csv.reader(io.StringIO(text)))
    assert len(parsed) == 19 and all(len(r) == 5 + len(rp.TAG_COLUMNS) for r in parsed)
    assert all(cell == "" for r in parsed[1:] for cell in r[5:])
