"""Tables for the timing write-up (docs/results/cost_timing.md) from fixed-workload directories (#35, parts 3 and 4).

Reads output directories of `scripts/fixed_workload.py` (`config.yaml`, `cost.jsonl`, `outputs.jsonl`, `gpu.json`,
`environment.json`) and, for the comparisons with a logged run, that run's `trace.jsonl` and `summaries.jsonl`.
It prints markdown, one section per question:

- **Fixed-workload table**: per directory, the median and the range over its repeats of seconds per call, output
  tokens per second and total seconds, with the setup, the idle check, the counts and the memory peaks.
- **Summaries against the logged run** (`--logged`): how many of the workload's summaries (repeat 0) equal the
  logged run's summaries of the same clusters, with examples of the differing ones.
- **Inflation of the logged timing** (`--inflation`): the logged run's own `summarizer_seconds` for the workload's
  step (its `trace.jsonl` row) against the median of the fixed workload, for directories that ran at the logged
  run's batch size. The logged step is one call of the summarizer per step, including the first call's one-off
  CUDA start-up, which the fixed workload's warm-up pass excludes.
- **Two directories against each other** (`--diff A B`, repeatable): identical and differing summaries, e.g. one
  model at two batch sizes.

The run directories named in `config.yaml` (`source.run_dir`) are resolved against `--root` (default: the current
directory, the checkout that holds `results/`).

Usage:

    python scripts/timing_report.py results/fixed_workload/time_*/* --logged --inflation \\
        --diff results/fixed_workload/time_0.6b_bs1/<stamp> results/fixed_workload/time_0.6b_bs8/<stamp>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median

from kslimeans.runlog import load_run
from kslimeans.workload import load_workload_dir, pick_record

EXAMPLE_CHARS = 110


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def load_dir(path: str | Path) -> dict:
    """`load_workload_dir` plus the directory's `environment.json` and `gpu.json` (`{}` when absent)."""
    w = load_workload_dir(path)
    w["environment"] = _read_json(w["path"] / "environment.json")
    w["gpu"] = _read_json(w["path"] / "gpu.json")
    return w


def outputs_by_cluster(path: str | Path, repeat: int = 0) -> dict[int, str]:
    """Cluster id to summary for one repeat of a directory's `outputs.jsonl`."""
    with open(Path(path) / "outputs.jsonl") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    return {row["cluster"]: row["summary"] for row in rows if row["repeat"] == repeat}


def spread(values: list[float], spec: str) -> str:
    """`median (min-max)`; just the value when there is one repeat."""
    if len(values) == 1:
        return f"{values[0]:{spec}}"
    return f"{median(values):{spec}} ({min(values):{spec}}-{max(values):{spec}})"


def repeat_stats(cost: list[dict]) -> dict[str, list[float]]:
    """Per repeat: seconds per call, output tokens per second, total seconds."""
    return {
        "s_per_call": [row["seconds"] / row["n_calls"] for row in cost],
        "tok_per_s": [row["output_tokens"] / row["seconds"] for row in cost],
        "total_s": [row["seconds"] for row in cost],
    }


def idle_cell(gpu: dict) -> str:
    idle = (gpu.get("idle_check") or {}).get("idle")
    return "not logged" if idle is None else ("yes" if idle else "no")


def model_name(w: dict) -> str:
    return str(w["config"]["summarizer"].get("model_id")).rsplit("/", 1)[-1]


def speed_row(w: dict) -> str:
    cfg, cost = w["config"], w["cost"]
    s = repeat_stats(cost)
    return (
        f"| {cfg['name']} | {model_name(w)} | {cfg['summarizer'].get('batch_size')} | {len(cost)} "
        f"| {spread(s['s_per_call'], '.2f')} | {spread(s['tok_per_s'], '.1f')} | {spread(s['total_s'], '.0f')} "
        f"| {'yes' if w['surface']['identical_across_repeats'] else 'NO'} |"
    )


def setup_row(w: dict) -> str:
    cfg, cost, env, gpu = w["config"], w["cost"], w["environment"], w["gpu"]
    peak = [row["peak_gpu_mem_gb"] for row in cost if row.get("peak_gpu_mem_gb") is not None]
    reserved = [row["peak_gpu_reserved_gb"] for row in cost if row.get("peak_gpu_reserved_gb") is not None]
    above = gpu.get("non_torch_above_baseline_mib")
    return (
        f"| {cfg['name']} | {cfg['summarizer'].get('batch_size')} | {(env.get('summarizer') or {}).get('dtype', 'n/a')} "
        f"| {env.get('gpu_name', 'n/a')} | {idle_cell(gpu)} | {'n/a' if above is None else f'{above:.0f}'} "
        f"| {cost[0]['n_calls']} of {cfg['source']['n_clusters']} | {cost[0]['input_tokens']:,} | {cost[0]['output_tokens']:,} "
        f"| {max(peak):.2f} | {max(reserved):.2f} |"
        if peak and reserved
        else f"| {cfg['name']} | {cfg['summarizer'].get('batch_size')} | n/a | n/a | {idle_cell(gpu)} | n/a | n/a | n/a | n/a | n/a | n/a |"
    )


