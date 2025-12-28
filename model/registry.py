"""Model registry utilities."""

from pathlib import Path


def get_latest_model(model_directory: Path) -> Path:
    """Return the most recently created model artifact."""
    models = list(model_directory.glob("model_*.json"))
    if not models:
        raise FileNotFoundError("No model artifacts found")
    return max(models, key=lambda model_path: model_path.stat().st_ctime)
