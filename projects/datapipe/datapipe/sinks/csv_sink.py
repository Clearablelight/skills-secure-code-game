from __future__ import annotations
import csv
from pathlib import Path
from datapipe.sinks.base import Sink


class CSVSink(Sink):
    def __init__(self, path: str | Path, delimiter: str = ",", encoding: str = "utf-8") -> None:
        self.path = Path(path)
        self.delimiter = delimiter
        self.encoding = encoding
        self._row_count: int = 0

    def write(self, rows: list[dict]) -> None:
        if not rows:
            self.path.write_text("", encoding=self.encoding)
            return
        fieldnames = list(rows[0].keys())
        with self.path.open("w", newline="", encoding=self.encoding) as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter=self.delimiter, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        self._row_count = len(rows)

    def __repr__(self) -> str:
        return f"CSVSink(path={str(self.path)!r})"
