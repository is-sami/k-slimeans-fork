"""`kslimeans.human_eval` and `scripts/human_eval_report.py` on tiny hand-made sheets and keys."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from kslimeans.human_eval import (
    analyse_rows,
    analyse_unsupported,
    category_counts,
    check_flags,
    check_sheets,
    consensus_sheet,
    flagged_table,
    members_fit_agreement,
    pairwise_agreement,
    paraphrase_summary,
    rater_disagreements,
    reverse_table,
    shown_members,
    vs_flags,
)
from kslimeans.summary_quality import load_nlp

try:
    NLP = load_nlp()
except OSError:  # pragma: no cover - the model is a documented install step
    pytest.skip("spaCy model en_core_web_sm is not installed", allow_module_level=True)

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
IDS = ["d-01-A", "d-01-B", "d-01-C", "d-01-D"]


def sheet(fit, generic, unsupported, fluent, summaries=None, members=None) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "row_id": IDS,
            "summary": summaries or ["s"] * 4,
            "members_shown": [10] * 4,
            "members": members or ["1. x"] * 4,
            "members_fit": fit,
            "generic": generic,
            "unsupported": unsupported,
            "fluent": fluent,
        }
    )


KEY = pd.DataFrame(
    {
        "row_id": IDS,
        "dataset": "d",
        "method": ["m1", "m2", "m1", "m2"],
        "flag_low_coverage": [False, True, True, False],
        "flag_generic": [False, True, False, False],
        "flag_unsupported": [False, False, True, False],
        "flag_not_fluent": [False, False, True, True],
    }
)
A = sheet([9, 2, 8, 1], [0, 1, 0, 1], [0, 0, 1, 0], [1, 1, 0, 1])
B = sheet([9, 3, 3, 8], [0, 1, 0, 1], [0, 0, 1, ""], [1, 1, 0, 1])  # B: C low coverage, D unsupported unrated


def test_pairwise_agreement_has_one_table_per_pair_and_the_2x2_counts():
    tables = pairwise_agreement({"a": A, "b": B, "c": A})
    assert list(tables) == [("a", "b"), ("a", "c"), ("b", "c")]
    low = tables[("a", "b")].set_index("property").loc["low_coverage"]
    # a marks B, D (fit/10 < 0.5); b marks B, C
    assert low[["n", "both", "hand_only", "auto_only", "neither"]].tolist() == [4, 1, 1, 1, 1]
    assert low["raw_agreement"] == 0.5 and low["kappa"] == 0.0
    assert tables[("a", "b")].set_index("property").loc["unsupported", "n"] == 3  # the empty cell is dropped


def test_members_fit_agreement_spearman_and_mean_abs_diff():
    out = members_fit_agreement(A, sheet([1, 2, 3, 4], [0] * 4, [0] * 4, [1] * 4))
    assert out["n"] == 4 and out["spearman"] == pytest.approx(-0.8)  # ranks (4,2,3,1) vs (1,2,3,4)
    assert out["mean_abs_diff"] == pytest.approx((8 + 0 + 5 + 3) / 4)
    assert members_fit_agreement(A, B)["identical"] == 1
    assert members_fit_agreement(A, sheet([""] * 4, [0] * 4, [0] * 4, [1] * 4))["n"] == 0
    assert np.isnan(members_fit_agreement(A, sheet([5] * 4, [0] * 4, [0] * 4, [1] * 4))["spearman"])


def test_rater_disagreements_lists_labels_and_counts_but_not_empty_cells():
    dis = rater_disagreements({"a": A, "b": B})
    got = {(r.row_id, r.property): (r.a, r.b) for r in dis.itertuples()}
    assert got[("d-01-C", "low_coverage")] == (0, 1)
    assert got[("d-01-D", "low_coverage")] == (1, 0)
    assert got[("d-01-B", "members_fit")] == (2, 3)  # same label, different count: listed under members_fit
    assert ("d-01-D", "unsupported") not in got  # b left it empty
    assert not any(p in ("generic", "not_fluent") for _, p in got)


def test_consensus_keeps_only_ratings_all_raters_agree_on():
    cons = consensus_sheet({"a": A, "b": B}).set_index("row_id")
    assert cons.loc["d-01-C", "members_fit"] != cons.loc["d-01-C", "members_fit"]  # NaN: labels differ
    assert cons.loc["d-01-B", "members_fit"] == 2  # counts differ, label agrees: the first rater's count
    assert pd.isna(cons.loc["d-01-D", "unsupported"]) and cons.loc["d-01-C", "unsupported"] == 1
    tables = vs_flags({"a": A, "b": B}, KEY)
    assert list(tables) == ["a", "b", "consensus"]
    cons_t = tables["consensus"].set_index("property")
    assert cons_t.loc["low_coverage", "n"] == 2 and cons_t.loc["unsupported", "n"] == 3
    assert cons_t.loc["generic", "n"] == 4


def test_check_sheets_fails_loudly_on_missing_rows_or_different_summaries():
    check_sheets({"a": A, "b": B}, KEY)
    with pytest.raises(ValueError, match="rows of the key"):
        check_sheets({"a": A.iloc[:3], "b": B}, KEY)
    other = sheet([1] * 4, [0] * 4, [0] * 4, [1] * 4, summaries=["s", "s", "s", "different"])
    with pytest.raises(ValueError, match="summaries"):
        check_sheets({"a": A, "b": other}, KEY)


def test_shown_members_strips_numbering():
    assert shown_members("1. how do I pay\n2. cancel my card") == ["how do I pay", "cancel my card"]


def test_analyse_unsupported_triggers_use_the_full_members_and_split_shown_from_unshown():
    shown = ["How do I cancel my card?"]
    members = [*shown, "I want to terminate my 3 account in Paris"]
    res = analyse_unsupported("How can I cancel my card in Berlin 7?", shown, members, NLP)
    assert res["flag_unsupported"] is True or res["flag_unsupported"] == 1
    assert res["unsupported_items"].split() == ["7", "berlin"]  # number and entity absent from every member
    assert "cancel" in res["lemmas_in_shown"].split()
    res = analyse_unsupported("Terminate my account", shown, members, NLP)
    assert res["lemmas_unshown_only"].split() == ["account", "terminate"]  # only in the unshown member
    assert res["lemmas_in_no_member"] == "" and not res["flag_unsupported"]  # the flag reads all members
    paraphrase = analyse_unsupported("Stop my card", shown, members, NLP)
    assert "stop" in paraphrase["unsupported_lemmas"].split()


def make_analysis(sheet_a: pd.DataFrame, key: pd.DataFrame) -> pd.DataFrame:
    members = {r: ["cancel my card", "pay a bill", "card lost"] for r in IDS}
    key = key.assign(unsupported_lemma_share=0.0)
    return analyse_rows(sheet_a, key, members, NLP)


def toy_analysis_inputs():
    summaries = ["Cancel my card", "Terminate my card", "Cancel my card", "Pay my bill"]
    a = sheet([9, 9, 9, 9], [0] * 4, [0, 0, 1, 0], [1] * 4, summaries, ["1. cancel my card"] * 4)
    b = sheet([9, 9, 9, 9], [0] * 4, [0, 0, 1, 0], [1] * 4, summaries, ["1. cancel my card"] * 4)
    key = KEY.assign(flag_unsupported=[False, True, False, False])
    return a, b, key


def test_flagged_and_reverse_tables_hold_exactly_the_right_rows():
    a, b, key = toy_analysis_inputs()
    key = key.assign(unsupported_lemma_share=[0.0, 0.5, 0.0, 0.0])
    analysis = analyse_rows(a, key, {r: ["cancel my card", "pay a bill", "card lost"] for r in IDS}, NLP)
    check_flags(analysis)
    flagged = flagged_table(analysis, {"a": a, "b": b})
    assert flagged["row_id"].tolist() == ["d-01-B"]
    assert flagged.loc[0, "trigger_lemmas"] == "terminate" and flagged.loc[0, "category"] == ""
    assert flagged.loc[0, ["unsupported_a", "unsupported_b"]].tolist() == [0, 0]
    reverse = reverse_table(analysis, {"a": a, "b": b})
    assert reverse["row_id"].tolist() == ["d-01-C"]  # rated unsupported, flag 0
    assert list(reverse.columns) == list(flagged.columns)
    s = paraphrase_summary(flagged, ["a", "b"])
    assert (s["flagged"], s["rated_by_all"], s["all_supported"], s["share_all_supported"]) == (1, 1, 1, 1.0)


def test_check_flags_raises_when_the_recomputation_differs_from_the_key():
    a, _, key = toy_analysis_inputs()
    analysis = analyse_rows(
        a, key.assign(unsupported_lemma_share=[0.0, 0.5, 0.0, 0.0]),
        {r: ["cancel my card", "pay a bill", "card lost"] for r in IDS}, NLP,
    )  # fmt: skip
    check_flags(analysis)
    wrong = analysis.assign(key_flag_unsupported=[0, 0, 1, 0])
    with pytest.raises(ValueError, match="d-01-B.*d-01-C|d-01-C.*d-01-B"):
        check_flags(wrong)
    with pytest.raises(ValueError, match="d-01-A"):
        check_flags(analysis.assign(key_unsupported_lemma_share=[0.3, 0.5, 0.0, 0.0]))


def test_paraphrase_summary_ignores_unrated_and_counts_supported():
    flagged = pd.DataFrame({"unsupported_a": [0, 0, 1, 0], "unsupported_b": [0, 1, 1, np.nan]})
    s = paraphrase_summary(flagged, ["a", "b"])
    assert (s["flagged"], s["rated_by_all"], s["all_supported"]) == (4, 3, 1)
    assert s["share_all_supported"] == pytest.approx(1 / 3)


def test_category_counts_and_unknown_category():
    table = pd.DataFrame({"category": ["paraphrase", "paraphrase", "unsupported", np.nan, "generalisation"]})
    counts = category_counts(table)
    assert counts["paraphrase"] == 2 and counts["unsupported"] == 1 and counts["generalisation"] == 1
    assert counts["unlabelled"] == 1 and counts["unshown_members"] == 0
    with pytest.raises(ValueError, match="unknown categories"):
        category_counts(pd.DataFrame({"category": ["synonym"]}))


def test_report_script_end_to_end_on_toy_data(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("human_eval_report_script", SCRIPTS / "human_eval_report.py")
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    a, b, key = toy_analysis_inputs()
    key = key.assign(unsupported_lemma_share=[0.0, 0.5, 0.0, 0.0])
    sheets, keys = tmp_path / "sheets", tmp_path / "keys"
    sheets.mkdir(), keys.mkdir()
    for dataset in ("clinc150_intent", "bank77"):
        key.assign(dataset=dataset).to_csv(keys / f"summary_audit_key_{dataset}.csv", index=False)
        a.to_csv(sheets / f"summary_audit_human_ann_{dataset}.csv", index=False)
        b.to_csv(sheets / f"summary_audit_human_bob_{dataset}.csv", index=False)
    monkeypatch.setattr(script, "load_members", lambda k, r, c: {i: ["cancel my card", "pay a bill"] for i in IDS})
    out = tmp_path / "out"
    text = script.report(["ann", "bob"], sheets, keys, tmp_path, tmp_path, out)
    assert "Human ratings by `ann`, `bob`" in text and "sample is fixed at 40" in text
    assert "n per dataset: clinc150_intent 4, bank77 4" in text
    assert "judged supported (unsupported = 0) by all raters: 1 (100%)" in text
    flagged = out / "paraphrase_flagged_bank77.csv"
    assert pd.read_csv(flagged)["row_id"].tolist() == ["d-01-B"]
    filled = pd.read_csv(flagged).assign(category="paraphrase")
    filled.to_csv(tmp_path / "filled.csv", index=False)
    again = script.report(["ann", "bob"], sheets, keys, tmp_path, tmp_path, out, category_files=[tmp_path / "filled.csv"])
    assert "Categories filled in `filled.csv`" in again
