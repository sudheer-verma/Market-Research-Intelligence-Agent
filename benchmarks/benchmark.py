"""Structured JSON benchmark logging."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class Benchmark:
    def __init__(self, output_path: str | Path):
        self.output_path = Path(output_path)
        self.started_wall = datetime.now(timezone.utc).isoformat()
        self.started_mono = time.perf_counter()
        self.task_times: dict[str, dict[str, Any]] = {}
        self.errors: list[dict[str, str]] = []
        self.manager_history: list[dict[str, Any]] = []
        self.pdf_duration_seconds: float | None = None

    def record_task(self, name: str, status: str, duration: float, error: str | None = None) -> None:
        entry = {"status": status, "duration_seconds": round(duration, 6)}
        if error:
            entry["error"] = error
        self.task_times[name] = entry

    def record_error(self, error: Exception | str) -> None:
        self.errors.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(error),
        })

    def finish(self) -> dict[str, Any]:
        ended_wall = datetime.now(timezone.utc)
        duration = time.perf_counter() - self.started_mono
        data = {
            "execution_start": self.started_wall,
            "execution_end": ended_wall.isoformat(),
            "total_execution_duration_seconds": round(duration, 6),
            "task_durations": self.task_times,
            "task_execution_status": {
                name: value["status"] for name, value in self.task_times.items()
            },
            "manager_delegation_history": self.manager_history,
            "errors": self.errors,
            "pdf_generation_duration_seconds": self.pdf_duration_seconds,
        }
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data
