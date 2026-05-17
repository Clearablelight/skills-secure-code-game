"""datapipe — lightweight, pure-Python ETL pipeline framework.

Define your ETL pipelines as code. Zero dependencies.

Quick start::

    from datapipe import Pipeline
    from datapipe.sources import CSVSource
    from datapipe.sinks import MemorySink

    pipeline = Pipeline(name="demo")

    @pipeline.step(name="extract")
    def extract(ctx):
        return ctx.source.read()

    @pipeline.step(name="load", depends_on=["extract"])
    def load(ctx, data):
        ctx.sink.write(data)
        return data

    result = pipeline.run(source=CSVSource("data.csv"), sink=MemorySink())
    print(result.metrics)
"""

from datapipe.pipeline import Pipeline, PipelineResult
from datapipe.step import Step
from datapipe.context import ExecutionContext
from datapipe.metrics import RunMetrics
from datapipe.sources.base import Source
from datapipe.sinks.base import Sink

__all__ = ["Pipeline", "PipelineResult", "Step", "ExecutionContext", "RunMetrics", "Source", "Sink"]
__version__ = "0.1.0"
