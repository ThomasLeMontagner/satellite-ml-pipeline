"""
Model health checks for monitoring and maintenance.

Key design decisions:
- Compare live monitoring stats with training baselines.
- Emit warnings when drift exceeds a configurable threshold.
- Log actionable recommendations for operators.
"""

from __future__ import annotations

from typing import TypedDict

from core_pipeline.observability import setup_logger
from core_pipeline.types_ import MonitoringMetrics
from model.train import Model

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

    training_mean = model["training_mean"]
    training_std = model["training_std"]
    live_mean = monitoring["mean_intensity"]["mean"]
    live_std = monitoring["mean_intensity"]["std"]

    recommendations: list[str] = []
    drift_detected = False
    mean_delta = monitoring["drift"]["mean_intensity_delta"]
    std_delta = monitoring["drift"]["std_intensity_delta"]

    if mean_delta is not None and abs(mean_delta) > drift_threshold:
        drift_detected = True
        logger.warning(
            "Potential data drift detected | metric=mean_intensity | "
            "live=%.4f | training=%.4f | delta=%.4f | threshold=%.4f",
            live_mean,
            float(training_mean),
            mean_delta,
            drift_threshold,
        )
        recommendations.append("Consider retraining the model with recent data.")

    if std_delta is not None and abs(std_delta) > drift_threshold:
        drift_detected = True
        logger.warning(
            "Potential data drift detected | metric=std_intensity | "
            "live=%.4f | training=%.4f | delta=%.4f | threshold=%.4f",
            live_std,
            float(training_std),
            std_delta,
            drift_threshold,
        )
        if "Consider retraining the model with recent data." not in recommendations:
            recommendations.append("Consider retraining the model with recent data.")

    for recommendation in recommendations:
        logger.info("Recommendation: %s", recommendation)

    return {
        "drift_detected": drift_detected,
        "mean_intensity_delta": mean_delta,
        "std_intensity_delta": std_delta,
        "recommendations": recommendations,
    }
