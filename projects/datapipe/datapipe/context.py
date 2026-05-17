"""ExecutionContext — runtime metadata passed to every step."""

from __future__ import annotations
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datapipe.sources.base import Source
    from datapipe.sinks.base import Sink


@dataclass
class ExecutionContext:
    pipeline_name: str
    run_id: str
    source: "Source"
    sink: "Sink"
    started_at: datetime
    logger: logging.Logger

    @classmethod
    def create(cls, pipeline_name: str, source: "Source", sink: "Sink") -> "ExecutionContext":
        run_id = str(uuid.uuid4())
        logger = logging.getLogger(f"datapipe.{pipeline_name}.{run_id[:8]}")
        return cls(pipeline_name=pipeline_name, run_id=run_id, source=source, sink=sink, started_at=datetime.utcnow(), logger=logger)
