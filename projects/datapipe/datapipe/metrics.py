"""RunMetrics — collected statistics for a single pipeline run."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class RunMetrics:
    rows_in: int = 0
    rows_out: int = 0
    steps_run: int = 0
    steps_failed: int = 0
    duration_ms: float = 0.0
    retries: int = 0
    run_id: str = ""

    def __str__(self) -> str:
        return (f"RunMetrics(rows_in={self.rows_in}, rows_out={self.rows_out}, steps_run={self.steps_run}, steps_failed={self.steps_failed}, duration_ms={self.duration_ms:.1f}, retries={self.retries}, run_id={self.run_id!r})")
