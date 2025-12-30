"""
Observability utilities for logging and metrics.

Key design decisions:
- Use standard Python logging for portability.
- Keep metrics lightweight and in-process.
- Avoid external dependencies to keep the demo simple.
- Expose a small, explicit API for recording metrics.
"""

from __future__ import annotations

import threading
import time
from statistics import fmean, pstdev
from types import TracebackType

from shared.constants import TILES_INFERRED
from shared.types import Model, MonitoringMetrics


class MetricsRecorder:
    """In-memory recorder for simple counters and timings.

    Thread-safe implementation using locks to prevent race conditions in concurrent
    environments like FastAPI with multiple workers.
    """

    def __init__(self) -> None:
        """Initialize the metrics recorder."""
        self.counters: dict[str, int] = {}
        self.timings: dict[str, list[float]] = {}
        self.values: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def increment(self, name: str, value: int = 1) -> None:
        """Increment a named counter in a thread-safe manner."""
        with self._lock:
            self.counters[name] = self.counters.get(name, 0) + value

    def record_timing(self, name: str, duration: float) -> None:
        """Record a timing measurement in seconds.

        Stores individual timing measurements to allow calculation of statistics like
        average, min, max, and percentiles.
        """
        with self._lock:
            timings = self.timings
            if name not in timings:
                timings[name] = []
            timings[name].append(duration)

    def record_value(self, name: str, value: float) -> None:
        """Record an arbitrary numeric value.

        Useful for capturing metrics that are aggregated later, such as prediction
        confidences or feature statistics.
        """
        with self._lock:
            values = self.values
            if name not in values:
                values[name] = []
            values[name].append(value)

    def reset(self) -> None:
        """Reset all metrics to prevent unbounded memory growth.

        Useful in batch processing scenarios to clear metrics between runs.
        """
        with self._lock:
            self.counters.clear()
            self.timings.clear()
            self.values.clear()

    def snapshot(self) -> dict[str, dict[str, float] | dict[str, int]]:
        """Return a snapshot of all recorded metrics."""
        with self._lock:
            return {
                "counters": dict(self.counters),
                "timings": {key: list(values) for key, values in self.timings.items()},
                "values": {key: list(values) for key, values in self.values.items()},
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
    ) -> bool:
        """Exit the context manager."""
        if self.start is not None:
            self.duration = time.perf_counter() - self.start
        return False


def build_monitoring_metrics(
    model: Model,
    metrics_recorder: MetricsRecorder,
) -> MonitoringMetrics:
    """Aggregate monitoring metrics for post-inference analysis."""
    counters = metrics_recorder.counters
    values = metrics_recorder.values

    total_tiles = counters.get(TILES_INFERRED, 0)
    prediction_bright = counters.get("prediction_1", 0)
    prediction_dark = counters.get("prediction_0", 0)

    mean_intensities = values.get("mean_intensity", [])
    mean_intensity_mean = fmean(mean_intensities) if mean_intensities else 0.0
    mean_intensity_std = pstdev(mean_intensities) if len(mean_intensities) > 1 else 0.0

    training_mean = model.get("training_mean", model.get("threshold"))
    training_std = model.get("training_std")

    drift = {
        "mean_intensity_delta": None,
        "std_intensity_delta": None,
    }

    if training_mean is not None:
        drift["mean_intensity_delta"] = mean_intensity_mean - float(training_mean)
    if training_std is not None:
        drift["std_intensity_delta"] = mean_intensity_std - float(training_std)

    bright_percentage = (prediction_bright / total_tiles * 100) if total_tiles else 0.0
    return {
        "prediction_distribution": {
            "bright_percentage": bright_percentage,
            "bright_count": prediction_bright,
            "dark_count": prediction_dark,
        },
        "mean_intensity": {
            "mean": mean_intensity_mean,
            "std": mean_intensity_std,
        },
        "drift": drift,
    }
