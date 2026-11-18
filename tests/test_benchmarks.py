"""Tests for benchmark JSON logging."""

import json
from pathlib import Path

from benchmarks.benchmark import Benchmark


def test_benchmark_json_creation(tmp_path: Path):
    path = tmp_path / "benchmarks.json"
    benchmark = Benchmark(path)
    benchmark.record_task("test_task", "completed", 0.125)
    data = benchmark.finish()

    assert path.exists()
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved == data
    assert "execution_start" in saved
    assert "execution_end" in saved
    assert "total_execution_duration_seconds" in saved
    assert saved["task_durations"]["test_task"]["duration_seconds"] == 0.125
    assert saved["task_execution_status"]["test_task"] == "completed"
