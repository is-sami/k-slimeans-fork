#!/usr/bin/env python
"""Export the two review packets for the teammates' manual reading tasks (CLINC150, seed 0, summary step 1).

Packet A (#50, cluster case studies): the 10 most helped and the 10 most hurt clusters, measured as the step's change in
member purity minus the no-replacement counterfactual, over the five runs with an exact #33 replay.
Packet B (#36, failure modes by size and prompt): about 25 clusters sampled by purity before, with the six summaries of
the 0.6B / 1.7B / 4B under the old and the clearer prompt, plus a tagging template CSV.

CPU only, no model calls and no embeddings: it reads the logged partitions and summaries, and takes the counterfactual
(plain Lloyd from the step-0 state, the same for every method of a seed) from the joined per-cluster CSV of the
synthesis. See `kslimeans.review_packets` for the selection and formatting logic.

    python scripts/export_review_packets.py --results-root ../../k-slimeans/results --out-dir docs/review_packets
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from kslimeans import review_packets as rp
from kslimeans.data import load_dataset
from kslimeans.runlog import RunLog, RunRecord, load_run, members_by_cluster

SEED = 0
SAMPLE_SEED = 20261119  # base seed of every member sample
N_SAMPLE = 10
PER_SIDE = 10
PER_METHOD_CAP = 4
PER_BIN = 5
JOINED_CSV = "gpu_reruns/50/synthesis_per_cluster.csv"
DATASET = "clinc150_intent"

# Run directories under the results root (the Reproduce section of docs/results/synthesis.md).
RUNS = {
    "lsa": "clinc150_lsa/20261027-174631",
    "old-0.6b": "clinc150_qwen3-0.6b/20261027-190908",
    "old-1.7b": "clinc150_qwen3-1.7b/20261027-202532",
    "old-4b": "clinc150_qwen3-4b/20261027-221042",
    "v2-0.6b": "clinc150_v2_qwen3-0.6b/20261112-200926",
    "v2-1.7b": "clinc150_v2_qwen3-1.7b/20261112-204127",
    "v2-4b": "clinc150_v2_qwen3-4b/20261112-181256",
}
LABELS = {
    "lsa": "extractive (LSA)",
    "old-0.6b": "Qwen3-0.6B, old prompt",
    "old-1.7b": "Qwen3-1.7B, old prompt",
    "old-4b": "Qwen3-4B, old prompt",
    "v2-0.6b": "Qwen3-0.6B, clearer prompt",
    "v2-1.7b": "Qwen3-1.7B, clearer prompt",
    "v2-4b": "Qwen3-4B, clearer prompt",
}
PACKET_A_RUNS = ["lsa", "old-0.6b", "old-1.7b", "old-4b", "v2-4b"]  # the runs with an exact #33 replay
PACKET_B_RUNS = [  # (run key, model, prompt)
    ("old-0.6b", "Qwen3-0.6B", "old"),
    ("v2-0.6b", "Qwen3-0.6B", "clearer"),
    ("old-1.7b", "Qwen3-1.7B", "old"),
    ("v2-1.7b", "Qwen3-1.7B", "clearer"),
    ("old-4b", "Qwen3-4B", "old"),
    ("v2-4b", "Qwen3-4B", "clearer"),
]
REGENERATE = "python scripts/export_review_packets.py --results-root ../../k-slimeans/results --out-dir docs/review_packets"

HOW_TO_WRITE = """\
For each cluster, write 3 to 5 lines:

- what the cluster was (which intents, and how mixed);
- what the summary covers and what it misses;
- whether the members that left were the ones the summary didn't cover;
- a one-line verdict (helped because ..., hurt because ...).

