from __future__ import annotations
from abc import ABC, abstractmethod


class Source(ABC):
    @abstractmethod
    def read(self) -> list[dict]: ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
