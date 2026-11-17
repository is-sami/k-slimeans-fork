"""`scripts/timing_report.py` on hand-written fixed-workload directories and a hand-written logged run."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "timing_report.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("timing_report_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tr = _load_script()


def _write_logged_run(root: Path, batch_size: int = 4) -> str:
    """A one-seed logged run: 3 clusters, two summary steps; step 0 took 60 s (3 calls), step 1 40 s."""
    rel = "results/logged/stamp"
    path = root / rel
    path.mkdir(parents=True)
    config = {"name": "logged", "dataset": "d", "embedder": "e", "summarizer": {"type": "hf", "batch_size": batch_size}}
    (path / "config.yaml").write_text(yaml.safe_dump(config))
    trace = [
        {"seed": 0, "method": "k-SLMmeans", "step": 0, "summarize": False, "n_calls": 0, "summarizer_seconds": 0.0},
        {"seed": 0, "method": "k-SLMmeans", "step": 1, "summarize": True, "n_calls": 3, "summarizer_seconds": 60.0},
        {"seed": 0, "method": "k-SLMmeans", "step": 2, "summarize": True, "n_calls": 2, "summarizer_seconds": 40.0},
    ]
    (path / "trace.jsonl").write_text("".join(json.dumps(r) + "\n" for r in trace))
    (path / "metrics.jsonl").write_text(json.dumps({"seed": 0, "method": "k-SLMmeans", "acc": 0.5}) + "\n")
    row = {"seed": 0, "method": "k-SLMmeans", "summaries_evolution": [["a", "b", "c"], ["a", "b", "d"]]}
    (path / "summaries.jsonl").write_text(json.dumps(row) + "\n")
    return rel


def _write_workload(root: Path, name: str, run_dir: str, outputs: list[str], seconds: list[float], batch_size: int = 4,
                    idle: bool | None = True) -> Path:
    path = root / "results" / "fixed_workload" / name / "stamp"
    path.mkdir(parents=True)
    config = {
        "name": name,
        "source": {"run_dir": run_dir, "method": "k-SLMmeans", "seed": 0, "step": 0, "n_clusters": 3, "n_sent": 3},
        "summarizer": {"type": "hf", "model_id": "Qwen/Qwen3-0.6B", "batch_size": batch_size},
    }
    (path / "config.yaml").write_text(yaml.safe_dump(config))
    cost = [
        {"repeat": r, "n_calls": 3, "seconds": s, "input_tokens": 300, "output_tokens": 30, "peak_gpu_mem_gb": 5.0 + r,
         "peak_gpu_reserved_gb": 6.0 + r}
        for r, s in enumerate(seconds)
    ]
    (path / "cost.jsonl").write_text("".join(json.dumps(c) + "\n" for c in cost))
    (path / "outputs.jsonl").write_text(
        "".join(json.dumps({"repeat": r, "cluster": c, "summary": s}) + "\n" for r in range(len(seconds)) for c, s in enumerate(outputs))
    )
    (path / "surface.json").write_text(json.dumps({"identical_across_repeats": True, "n": 3}))
    (path / "environment.json").write_text(json.dumps({"gpu_name": "RTX", "summarizer": {"dtype": "torch.bfloat16"}}))
    gpu = {"non_torch_above_baseline_mib": 139.0}
    if idle is not None:
        gpu["idle_check"] = {"idle": idle}
    (path / "gpu.json").write_text(json.dumps(gpu))
    return path


def test_spread_reports_median_and_range():
    assert tr.spread([3.0, 1.0, 2.0], ".1f") == "2.0 (1.0-3.0)"
    assert tr.spread([2.5], ".1f") == "2.5"


def test_repeat_stats_divide_by_calls_and_seconds():
    stats = tr.repeat_stats([{"seconds": 30.0, "n_calls": 3, "output_tokens": 60}])
    assert stats == {"s_per_call": [10.0], "tok_per_s": [2.0], "total_s": [30.0]}


def test_compare_summaries_counts_and_lists_differences():
    same, differ, examples = tr.compare_summaries({0: "x", 1: "y", 2: "z"}, {0: "x", 1: "Y", 3: "w"})
    assert (same, differ) == (1, 1)
    assert examples == [(1, "y", "Y")]


def test_clip_collapses_whitespace_and_truncates():
    assert tr.clip("a\n  b") == "a b"
    assert len(tr.clip("x" * 500)) == tr.EXAMPLE_CHARS and tr.clip("x" * 500).endswith("...")


def test_rows_show_median_range_idle_and_memory_peak(tmp_path):
    run = _write_logged_run(tmp_path)
    w = tr.load_dir(_write_workload(tmp_path, "time_x", run, ["a", "b", "c"], [30.0, 60.0, 45.0]))
    assert "| time_x | Qwen3-0.6B | 4 | 3 | 15.00 (10.00-20.00) | 0.7 (0.5-1.0) | 45 (30-60) | yes |" == tr.speed_row(w)
    assert tr.setup_row(w) == (
        "| time_x | 4 | torch.bfloat16 | RTX | yes | 139 | 3 of 3 | 300 | 30 | 7.00 | 8.00 |"
    )


def test_idle_cell_distinguishes_busy_and_not_logged(tmp_path):
    run = _write_logged_run(tmp_path)
    busy = tr.load_dir(_write_workload(tmp_path, "busy", run, ["a"], [1.0], idle=False))
    old = tr.load_dir(_write_workload(tmp_path, "old", run, ["a"], [1.0], idle=None))
    assert tr.idle_cell(busy["gpu"]) == "no"
    assert tr.idle_cell(old["gpu"]) == "not logged"


def test_inflation_row_is_logged_over_fixed_median(tmp_path):
    run = _write_logged_run(tmp_path)
    w = tr.load_dir(_write_workload(tmp_path, "time_x", run, ["a", "b", "c"], [30.0, 20.0, 40.0]))
    assert tr.inflation_row(w, tmp_path) == "| Qwen3-0.6B | 4 | 3 | 60.0 | 30.0 (20.0-40.0) | 2.00 |"


def test_inflation_row_skips_other_batch_size_and_rejects_call_mismatch(tmp_path):
    run = _write_logged_run(tmp_path)
    other = tr.load_dir(_write_workload(tmp_path, "bs1", run, ["a"], [10.0], batch_size=1))
    assert tr.inflation_row(other, tmp_path) is None
    w = tr.load_dir(_write_workload(tmp_path, "bad", run, ["a"], [10.0]))
    w["cost"][0]["n_calls"] = 2
    with pytest.raises(ValueError, match="3 calls"):
        tr.inflation_row(w, tmp_path)


def test_main_prints_every_section(tmp_path, monkeypatch, capsys):
    run = _write_logged_run(tmp_path)
    a = _write_workload(tmp_path, "a", run, ["a", "b", "c"], [30.0, 30.0, 30.0])
    b = _write_workload(tmp_path, "b", run, ["a", "b", "X"], [20.0, 20.0, 20.0], batch_size=8)
    monkeypatch.setattr(
        sys, "argv",
        ["timing_report.py", str(a), str(b), "--root", str(tmp_path), "--logged", "--inflation", "--diff", str(a), str(b)],
    )
    tr.main()
    out = capsys.readouterr().out
    assert "- a: 3 identical, 0 differing (of 3)" in out
    assert "- b: 2 identical, 1 differing (of 3)" in out
    assert '- a against b: 2 identical, 1 differing (of 3)\n  - cluster 2: "c" vs "X"' in out
    assert "| Qwen3-0.6B | 4 | 3 | 60.0 | 30.0 (30.0-30.0) | 2.00 |" in out
    assert out.count("| Qwen3-0.6B | 8 |") == 1  # the batch-8 directory is in the speed table only, not the inflation table
