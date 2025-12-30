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

logger = setup_logger(__name__)


class HealthReport(TypedDict):
    """Format of the model health report."""

    drift_detected: bool
    mean_intensity_delta: float | None
    std_intensity_delta: float | None
    recommendations: list[str]


def check_model_health(
    model: Model,
    monitoring: MonitoringMetrics,
    drift_threshold: float = 0.5,
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