SPEED_HEADER = (
    "| Setting | Model | Batch | Repeats | s per call, median (range) | Output tok/s, median (range) "
    "| Total s, median (range) | Same summaries in every repeat |\n"
    "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |"
)
SETUP_HEADER = (
    "| Setting | Batch | dtype | GPU | Idle at start | Max non-torch MiB above baseline | Calls "
    "| Input tokens | Output tokens | Peak GB | Reserved GB |\n"
    "| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"
)


def compare_summaries(a: dict[int, str], b: dict[int, str]) -> tuple[int, int, list[tuple[int, str, str]]]:
    """`(identical, differing, differing examples)` over the clusters both sides have, in cluster order."""
    shared = sorted(a.keys() & b.keys())
    differing = [(c, a[c], b[c]) for c in shared if a[c] != b[c]]
    return len(shared) - len(differing), len(differing), differing


def clip(text: str) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= EXAMPLE_CHARS else text[: EXAMPLE_CHARS - 3] + "..."


def format_comparison(title: str, same: int, differ: int, examples: list, n_examples: int = 3) -> str:
    lines = [f"- {title}: {same} identical, {differ} differing (of {same + differ})"]
    for cluster, left, right in examples[:n_examples]:
        lines.append(f"  - cluster {cluster}: \"{clip(left)}\" vs \"{clip(right)}\"")
    return "\n".join(lines)


def logged_run(w: dict, root: Path):
    """`(runlog, record)` of the logged run the workload was cut from."""
    src = w["config"]["source"]
    runlog = load_run(root / src["run_dir"])
    return runlog, pick_record(runlog, src["method"], src["seed"])


def logged_outputs(record, step: int) -> dict[int, str]:
    return {c: s for c, s in enumerate(record.summaries_evolution[step]) if s is not None}


def logged_step_seconds(record, step: int) -> tuple[float, int]:
    """`(summarizer_seconds, n_calls)` of the `step`-th summary step's trace row (rows with `summarize` set)."""
    rows = [row for row in record.trace if row.get("summarize")]
    return rows[step]["summarizer_seconds"], rows[step]["n_calls"]


def inflation_row(w: dict, root: Path) -> str | None:
    """Logged step seconds against the fixed workload's median at the logged batch size; None at another one."""
    runlog, record = logged_run(w, root)
    logged_bs = runlog.config["summarizer"].get("batch_size")
    if w["config"]["summarizer"].get("batch_size") != logged_bs:
        return None
    step = w["config"]["source"]["step"]
    logged_s, logged_calls = logged_step_seconds(record, step)
    if logged_calls != w["cost"][0]["n_calls"]:
        raise ValueError(f"{w['path']}: logged step has {logged_calls} calls, the workload {w['cost'][0]['n_calls']}")
    seconds = [row["seconds"] for row in w["cost"]]
    return (
        f"| {model_name(w)} | {logged_bs} | {logged_calls} | {logged_s:.1f} | {median(seconds):.1f} "
        f"({min(seconds):.1f}-{max(seconds):.1f}) | {logged_s / median(seconds):.2f} |"
    )


INFLATION_HEADER = (
    "| Model | Batch | Calls | Logged step s (trace `summarizer_seconds`) | Fixed workload s, median (range) "
    "| Logged / fixed workload |\n| --- | ---: | ---: | ---: | ---: | ---: |"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dirs", nargs="+", metavar="WORKLOAD_DIR")
    parser.add_argument("--root", default=".", help="checkout that holds results/ (default: the current directory)")
    parser.add_argument("--logged", action="store_true", help="compare each directory's summaries with the logged run's")
    parser.add_argument("--inflation", action="store_true", help="logged step seconds against the fixed workload")
    parser.add_argument("--diff", nargs=2, action="append", default=[], metavar=("A", "B"),
                        help="compare the summaries of two workload directories (repeatable)")
    args = parser.parse_args()
    root = Path(args.root)

    workloads = [load_dir(path) for path in args.dirs]
    print(SPEED_HEADER)
    print("\n".join(speed_row(w) for w in workloads))
    print()
    print(SETUP_HEADER)
    print("\n".join(setup_row(w) for w in workloads))

    if args.logged:
        print("\nSummaries (repeat 0) against the logged run's:\n")
        for w in workloads:
            _, record = logged_run(w, root)
            same, differ, examples = compare_summaries(
                outputs_by_cluster(w["path"]), logged_outputs(record, w["config"]["source"]["step"])
            )
            print(format_comparison(w["config"]["name"], same, differ, examples))
    for a, b in args.diff:
        wa, wb = load_workload_dir(a), load_workload_dir(b)
        same, differ, examples = compare_summaries(outputs_by_cluster(a), outputs_by_cluster(b))
        print("\n" + format_comparison(f"{wa['config']['name']} against {wb['config']['name']}", same, differ, examples))
    if args.inflation:
        rows = [(w, inflation_row(w, root)) for w in workloads]
        print("\nLogged timing against the fixed workload at the logged batch size:\n")
        print(INFLATION_HEADER)
        print("\n".join(row for _, row in rows if row))


if __name__ == "__main__":
    main()
