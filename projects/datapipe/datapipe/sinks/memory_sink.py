from __future__ import annotations
from datapipe.sinks.base import Sink


class MemorySink(Sink):
    """Accumulates rows in self.data for easy inspection in tests."""

    def __init__(self) -> None:
        self.data: list[dict] = []

    def write(self, rows: list[dict]) -> None:
        self.data.extend(rows)

    def read(self) -> list[dict]:
        return list(self.data)

    def clear(self) -> None:
        self.data.clear()

    def __repr__(self) -> str:
        return f"MemorySink(rows={len(self.data)})"
