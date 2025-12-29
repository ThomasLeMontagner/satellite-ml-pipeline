"""
Training script for a simple per-tile classification model.

Key design decisions:
- Train a trivial, interpretable model to focus on pipeline mechanics.
- Derive model parameters from real tile data.
- Produce an immutable, versioned model artifact.
"""

from __future__ import annotations

from pathlib import Path

from core_pipeline.tile import load_tile
from model.features import Features, extract_features
from model.registry import get_latest_model
from model.train import save_model, train_model


def aggregate_features(tile_paths: list[Path]) -> list[Features]:
    """Aggregate features across multiple tiles."""
    aggregated_features = []

    for tile_path in tile_paths:
        tile = load_tile(tile_path)
        features = extract_features(tile)
        aggregated_features.append(features)

    return aggregated_features


def update_latest_model(model_path: Path, latest_path: Path) -> None:
    """Update the pointer to the latest model artifact."""
    latest_path.write_text(model_path.read_text())


if __name__ == "__main__":
    from constants import MODELS_DIRECTORY, TILES_DIRECTORY

    latest_model_path = get_latest_model(MODELS_DIRECTORY)

    tile_paths = sorted(TILES_DIRECTORY.glob("*.tif"))
    if not tile_paths:
        raise FileNotFoundError("No tiles found for training")

    features = aggregate_features(tile_paths)
    model = train_model(features)
    model_path = save_model(model, MODELS_DIRECTORY)
    update_latest_model(model_path, latest_model_path)

    print(f"Model trained and saved at {model_path}")
    print(f"Latest model updated at {latest_model_path}")
