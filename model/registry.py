"""Model registry utilities."""

from pathlib import Path


def get_latest_model(model_directory: Path) -> Path:
    """Return the most recently created model artifact."""
    models = sorted(model_directory.glob("model_*.json"))
    if not models:
        raise FileNotFoundError("No model artifacts found")
    return models[-1]
