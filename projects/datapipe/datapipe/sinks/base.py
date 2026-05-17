from __future__ import annotations
from abc import ABC, abstractmethod


class Sink(ABC):
    @abstractmethod
    def write(self, rows: list[dict]) -> None: ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
