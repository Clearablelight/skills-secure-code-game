"""Retry logic with exponential backoff."""

from __future__ import annotations
import logging
import time
from typing import Callable, TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


def with_retry(fn: Callable[[], T], max_retries: int = 3, base_delay: float = 1.0, backoff_factor: float = 2.0, step_name: str = "<step>") -> tuple[T, int]:
    """Call fn(), retrying on exception with exponential backoff.

    Returns (result, retries_used).
    Delay schedule: base_delay * backoff_factor^attempt
    """
    last_exc: Exception | None = None
    retries_used = 0

    for attempt in range(max_retries + 1):
        try:
            return fn(), retries_used
        except Exception as exc:
            last_exc = exc
            if attempt < max_retries:
                delay = base_delay * (backoff_factor ** attempt)
                logger.warning("Step %r failed (attempt %d/%d): %s — retrying in %.1fs", step_name, attempt + 1, max_retries + 1, exc, delay)
                time.sleep(delay)
                retries_used += 1
            else:
                logger.error("Step %r failed permanently after %d attempt(s): %s", step_name, max_retries + 1, exc)

    raise RuntimeError(f"Step {step_name!r} failed after {max_retries + 1} attempt(s)") from last_exc
