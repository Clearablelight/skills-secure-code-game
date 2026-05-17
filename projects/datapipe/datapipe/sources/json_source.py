from __future__ import annotations
import json
from pathlib import Path
from datapipe.sources.base import Source


class JSONSource(Source):
    """Read a JSON array or JSONL file. Auto-detects format."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._row_count: int = 0

    def read(self) -> list[dict]:
        text = self.path.read_text(encoding="utf-8")
        stripped = text.strip()
        if stripped.startswith("["):
            rows = json.loads(stripped)
            if not isinstance(rows, list):
                raise ValueError(f"{self.path}: expected a JSON array at the top level.")
        else:
            rows = [json.loads(line) for line in stripped.splitlines() if line.strip()]
        self._row_count = len(rows)
        return rows

    def __repr__(self) -> str:
        return f"JSONSource(path={str(self.path)!r})"
