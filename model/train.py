"""
Training module for a simple per-tile classifier.

Key design decisions:
- Use a trivial model to demonstrate training, serialization, and versioning.
- Avoid heavy ML frameworks to keep focus on production workflows.
"""

from pathlib import Path
import json
import uuid


def train_model(features: dict[str, float]) -> dict[str, float]:
    """Train a simple threshold-based model from aggregated features."""
    threshold = features["mean_intensity"]

    return {
        "threshold": threshold,
    }


def save_model(model: dict[str, float], output_dir: Path) -> Path:
    """Serialize a trained model artifact to disk with a unique version."""
    output_dir.mkdir(parents=True, exist_ok=True)

    model_id = str(uuid.uuid4())
    model_path = output_dir / f"model_{model_id}.json"

    with open(model_path, "w") as f:
        json.dump(model, f)

    return model_path
