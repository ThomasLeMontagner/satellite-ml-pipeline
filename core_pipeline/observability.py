"""
Observability utilities for logging and metrics.

Key design decisions:
- Use standard Python logging for portability.
- Keep metrics lightweight and in-process.
- Avoid external dependencies to keep the demo simple.
- Expose a small, explicit API for recording metrics.
"""

import logging
import time


def setup_logger(name: str) -> logging.Logger:
    """Configure and return a module-level logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


class MetricsRecorder:
    """In-memory recorder for simple counters and timings."""

    def __init__(self) -> None:
        """Initialize the metrics recorder."""
        self.counters: dict[str, int] = {}
        self.timings: dict[str, float] = {}

    def increment(self, name: str, value: int = 1) -> None:
        """Increment a named counter."""
        self.counters[name] = self.counters.get(name, 0) + value

    def record_timing(self, name: str, duration: float) -> None:
        """Record a timing measurement in seconds."""
        self.timings[name] = self.timings.get(name, 0.0) + duration

    def snapshot(self) -> dict[str, dict[str, float]]:
        """Return a snapshot of all recorded metrics."""
        return {
            "counters": dict(self.counters),
            "timings": dict(self.timings),
        }


class Timer:
    """Context manager for timing code blocks."""

    def __init__(self) -> None:
        """Initialize the timer."""
        self.start: float | None = None
        self.duration: float | None = None

    def __enter__(self) -> "Timer":
        """Enter the context manager."""
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit the context manager."""
        if self.start is not None:
            self.duration = time.perf_counter() - self.start
