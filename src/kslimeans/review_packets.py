"""Review packets for the teammates' manual reading tasks (#50 case studies, #36 failure modes).

Everything here works on plain arrays and frames so it can be tested on tiny inputs; `scripts/export_review_packets.py`
loads the logged runs and writes the files. All sampling is seeded, so the packets are reproducible.

Step numbering is #33's: step 1 is the first summary step. For a record, the partition the step-1 summaries were written
from is `source_partition(0)` and the partition after the step's Lloyd block is `partition_after(0)`.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .runlog import RunRecord, members_by_cluster
from .synthesis import member_agreement

BLIND_NOTICE = "**Open this only after you have submitted your #34 ratings.**"
BLIND_REASON = (
    "This packet shows which model wrote which summary. The #34 hand check has to stay blind, so please finish and "
    "submit those ratings first."
)

# Purity-before bins of the synthesis (`add_bins`): upper edges, the last bin is open above 0.9.
PURITY_EDGES = (0.4, 0.6, 0.8, 0.9)
PURITY_BIN_NAMES = ("<= 0.4", "(0.4, 0.6]", "(0.6, 0.8]", "(0.8, 0.9]", "> 0.9")

TAG_COLUMNS = (
    "echoes_instruction",
    "mentions_cluster_or_questions",
    "quote_marks_or_markup",
    "copies_member_verbatim",
    "no_question_mark",
    "answers_instead_of_asking",
    "covers_one_subgroup",
    "adds_detail_no_member_has",
    "other",
    "notes",
)


# ------------------------------------------------------------------ partitions of a run


def step1_partitions(record: RunRecord) -> tuple[np.ndarray, np.ndarray]:
    """`(source, after)` labels of summary step 1: the partition it was written from and the one after its Lloyd block."""
    return record.source_partition(0), record.partition_after(0)


def check_same_partition(partitions: dict[str, np.ndarray], sha1s: dict[str, str | None] | None = None) -> None:
    """Raise `ValueError` unless every run's step-0 partition is identical (and, where logged, its `step0_sha1`).

    `partitions` maps a run label to the labels its step-1 summaries were written from. Packet B shows the same
    members next to six summaries, which is only valid if every run really started from one partition.
    """
    if not partitions:
        raise ValueError("no partitions to compare")
    (first_label, first), *rest = partitions.items()
    for label, labels in rest:
        if labels.shape != first.shape or not np.array_equal(labels, first):
            n_diff = "different lengths" if labels.shape != first.shape else f"{int((labels != first).sum())} documents differ"
            raise ValueError(f"step-0 partitions differ between {first_label!r} and {label!r}: {n_diff}")
    seen = {label: sha for label, sha in (sha1s or {}).items() if sha is not None}
    if len(set(seen.values())) > 1:
        raise ValueError(f"step0_sha1 differs between runs: {seen}")


def purity_of(labels: np.ndarray, gold: np.ndarray, k: int) -> np.ndarray:
    """Per cluster, the share of its members holding its majority gold intent (NaN for an empty cluster)."""
    return member_agreement(labels, labels, gold, k)


def step_change(source: np.ndarray, after: np.ndarray, gold: np.ndarray, k: int) -> pd.DataFrame:
    """Per source cluster: `purity`, `d_member_purity` (members' agreement with where they end up, minus purity)."""
    purity = purity_of(source, gold, k)
    return pd.DataFrame(
        {"cluster": np.arange(k), "purity": purity, "d_member_purity": member_agreement(source, after, gold, k) - purity}
    )


# ------------------------------------------------------------------ packet A: help / hurt selection


def select_cases(scores: pd.DataFrame, per_side: int, per_method_cap: int, method_order: list[str]) -> pd.DataFrame:
    """Pick the most helped and the most hurt (method, cluster) rows.

    `scores` has `method`, `cluster` and `score` (the change in member purity minus the no-replacement counterfactual).
    Per side, candidates are ranked by score (descending for helped, ascending for hurt; ties broken by the order of
    `method_order`, then cluster id) and taken greedily subject to at most `per_method_cap` per method. Pass 1 also
    skips a cluster id already taken on that side; if that leaves fewer than `per_side`, pass 2 fills the remainder
    from the same ranking without the distinct-id condition (the cap still applies). Only rows with a strictly
    positive (helped) or negative (hurt) score qualify, and NaN scores are ignored.

    Returns `side`, `rank` (1-based within side), `method`, `cluster`, `score`, `pass` (1 or 2).
    """
    order = {m: i for i, m in enumerate(method_order)}
    unknown = set(scores["method"]) - set(order)
    if unknown:
        raise ValueError(f"methods missing from method_order: {sorted(unknown)}")
    frame = scores.dropna(subset=["score"]).assign(_m=lambda d: d["method"].map(order))
    picked = []
    for side, ascending in (("helped", False), ("hurt", True)):
        pool = frame[frame["score"] > 0] if side == "helped" else frame[frame["score"] < 0]
        ranked = pool.sort_values(["score", "_m", "cluster"], ascending=[ascending, True, True])
        taken: list[tuple[str, int, float, int]] = []
        for pass_no in (1, 2):
            for row in ranked.itertuples():
                if len(taken) >= per_side:
                    break
                if any(t[0] == row.method and t[1] == row.cluster for t in taken):
                    continue
                if sum(t[0] == row.method for t in taken) >= per_method_cap:
                    continue
                if pass_no == 1 and any(t[1] == row.cluster for t in taken):
                    continue
                taken.append((row.method, row.cluster, row.score, pass_no))
        for rank, (method, cluster, score, pass_no) in enumerate(taken, start=1):
            picked.append({"side": side, "rank": rank, "method": method, "cluster": int(cluster), "score": score, "pass": pass_no})
    return pd.DataFrame(picked, columns=["side", "rank", "method", "cluster", "score", "pass"])


# ------------------------------------------------------------------ packet B: stratified sample


def purity_bins(purity: np.ndarray) -> np.ndarray:
    """Bin index (0-4, see `PURITY_BIN_NAMES`) of each purity; the bins are (lo, hi] with the first closed at 0."""
    return np.searchsorted(np.asarray(PURITY_EDGES), np.asarray(purity), side="left")


def stratified_sample(purity: np.ndarray, per_bin: int, seed: int) -> list[int]:
    """Cluster ids sampled without replacement, `per_bin` from each purity bin (all of a bin that has fewer).

    Returned bin by bin (ascending purity), ascending id within a bin. Empty clusters (NaN purity) are skipped.
    """
    purity = np.asarray(purity, dtype=float)
    bins = purity_bins(np.nan_to_num(purity, nan=-1.0))
    rng = np.random.default_rng(seed)
    chosen: list[int] = []
    for b in range(len(PURITY_BIN_NAMES)):
        ids = np.flatnonzero((bins == b) & ~np.isnan(purity))
        take = ids if len(ids) <= per_bin else rng.choice(ids, size=per_bin, replace=False)
        chosen.extend(sorted(int(i) for i in take))
    return chosen


# ------------------------------------------------------------------ members and intents


def sample_ids(ids: np.ndarray, n: int, rng: np.random.Generator) -> list[int]:
    """Up to `n` of `ids`, sampled without replacement, in ascending order."""
    ids = np.asarray(ids)
    if len(ids) <= n:
        return sorted(int(i) for i in ids)
    return sorted(int(i) for i in rng.choice(ids, size=n, replace=False))


def intent_composition(gold_members: np.ndarray, names: list[str], top: int = 5) -> list[tuple[str, int]]:
    """The `top` most common intents among `gold_members` as (name, count); ties by lower intent id."""
    counts = np.bincount(np.asarray(gold_members), minlength=len(names))
    order = np.argsort(-counts, kind="stable")[:top]
    return [(names[i], int(counts[i])) for i in order if counts[i] > 0]


def composition_text(composition: list[tuple[str, int]], size: int) -> str:
    return ", ".join(f"{name} {count} ({count / size:.0%})" for name, count in composition)


def movers(
    source: np.ndarray, after: np.ndarray, gold: np.ndarray, cluster: int, k: int
) -> dict[str, np.ndarray | int]:
    """Who left and who arrived at `cluster` over the step's Lloyd block.

    `left`: documents in `source == cluster` with `after != cluster`; `left_majority`: the majority gold intent of the
    cluster each went to (after the step); `arrived`: documents with `after == cluster` and `source != cluster`.
    """
    n_gold = int(gold.max()) + 1
    majority_after = np.array(
        [np.bincount(gold[m], minlength=n_gold).argmax() if len(m) else -1 for m in members_by_cluster(after, k)]
    )
    left = np.flatnonzero((source == cluster) & (after != cluster))
    arrived = np.flatnonzero((after == cluster) & (source != cluster))
    return {"left": left, "left_majority": majority_after[after[left]], "arrived": arrived}


# ------------------------------------------------------------------ Markdown


def md_escape(text: str) -> str:
    """Make `text` render literally inside one Markdown line (backslash-escapes, collapsed whitespace)."""
    text = " ".join(str(text).split())
    out = []
    for ch in text:
        if ch in "\\`*_[]<>|~$":
            out.append("\\" + ch)
        elif ch == "&":
            out.append("&amp;")
        else:
            out.append(ch)
    return "".join(out)


def fenced(text: str) -> str:
    """`text` verbatim in a code fence long enough not to be closed by backticks inside it."""
    longest = max((len(run) for run in _backtick_runs(text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{text.rstrip()}\n{fence}"


def _backtick_runs(text: str) -> list[str]:
    runs, current = [], ""
    for ch in text:
        if ch == "`":
            current += ch
        elif current:
            runs.append(current)
            current = ""
    if current:
        runs.append(current)
    return runs


def member_bullets(ids: list[int], texts: list[str], gold: np.ndarray, names: list[str], extra=None) -> str:
    """One bullet per document: the escaped text, then its gold intent (and `extra(i)` if given)."""
    lines = []
    for i in ids:
        tail = f"gold: {md_escape(names[gold[i]])}"
        if extra is not None:
            tail += f"; {extra(i)}"
        lines.append(f"- {md_escape(texts[i])} _({tail})_")
    return "\n".join(lines) if lines else "_none_"


@dataclass(frozen=True)
class CaseInputs:
    """What `render_case` needs for one (method, cluster) of packet A."""

    side: str
    rank: int
    method_label: str
    cluster: int
    size: int
    purity: float
    score: float
    d_member_purity: float
    cf_d_member_purity: float
    summary: str
    composition: list[tuple[str, int]]
    sample: list[int]
    n_left: int
    left: list[int]
    n_arrived: int
    arrived: list[int]


def render_case(case: CaseInputs, texts: list[str], gold: np.ndarray, names: list[str], majority_of_destination, source_of) -> str:
    """The Markdown block of one packet-A case."""
    title = f"{case.side.capitalize()} {case.rank}: {case.method_label}, cluster {case.cluster}"
    return "\n".join(
        [
            f"### {title}",
            "",
            f"- **Size:** {case.size} members; **purity before:** {case.purity:.2f}",
            f"- **Selection number:** {case.score:+.3f} = change in member purity {case.d_member_purity:+.3f} "
            f"minus the no-replacement counterfactual {case.cf_d_member_purity:+.3f}",
            f"- **Gold intents before:** {md_escape(composition_text(case.composition, case.size))}",
            "",
            "**Summary**",
            "",
            fenced(case.summary),
            "",
            f"**Sample of {len(case.sample)} members before the step**",
            "",
            member_bullets(case.sample, texts, gold, names),
            "",
            f"**Left the cluster** ({case.n_left} of {case.size}; showing {len(case.left)}), with the majority intent of the "
            "cluster each went to",
            "",
            member_bullets(case.left, texts, gold, names, extra=lambda i: f"went to a cluster mostly about {md_escape(majority_of_destination(i))}"),
            "",
            f"**Arrived** ({case.n_arrived} documents; showing {len(case.arrived)})",
            "",
            member_bullets(case.arrived, texts, gold, names, extra=lambda i: f"came from cluster {source_of(i)}"),
            "",
        ]
    )


def csv_text(header: list[str], rows: list[list]) -> str:
    """CSV with `\\n` line ends (stable across platforms)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue()


def tagging_rows(clusters: list[int], sizes: dict[int, int], summaries: dict[tuple[int, str, str], str], models: list[str], prompts: list[str]) -> list[list]:
    """One row per (cluster, model, prompt): ids, the summary text and an empty cell per tag column."""
    rows = []
    for c in clusters:
        for model in models:
            for prompt in prompts:
                rows.append([c, sizes[c], model, prompt, summaries[(c, model, prompt)]] + [""] * len(TAG_COLUMNS))
    return rows
