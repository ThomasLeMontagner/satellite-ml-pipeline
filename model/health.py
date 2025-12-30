"""
Model health checks for monitoring and maintenance.

Key design decisions:
- Compare live monitoring stats with training baselines.
- Emit warnings when drift exceeds a configurable threshold.
- Log actionable recommendations for operators.
"""

from __future__ import annotations

from typing import TypedDict

from utils.logging import setup_logger
from utils.types_ import Model, MonitoringMetrics

CONSIDER_RETRAINING_MODEL = "Consider retraining the model with recent data."

DRIFT_THRESHOLD = 0.5
FAILED_RATE_THRESHOLD = 0.02
LATENCY_MS_THRESHOLD = 500.0

logger = setup_logger(__name__)


class RetrainingMetrics(TypedDict):
    """Operational metrics used to decide whether retraining is warranted."""

    drift_score: float  # Aggregated drift signal (higher means more drift).
    failed_inference_rate: float  # Fraction of failed inferences in the window.
    p95_latency_ms: float  # 95th percentile inference latency in milliseconds.


class HealthReport(TypedDict):
    """Format of the model health report."""

    drift_detected: bool
    mean_intensity_delta: float | None
    std_intensity_delta: float | None
    recommendations: list[str]


def should_retrain(metrics: RetrainingMetrics) -> bool:
    """Return True when operational metrics suggest scheduling retraining.

    This is a documented stub for operational optimization only; it does not
    trigger any automatic retraining.
    """
    drift_score = metrics.get("drift_score", 0.0)
    failed_rate = metrics.get("failed_inference_rate", 0.0)
    p95_latency_ms = metrics.get("p95_latency_ms", 0.0)

    return (
        drift_score >= DRIFT_THRESHOLD
        or failed_rate >= FAILED_RATE_THRESHOLD
        or p95_latency_ms >= LATENCY_MS_THRESHOLD
    )


def check_model_health(
    model: Model,
    monitoring: MonitoringMetrics,
    drift_threshold: float = DRIFT_THRESHOLD,
) -> HealthReport:
    """Compare live monitoring stats with training stats and log warnings."""
    if drift_threshold <= 0:
        raise ValueError("drift_threshold must be positive")

    training_mean = model.get("training_mean")
    training_std = model.get("training_std")
    live_mean = monitoring["mean_intensity"]["mean"]
    live_std = monitoring["mean_intensity"]["std"]

    recommendations: list[str] = []
    drift_detected = False
    mean_delta = monitoring["drift"]["mean_intensity_delta"]
    std_delta = monitoring["drift"]["std_intensity_delta"]

    if training_mean is None:
        logger.warning("Training mean missing; cannot evaluate mean intensity drift.")
    elif mean_delta is not None and abs(mean_delta) > drift_threshold:
        drift_detected = True
        logger.warning(
            "Potential data drift detected | metric=mean_intensity | "
            "live=%.4f | training=%.4f | delta=%.4f | threshold=%.4f",
            live_mean,
            float(training_mean),
            mean_delta,
            drift_threshold,
        )
        recommendations.append(CONSIDER_RETRAINING_MODEL)

    if training_std is None:
        logger.warning("Training std missing; cannot evaluate std intensity drift.")
    elif std_delta is not None and abs(std_delta) > drift_threshold:
        drift_detected = True
        logger.warning(
            "Potential data drift detected | metric=std_intensity | "
            "live=%.4f | training=%.4f | delta=%.4f | threshold=%.4f",
            live_std,
            float(training_std),
            std_delta,
            drift_threshold,
        )
        if CONSIDER_RETRAINING_MODEL not in recommendations:
            recommendations.append(CONSIDER_RETRAINING_MODEL)

    return {
        "drift_detected": drift_detected,
        "mean_intensity_delta": mean_delta,
        "std_intensity_delta": std_delta,
        "recommendations": recommendations,
    }