Then add a short paragraph across all 20: what the helped cases have in common, what the hurt ones have in common, and
**any case that contradicts the synthesis**. Flag those clearly; they matter most. Read `docs/results/synthesis.md`
section 9 first for context. Deliver `docs/results/synthesis_case_studies.md` in a PR (#50). Don't run anything or change
the analysis code.\
"""


def seed_record(runlog: RunLog) -> RunRecord:
    """The summarizing record of `SEED` (the baselines in the same log have no summaries)."""
    records = [r for m in runlog.methods for r in runlog.method_records(m) if r.seed == SEED and r.summaries_evolution]
    if len(records) != 1:
        raise ValueError(f"{runlog.path}: expected one summarizing record for seed {SEED}, found {len(records)}")
    return records[0]


def load_records(root: Path, keys: list[str]) -> dict[str, RunRecord]:
    return {key: seed_record(load_run(root / RUNS[key])) for key in keys}


def step0_sha1s(root: Path, keys: list[str]) -> dict[str, str | None]:
    """The logged `step0_sha1` of each run's seed (on its k-means baseline row, if any row carries it)."""
    out = {}
    for key in keys:
        log = load_run(root / RUNS[key])
        shas = {r.metrics.get("step0_sha1") for r in log.records.values() if r.seed == SEED} - {None}
        if len(shas) > 1:
            raise ValueError(f"{key}: several step0_sha1 values for seed {SEED}: {sorted(shas)}")
        out[key] = shas.pop() if shas else None
    return out


# ------------------------------------------------------------------ packet A


def counterfactual(joined_csv: Path, k: int) -> np.ndarray:
    """Per cluster, `cf_d_member_purity` of seed 0 step 1; asserted identical across the methods that carry it."""
    cols = ["dataset", "seed", "step", "cluster", "method_id", "cf_d_member_purity"]
    df = pd.read_csv(joined_csv, usecols=cols, low_memory=False)
    df = df[(df["dataset"] == DATASET) & (df["seed"] == SEED) & (df["step"] == 1)].dropna(subset=["cf_d_member_purity"])
    spread = df.groupby("cluster")["cf_d_member_purity"].agg(["min", "max", "count"])
    if len(spread) != k or (spread["max"] - spread["min"]).max() > 1e-9:
        raise ValueError(f"{joined_csv}: the counterfactual is not one value per cluster ({len(spread)} clusters)")
    return spread["min"].sort_index().to_numpy()


def build_packet_a(root: Path, ds, joined_csv: Path) -> tuple[str, list[list]]:
    records = load_records(root, PACKET_A_RUNS)
    k = len(next(iter(records.values())).summaries_evolution[0])
    cf = counterfactual(joined_csv, k)
    gold, names, texts = ds.labels, ds.label_names, ds.texts

    parts = {key: rp.step1_partitions(rec) for key, rec in records.items()}
    rp.check_same_partition({key: p[0] for key, p in parts.items()})
    frames = []
    for key, (source, after) in parts.items():
        change = rp.step_change(source, after, gold, k)
        frames.append(change.assign(method=key, cf=cf, score=change["d_member_purity"] - cf))
    allrows = pd.concat(frames, ignore_index=True)
    picks = rp.select_cases(allrows, PER_SIDE, PER_METHOD_CAP, PACKET_A_RUNS)
    detail = allrows.set_index(["method", "cluster"])

    blocks, csv_rows = [], []
    for pick in picks.itertuples():
        key, c = pick.method, pick.cluster
        source, after = parts[key]
        members = np.flatnonzero(source == c)
        rng = np.random.default_rng([SAMPLE_SEED, PACKET_A_RUNS.index(key), c])
        mv = rp.movers(source, after, gold, c, k)
        left_ids = rp.sample_ids(mv["left"], N_SAMPLE, rng)
        arrived_ids = rp.sample_ids(mv["arrived"], N_SAMPLE, rng)
        majority = dict(zip(mv["left"].tolist(), mv["left_majority"].tolist()))
        row = detail.loc[(key, c)]
        case = rp.CaseInputs(
            side=pick.side, rank=pick.rank, method_label=LABELS[key], cluster=c, size=len(members),
            purity=float(row["purity"]), score=float(pick.score), d_member_purity=float(row["d_member_purity"]),
            cf_d_member_purity=float(row["cf"]), summary=records[key].summaries_evolution[0][c] or "",
            composition=rp.intent_composition(gold[members], names), sample=rp.sample_ids(members, N_SAMPLE, rng),
            n_left=len(mv["left"]), left=left_ids, n_arrived=len(mv["arrived"]), arrived=arrived_ids,
        )  # fmt: skip
        blocks.append(rp.render_case(case, texts, gold, names, lambda i, m=majority: names[m[i]], lambda i, s=source: int(s[i])))
        csv_rows.append([pick.side, pick.rank, LABELS[key], c, case.size, f"{case.purity:.4f}", f"{case.score:.4f}",
                         f"{case.d_member_purity:.4f}", f"{case.cf_d_member_purity:.4f}", case.n_left, case.n_arrived,
                         rp.composition_text(case.composition, case.size), case.summary])  # fmt: skip
    return render_packet_a(blocks, picks), csv_rows


def render_packet_a(blocks: list[str], picks: pd.DataFrame) -> str:
    per_method = picks.groupby(["side", "method"]).size()
    counts = "; ".join(
        f"{side}: " + ", ".join(f"{LABELS[m]} ({n})" for (s, m), n in per_method.items() if s == side) for side in ("helped", "hurt")
    )
    n_pass2 = int((picks["pass"] == 2).sum())
    head = f"""{rp.BLIND_NOTICE}

# Cluster case studies, CLINC150 seed 0, step 1 (issue #50, for Samiksha)

{rp.BLIND_REASON}

Regenerate: `{REGENERATE}` (reads the gitignored logged runs of the main checkout; `scripts/export_review_packets.py`).

## How the clusters were chosen

The rule was fixed before any text was read and uses numbers only.

- **Runs:** the five CLINC150 runs with an exact #33 replay: extractive (LSA), Qwen3 0.6B, 1.7B and 4B with the old
  prompt, and Qwen3 4B with the clearer prompt (#46). Seed 0, first summary step (step 1 in #33's numbering). All five
  start from the same step-0 partition, so cluster `c` has the same members in each; this is checked when the packet is
  built.
- **Measure:** for a cluster, the share of its members whose gold intent is the majority intent of the cluster they are in
  after the step's Lloyd block, minus the cluster's purity before (`d_member_purity`, `synthesis.md` section 1); then minus
  the same change under the no-replacement counterfactual (plain Lloyd from the same step-0 state, `synthesis.md` section
  5). That difference is the **selection number**. Positive means helped, negative hurt.
- **Rule:** the 10 largest positive and the 10 most negative selection numbers over all (run, cluster) pairs, with at most
  {PER_METHOD_CAP} per run on each side. Candidates are taken in rank order; a candidate is skipped if its run already has
  {PER_METHOD_CAP} on that side, or (first pass) if its cluster id is already on that side. If the first pass cannot fill 10,
  a second pass takes the next-ranked candidates without the distinct-id condition (the cap still holds).
  Equal scores are ordered by run (LSA, 0.6B, 1.7B, 4B, 4B clearer prompt) and then by cluster id.
- **This packet:** {counts}. {n_pass2} of the 20 came from the second pass (a repeated cluster id on its side).
- **Purity ceiling:** a cluster with purity above 0.9 cannot be helped by much (purity cannot exceed 1), so the helped side is
  mostly clusters that were mixed before, and the hurt side is where a pure cluster had room to fall. This selection
  therefore shows the extremes of one measure, not a random sample of clusters.
- **Not shown:** the automatic quality scores and flags (#34). Judge coverage yourself.
- **Members:** samples of up to {N_SAMPLE} are random with a fixed seed. "Left" members are those of the cluster that sit in
  another cluster after the Lloyd block; for each, the majority intent of its new cluster is given. "Arrived" members are
  in the cluster after the block and were elsewhere before.
- LSA is called "extractive": its summary is a few sentences copied from the members.

## How to write each case

{HOW_TO_WRITE}

## The 20 clusters

"""
    return head + "\n".join(blocks)


# ------------------------------------------------------------------ packet B


def build_packet_b(root: Path, ds) -> tuple[str, str, dict]:
    keys = [key for key, _, _ in PACKET_B_RUNS]
    records = load_records(root, keys)
    sha1s = step0_sha1s(root, keys)
    parts = {key: rp.step1_partitions(rec) for key, rec in records.items()}
    rp.check_same_partition({key: p[0] for key, p in parts.items()}, sha1s)
    source = parts[keys[0]][0]
    k = len(records[keys[0]].summaries_evolution[0])
    gold, names, texts = ds.labels, ds.label_names, ds.texts
    purity = rp.purity_of(source, gold, k)
    clusters = rp.stratified_sample(purity, PER_BIN, SAMPLE_SEED)
    by_cluster = members_by_cluster(source, k)
    models = list(dict.fromkeys(m for _, m, _ in PACKET_B_RUNS))
    prompts = list(dict.fromkeys(p for _, _, p in PACKET_B_RUNS))

    summaries = {}
    blocks = []
    sizes = {}
    for c in clusters:
        members = by_cluster[c]
        sizes[c] = len(members)
        rng = np.random.default_rng([SAMPLE_SEED, 1000, c])
        sample = rp.sample_ids(members, N_SAMPLE, rng)
        lines = []
        for key, model, prompt in PACKET_B_RUNS:
            text = records[key].summaries_evolution[0][c] or ""
            summaries[(c, model, prompt)] = text
            lines += [f"**{model}, {prompt} prompt**", "", rp.fenced(text), ""]
        bin_name = rp.PURITY_BIN_NAMES[int(rp.purity_bins(purity[c : c + 1])[0])]
        blocks.append(
            "\n".join(
                [
                    f"### Cluster {c}",
                    "",
                    f"- **Size:** {len(members)} members; **purity before:** {purity[c]:.2f} (bin {bin_name})",
                    f"- **Gold intents:** {rp.md_escape(rp.composition_text(rp.intent_composition(gold[members], names, 4), len(members)))}",
                    "",
                    f"**{len(sample)} members**",
                    "",
                    rp.member_bullets(sample, texts, gold, names),
                    "",
                    *lines,
                ]
            )
        )
    n_bins = {name: int(((rp.purity_bins(np.nan_to_num(purity, nan=-1)) == b) & ~np.isnan(purity)).sum())
              for b, name in enumerate(rp.PURITY_BIN_NAMES)}  # fmt: skip
    sha = next((s for s in sha1s.values() if s), None)
    head = f"""{rp.BLIND_NOTICE}

# Failure modes by size and prompt, CLINC150 seed 0, step 1 (issue #36, for Nabin)

{rp.BLIND_REASON}

Regenerate: `{REGENERATE}`.

## What this is

- {len(clusters)} clusters of the 150 at the first summary step, seed 0, sampled with a fixed seed ({SAMPLE_SEED}),
  {PER_BIN} from each purity-before bin (all clusters in a bin if it has fewer). Clusters per bin out of 150: {", ".join(f"{n} {b}" for b, n in n_bins.items())}.
- **Same members in every run.** All six runs start step 1 from one step-0 partition. This was checked from the logs
  when the packet was built: the step-0 assignments of the six runs are identical and their logged `step0_sha1` agree
  ({sha}). So each cluster id has the same members under all six summaries.
- Per cluster: its size, purity before, the gold intents, {N_SAMPLE} sample members (random, fixed seed, with their gold
  intent), and the six summaries exactly as written, in a code block so quote marks and line breaks stay visible.
- The automatic quality scores and flags (#34) are not shown.
- The tagging template is `size_failure_modes_tags.csv`: one row per (cluster, model, prompt), the summary text, and an
  empty 0/1 column per tag ({", ".join(rp.TAG_COLUMNS[:-2])}) plus `other` (say what) and `notes`.
  Tags from the #36 comment: echoes the instruction; talks about "the cluster" or "the questions"; quote marks or
  markup; copies a member word for word; no "?"; answers instead of asking; covers only one sub-group; adds a detail no
  member has; other.
- Read `docs/results/prompt_test.md` sections 5 to 6 and 8.3 and `clinc150_summarizers.md` section 2.4 only after tagging.

## The clusters

"""
    csv = rp.csv_text(
        ["cluster", "size", "model", "prompt", "summary", *rp.TAG_COLUMNS],
        rp.tagging_rows(clusters, sizes, summaries, models, prompts),
    )
    return head + "\n".join(blocks), csv, {"clusters": clusters, "step0_sha1": sha}


# ------------------------------------------------------------------ main


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results-root", default="../../k-slimeans/results", help="directory holding the run directories")
    parser.add_argument("--joined-csv", default=None, help=f"joined per-cluster CSV (default: <root>/{JOINED_CSV})")
    parser.add_argument("--out-dir", default="docs/review_packets")
    args = parser.parse_args()
    root = Path(args.results_root)
    joined = Path(args.joined_csv) if args.joined_csv else root / JOINED_CSV
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ds = load_dataset(DATASET)

    md_a, rows_a = build_packet_a(root, ds, joined)
    (out / "case_studies_step1_seed0.md").write_text(md_a)
    header_a = ["side", "rank", "method", "cluster", "size", "purity_before", "selection_number", "d_member_purity",
                "counterfactual_d_member_purity", "n_left", "n_arrived", "gold_intents", "summary"]  # fmt: skip
    (out / "case_studies_step1_seed0.csv").write_text(rp.csv_text(header_a, rows_a))

    md_b, csv_b, info = build_packet_b(root, ds)
    (out / "size_failure_modes_step1_seed0.md").write_text(md_b)
    (out / "size_failure_modes_tags.csv").write_text(csv_b)
    print(f"packet A: {len(rows_a)} cases; packet B: {len(info['clusters'])} clusters {info['clusters']}, step0_sha1 {info['step0_sha1']}")


if __name__ == "__main__":
    main()
