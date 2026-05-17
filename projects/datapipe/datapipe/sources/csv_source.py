from __future__ import annotations
import csv
from pathlib import Path
from datapipe.sources.base import Source


class CSVSource(Source):
    def __init__(self, path: str | Path, delimiter: str = ",", encoding: str = "utf-8") -> None:
        self.path = Path(path)
        self.delimiter = delimiter
        self.encoding = encoding
        self._row_count: int = 0

    def read(self) -> list[dict]:
        with self.path.open(newline="", encoding=self.encoding) as fh:
            rows = list(csv.DictReader(fh, delimiter=self.delimiter))
        self._row_count = len(rows)
        return rows

    def __repr__(self) -> str:
        return f"CSVSource(path={str(self.path)!r}, delimiter={self.delimiter!r})"
