from __future__ import annotations
import json
from pathlib import Path
from typing import Literal
from datapipe.sinks.base import Sink


class JSONSink(Sink):
    def __init__(self, path: str | Path, mode: Literal["json", "jsonl"] = "json") -> None:
        if mode not in ("json", "jsonl"):
            raise ValueError(f"mode must be 'json' or 'jsonl', got {mode!r}")
        self.path = Path(path)
        self.mode = mode
        self._row_count: int = 0

    def write(self, rows: list[dict]) -> None:
        if self.mode == "json":
            text = json.dumps(rows, indent=2, default=str)
        else:
            text = "\n".join(json.dumps(row, default=str) for row in rows)
            if text:
                text += "\n"
        self.path.write_text(text, encoding="utf-8")
        self._row_count = len(rows)

    def __repr__(self) -> str:
        return f"JSONSink(path={str(self.path)!r}, mode={self.mode!r})"
