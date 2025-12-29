"""
Training script for a simple per-tile classification model.

Key design decisions:
- Train a trivial, interpretable model to focus on pipeline mechanics.
- Derive model parameters from real tile data.
- Produce an immutable, versioned model artifact.
"""

from __future__ import annotations

from pathlib import Path

import rasterio
import numpy as np

from model.features import extract_features
from model.train import Model, save_model


def load_tile(path: Path) -> np.ndarray:
    """Load a raster tile from disk as a NumPy array."""
    with rasterio.open(path) as source:
        return source.read()


def aggregate_features(tile_paths: list[Path]) -> dict[str, float]:
    """Aggregate features across multiple tiles."""
    means = list()

    for tile_path in tile_paths:
        tile = load_tile(tile_path)
        features = extract_features(tile)
        means.append(features["mean_intensity"])

    return {"global_mean_intensity": float(np.mean(means))}


def train_model(features: dict[str, float]) -> Model:
    """Create a simple threshold-based model from aggregated features."""
    return {"threshold": features["global_mean_intensity"]}


def update_latest_model(model_path: Path, latest_path: Path) -> None:
    """Update the pointer to the latest model artifact."""
    latest_path.write_text(model_path.read_text())


if __name__ == "__main__":
    from core_pipeline.constants import TILES_DIRECTORY

    model_directory = Path("models")
    latest_model_path = model_directory / "latest_model.json"

    tile_paths = sorted(TILES_DIRECTORY.glob("*.tif"))
    if not tile_paths:
        raise FileNotFoundError("No tiles found for training")

    features = aggregate_features(tile_paths)
    model = train_model(features)
    model_path = save_model(model, model_directory)
    update_latest_model(model_path, latest_model_path)

    print(f"Model trained and saved at {model_path}")
    print(f"Latest model updated at {latest_model_path}")
