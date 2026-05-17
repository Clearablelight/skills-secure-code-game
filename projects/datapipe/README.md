# datapipe

**Define your ETL pipelines as code. Zero dependencies.**

`datapipe` is a lightweight, pure-Python library for building and running ETL pipelines as directed acyclic graphs (DAGs) of steps. Think "mini Prefect" — but with no runtime dependencies and a five-minute learning curve.

---

## Quick Start

```python
from datapipe import Pipeline
from datapipe.sources import CSVSource
from datapipe.sinks import CSVSink

pipeline = Pipeline(name="user-etl")

@pipeline.step(name="extract")
def extract(ctx):
    return ctx.source.read()

@pipeline.step(name="transform", depends_on=["extract"])
def transform(ctx, data):
    return [
        {**row, "full_name": f"{row['first']} {row['last']}"}
        for row in data
        if row.get("active") == "true"
    ]

@pipeline.step(name="load", depends_on=["transform"])
def load(ctx, data):
    ctx.sink.write(data)
    return data

result = pipeline.run(
    source=CSVSource("users.csv"),
    sink=CSVSink("output.csv"),
)
print(result.metrics)
# RunMetrics(rows_in=100, rows_out=87, duration_ms=42, ...)
```

---

## Installation

```bash
git clone https://github.com/clearablelight/datapipe
cd datapipe
pip install -e ".[dev]"
```

---

## Architecture

`datapipe` models a pipeline as a **DAG** of `Step` nodes:

```
extract ► transform ► load
```

When you call `pipeline.run()`, the engine:
1. Performs a **topological sort** (Kahn's algorithm) to determine execution order
2. Runs each step in order, passing upstream outputs as positional arguments
3. Wraps each step in **retry logic** with exponential backoff
4. Collects timing and row-count **metrics** for observability

### Visualizing

```python
pipeline.visualize()
# Pipeline: 'user-etl'
# ======================
# [ extract ]
#   [ transform ]  ← [extract]
#     [ load ]  ← [transform]
```

---

## Sources

| Class | Description |
|---|---|
| `CSVSource(path, delimiter=',')` | Reads CSV into list of dicts |
| `JSONSource(path)` | Reads JSON array or JSONL, auto-detects format |
| `HTTPSource(url, headers=None, params=None)` | Fetches JSON via stdlib `urllib` |

---

## Sinks

| Class | Description |
|---|---|
| `CSVSink(path, delimiter=',')` | Writes rows to CSV |
| `JSONSink(path, mode='json')` | Writes JSON array or JSONL |
| `MemorySink()` | Stores rows in `self.data` — ideal for tests |

---

## Retry & Metrics

```python
pipeline = Pipeline(name="robust", max_retries=3, retry_delay=1.0)
# Delay schedule: 1s, 2s, 4s (doubles each attempt)

result = pipeline.run(source=..., sink=...)
print(result.metrics.rows_in)     # rows read
print(result.metrics.rows_out)    # rows written
print(result.metrics.duration_ms) # total time
print(result.metrics.retries)     # total retries used
print(result.metrics.run_id)      # unique UUID per run
```

---

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -q
# 95 passed in 0.12s
```

---

## License

MIT
