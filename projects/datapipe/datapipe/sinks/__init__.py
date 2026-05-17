from datapipe.sinks.base import Sink
from datapipe.sinks.csv_sink import CSVSink
from datapipe.sinks.json_sink import JSONSink
from datapipe.sinks.memory_sink import MemorySink

__all__ = ["Sink", "CSVSink", "JSONSink", "MemorySink"]
