"""
Training module for a simple per-tile classifier.

Key design decisions:
- Use a trivial model to demonstrate training, serialization, and versioning.
- Avoid heavy ML frameworks to keep focus on production workflows.
"""

import json
import uuid
from pathlib import Path

import numpy as np

from model.features import Features
from shared.types import Model


def train_model(aggregated_features: list[Features]) -> Model:
    """Train a simple threshold-based model from aggregated features."""
    if not aggregated_features:
        raise ValueError(
            "Cannot train model: 'aggregated_features' must contain at least one "
            "feature set."
        )

    means = [features["mean_intensity"] for features in aggregated_features]
    threshold = float(np.mean(means))
    training_std = float(np.std(means))

    return {
        "threshold": threshold,
        "training_mean": threshold,
        "training_std": training_std,
    }


def save_model(model: Model, output_dir: Path) -> Path:
    """Serialize a trained model artifact to disk with a unique version."""
    output_dir.mkdir(parents=True, exist_ok=True)

    model_id = str(uuid.uuid4())
    model_path = output_dir / f"model_{model_id}.json"

    with open(model_path, "w") as f:
        json.dump(model, f, indent=2)

    return model_path
