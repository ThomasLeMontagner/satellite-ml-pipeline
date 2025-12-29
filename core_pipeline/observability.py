"""
Observability utilities for logging and metrics.

Key design decisions:
- Use standard Python logging for portability.
- Keep metrics lightweight and in-process.
- Avoid external dependencies to keep the demo simple.
- Expose a small, explicit API for recording metrics.
"""

from __future__ import annotations

import logging
import threading
import time
from types import TracebackType


def setup_logger(name: str) -> logging.Logger:
    """Configure and return a module-level logger.

    Sets propagate=False to prevent duplicate log messages when parent
    loggers already have handlers configured.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Prevent duplicate log messages due to propagation
    logger.propagate = False

    return logger


class MetricsRecorder:
    """In-memory recorder for simple counters and timings.

    Thread-safe implementation using locks to prevent race conditions
    in concurrent environments like FastAPI with multiple workers.
    """

    def __init__(self) -> None:
        """Initialize the metrics recorder."""
        self.counters: dict[str, int] = {}
        self.timings: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def increment(self, name: str, value: int = 1) -> None:
        """Increment a named counter in a thread-safe manner."""
        with self._lock:
            self.counters[name] = self.counters.get(name, 0) + value

    def record_timing(self, name: str, duration: float) -> None:
        """Record a timing measurement in seconds.

        Stores individual timing measurements to allow calculation of
        statistics like average, min, max, and percentiles.
        """
        with self._lock:
            if name not in self.timings:
                self.timings[name] = []
            self.timings[name].append(duration)

    def reset(self) -> None:
        """Reset all metrics to prevent unbounded memory growth.

        Useful in batch processing scenarios to clear metrics between runs.
        """
        with self._lock:
            self.counters.clear()
            self.timings.clear()

    def snapshot(
        self,
    ) -> dict[str, dict[str, float] | dict[str, int] | dict[str, list[float]]]:
        """Return a snapshot of all recorded metrics.

        Returns counters as integers and timings as lists of individual
        measurements for statistical analysis.
        """
        with self._lock:
            return {
                "counters": dict(self.counters),
                "timings": {k: list(v) for k, v in self.timings.items()},
            }


class Timer:
    """Context manager for timing code blocks."""

    def __init__(self) -> None:
        """Initialize the timer."""
        self.start: float | None = None
        self.duration: float | None = None

    def __enter__(self) -> Timer:
        """Enter the context manager."""
        self.start = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the context manager."""
        if self.start is not None:
            self.duration = time.perf_counter() - self.start
