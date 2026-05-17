"""Pipeline — DAG builder and execution engine."""

from __future__ import annotations

import time
import logging
from datetime import datetime
from typing import Any, Callable

from datapipe.context import ExecutionContext
from datapipe.metrics import RunMetrics
from datapipe.retry import with_retry
from datapipe.sources.base import Source
from datapipe.sinks.base import Sink
from datapipe.step import Step

logger = logging.getLogger(__name__)


class PipelineResult:
    def __init__(self, metrics: RunMetrics) -> None:
        self.metrics = metrics

    def __repr__(self) -> str:
        return f"PipelineResult(metrics={self.metrics})"


class Pipeline:
    """A directed acyclic graph of Step objects."""

    def __init__(self, name: str, max_retries: int = 3, retry_delay: float = 1.0) -> None:
        self.name = name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._steps: dict[str, Step] = {}

    def step(self, name: str | None = None, depends_on: list[str] | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        _depends_on = depends_on or []

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            step_name = name or fn.__name__
            s = Step(name=step_name, fn=fn, depends_on=_depends_on)
            if step_name in self._steps:
                raise ValueError(f"Step {step_name!r} is already registered.")
            self._steps[step_name] = s
            return fn

        return decorator

    def add_step(self, step: Step) -> None:
        if step.name in self._steps:
            raise ValueError(f"Step {step.name!r} is already registered.")
        self._steps[step.name] = step

    def _topological_sort(self) -> list[str]:
        in_degree: dict[str, int] = {n: 0 for n in self._steps}
        adjacency: dict[str, list[str]] = {n: [] for n in self._steps}

        for name, step in self._steps.items():
            for dep in step.depends_on:
                if dep not in self._steps:
                    raise ValueError(f"Step {name!r} depends on unknown step {dep!r}.")
                adjacency[dep].append(name)
                in_degree[name] += 1

        queue = [n for n, d in in_degree.items() if d == 0]
        order: list[str] = []

        while queue:
            queue.sort()
            node = queue.pop(0)
            order.append(node)
            for neighbour in sorted(adjacency[node]):
                in_degree[neighbour] -= 1
                if in_degree[neighbour] == 0:
                    queue.append(neighbour)

        if len(order) != len(self._steps):
            raise ValueError("Pipeline contains a cycle — DAG execution is not possible.")
        return order

    def run(self, source: Source, sink: Sink, **kwargs: Any) -> PipelineResult:
        ctx = ExecutionContext.create(pipeline_name=self.name, source=source, sink=sink)
        metrics = RunMetrics(run_id=ctx.run_id)
        order = self._topological_sort()
        outputs: dict[str, Any] = {}
        wall_start = time.monotonic()

        for step_name in order:
            step = self._steps[step_name]
            dep_outputs = [outputs[dep] for dep in step.depends_on]
            ctx.logger.info("Running step %r", step_name)

            def _call(s=step, deps=dep_outputs):
                return s(ctx, *deps)

            try:
                result, retries_used = with_retry(_call, max_retries=self.max_retries, base_delay=self.retry_delay, step_name=step_name)
                outputs[step_name] = result
                metrics.steps_run += 1
                metrics.retries += retries_used
            except RuntimeError:
                metrics.steps_failed += 1
                metrics.retries += self.max_retries
                raise

        metrics.rows_in = _count_rows(source)
        metrics.rows_out = _count_rows(sink)
        metrics.duration_ms = (time.monotonic() - wall_start) * 1000
        ctx.logger.info("Pipeline %r finished — %s", self.name, metrics)
        return PipelineResult(metrics=metrics)

    def visualize(self) -> None:
        try:
            order = self._topological_sort()
        except ValueError as exc:
            print(f"[datapipe] Cannot visualize: {exc}")
            return

        print(f"\nPipeline: {self.name!r}")
        print("=" * (len(self.name) + 12))
        for step_name in order:
            step = self._steps[step_name]
            indent = "  " * len(step.depends_on)
            deps = f"  ← [{', '.join(step.depends_on)}]" if step.depends_on else ""
            print(f"{indent}[ {step_name} ]{deps}")
        print()


def _count_rows(obj: Any) -> int:
    if hasattr(obj, "data") and isinstance(obj.data, list):
        return len(obj.data)
    if hasattr(obj, "_row_count"):
        return obj._row_count
    return 0
