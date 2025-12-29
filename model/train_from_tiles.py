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
from model.train import save_model, train_model


def collect_tile_features(tile_paths: list[Path]) -> list[Features]:
    """Collect features across multiple tiles."""
    collected_features = []

    for tile_path in tile_paths:
        tile = load_tile(tile_path)
        features = extract_features(tile)
        collected_features.append(features)

    return collected_features


def copy_model_to_latest(model_path: Path, latest_path: Path) -> None:
    """Update the pointer to the latest model artifact."""
    latest_path.write_text(model_path.read_text())


if __name__ == "__main__":
    from constants import MODELS_DIRECTORY, TILES_DIRECTORY

    tile_paths = sorted(TILES_DIRECTORY.glob("*.tif"))
    if not tile_paths:
        raise FileNotFoundError("No tiles found for training")

    features = collect_tile_features(tile_paths)
    model = train_model(features)
    model_path = save_model(model, MODELS_DIRECTORY)

    latest_model_path = MODELS_DIRECTORY / "latest_model.json"
    copy_model_to_latest(model_path, latest_model_path)

    print(f"Model trained and saved at {model_path}")
    print(f"Latest model updated at {latest_model_path}")
