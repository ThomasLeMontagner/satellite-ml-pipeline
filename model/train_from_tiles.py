"""
Training script for a simple per-tile classification model.

Key design decisions:
- Train a trivial, interpretable model to focus on pipeline mechanics.
- Derive model parameters from real tile data.
- Produce an immutable, versioned model artifact.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from model.features import Features, extract_features
from model.train import save_model, train_model
from shared.data_utils import load_tile


def collect_tile_features(tile_paths: list[Path]) -> list[Features]:
    """Collect features across multiple tiles."""
    collected_features = []

    for tile_path in tile_paths:
        tile = load_tile(tile_path)
        features = extract_features(tile)
        collected_features.append(features)

    return collected_features


def copy_model_to_latest(model_path: Path, latest_path: Path) -> None:
    """Copy the model artifact to the path representing the latest model."""
    shutil.copyfile(model_path, latest_path)


if __name__ == "__main__":
    from shared.config import MODELS_DIRECTORY, TILES_DIRECTORY

    tile_paths = sorted(TILES_DIRECTORY.glob("*.tif"))
    if not tile_paths:
        raise ValueError(f"No .tif tiles found in {TILES_DIRECTORY} for training")

    features = collect_tile_features(tile_paths)
    model = train_model(features)
    model_path = save_model(model, MODELS_DIRECTORY)

    latest_model_path = MODELS_DIRECTORY / "latest_model.json"
    copy_model_to_latest(model_path, latest_model_path)

    print(f"Model trained and saved at {model_path}")
    print(f"Latest model updated at {latest_model_path}")
