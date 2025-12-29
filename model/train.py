"""
Training module for a simple per-tile classifier.

Key design decisions:
- Use a trivial model to demonstrate training, serialization, and versioning.
- Avoid heavy ML frameworks to keep focus on production workflows.
"""

import json
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from model.features import Features


class Model(TypedDict):
    """A trained model."""

    threshold: float


def train_model(features: Features) -> Model:
    """Train a simple threshold-based model from aggregated features."""
    threshold = features["mean_intensity"]

    return {
        "threshold": threshold,
    }


def save_model(model: Model, output_dir: Path) -> Path:
    """Serialize a trained model artifact to disk with a unique version."""
    output_dir.mkdir(parents=True, exist_ok=True)

    model_id = str(uuid.uuid4())
    model_path = output_dir / f"model_{model_id}.json"

    with open(model_path, "w") as f:
        json.dump(model, f)

    return model_path
