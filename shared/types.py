"""Shared type definitions used across multiple packages."""

from typing import TypedDict


class Model(TypedDict):
    """A trained model."""

    threshold: float
    training_mean: float
    training_std: float


class PredictionDistributionMetrics(TypedDict):
    """Format of the prediction distribution metrics."""

    bright_percentage: float
    bright_count: int
    dark_count: int


class MeanIntensityMetrics(TypedDict):
    """Format of the mean intensity metrics."""

    mean: float
    std: float


class DriftMetrics(TypedDict):
    """Format of the drift metrics."""

    mean_intensity_delta: float | None
    std_intensity_delta: float | None


class MonitoringMetrics(TypedDict):
    """Format of the monitoring metrics."""

    prediction_distribution: PredictionDistributionMetrics
    mean_intensity: MeanIntensityMetrics
    drift: DriftMetrics
