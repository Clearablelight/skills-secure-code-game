"""Step — a single unit of work in a pipeline DAG."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Any


@dataclass
class Step:
    name: str
    fn: Callable[..., Any]
    depends_on: list[str] = field(default_factory=list)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.fn(*args, **kwargs)

    def __repr__(self) -> str:
        return f"Step(name={self.name!r}, depends_on={self.depends_on!r})"
