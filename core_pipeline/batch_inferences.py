"""
Batch inference module for satellite image tiles.

Key design decisions:
- Load a single immutable model artifact per batch run.
- Process tiles sequentially to keep memory usage predictable.
- Keep inference stateless and deterministic.
- Persist per-tile predictions together with model version metadata
  to support traceability and reproducibility.
"""

import logging
from pathlib import Path
import json

import numpy as np
import rasterio

from core_pipeline.constants import TILES_DIRECTORY
from core_pipeline.validate import validate_raster
from model.inferences import load_model, predict


def load_tile(path: Path) -> np.ndarray:
    """Load a raster tile from disk as a NumPy array."""
    with rasterio.open(path) as src:
        return src.read()


def run_batch_inference(
    tiles_directory: Path,
    model_path: Path,
    output_path: Path,
) -> None:
    """Run batch inference on all tiles in a directory and save predictions."""
    model = load_model(str(model_path))

    results = list()

    tile_paths = sorted(tiles_directory.glob("tile_*.tif"))

    if not tile_paths:
        raise FileNotFoundError(f"No tiles found in {tiles_directory}")

    for tile_path in tile_paths:
        validate_raster(tile_path)

        tile = load_tile(tile_path)
        prediction = predict(tile, model)

        results.append(
            {
                "tile_id": tile_path.stem,
                "model_path": str(model_path),
                "prediction": prediction["prediction"],
                "mean_intensity": prediction["mean_intensity"],
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    logging.info("Batch inference completed for %s tiles", len(results))
    logging.info("Results written to %s", output_path)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run_batch_inference(
        tiles_directory=TILES_DIRECTORY,
        model_path=Path("models/model_example.json"),
        output_path=Path("outputs/batch_predictions.json"),
    )
