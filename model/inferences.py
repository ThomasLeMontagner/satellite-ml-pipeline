"""
Inference module for per-tile classification.

Key design decisions:
- Keep inference stateless and lightweight.
- Load model artifacts explicitly to support batch and API workflows.
"""

from __future__ import annotations

import json
from typing import TypedDict

import numpy as np

from model.features import extract_features
from model.train import Model


class Predictions(TypedDict):
    """Format of predictions."""

    prediction: int
    mean_intensity: float


def load_model(path: str) -> Model:
    """Load a serialized model artifact from disk."""
    with open(path, "r") as f:
        return json.load(f)


def predict(tile: np.ndarray, model: Model) -> Predictions:
    """Run per-tile inference and return prediction and confidence proxy."""
    features = extract_features(tile)
    threshold = model["threshold"]

    prediction = int(features["mean_intensity"] > threshold)

    return {
        "prediction": prediction,
        "mean_intensity": features["mean_intensity"],
    }
