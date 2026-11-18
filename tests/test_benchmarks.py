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


def test_benchmark_records_manager_routing(tmp_path: Path):
    benchmark = Benchmark(tmp_path / "benchmarks.json")
    benchmark.record_delegation("manager_llm", "Market Research Specialist", "research")
    data = benchmark.finish()

    assert len(data["manager_delegation_history"]) == 1
    route = data["manager_delegation_history"][0]
    assert route["delegated_by"] == "manager_llm"
    assert route["delegated_to"] == "Market Research Specialist"
    assert route["task"] == "research"
