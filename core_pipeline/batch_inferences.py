"""
Batch inference module for satellite image tiles.

Key design decisions:
- Load a single immutable model artifact per batch run.
- Process tiles sequentially to keep memory usage predictable.
- Keep inference stateless and deterministic.
- Persist per-tile predictions together with model version metadata to support
  traceability and reproducibility.
"""

import json
from pathlib import Path

from constants import MODELS_DIRECTORY, TILES_DIRECTORY
from core_pipeline.observability import MetricsRecorder, Timer, setup_logger
from core_pipeline.tile import load_tile
from core_pipeline.validate import validate_raster
from model.inferences import Predictions, load_model, predict

TILES_INFERRED = "tiles_inferred"
TILES_FAILED = "tiles_failed"

logger = setup_logger(__name__)
metrics = MetricsRecorder()


def run_batch_inference(
    tiles_directory: Path,
    model_path: Path,
    output_path: Path,
) -> None:
    """Run batch inference on all tiles in a directory and save predictions."""
    metrics.reset()  # Reset metrics at the start to prevent unbounded memory growth

    model = load_model(str(model_path))
    results = []
    tile_paths = sorted(tiles_directory.glob("*.tif"))

    if not tile_paths:
        raise FileNotFoundError(f"No tiles found in {tiles_directory}")

    logger.info(
        "Starting batch inference | tiles_dir=%s | model_path=%s",
        tiles_directory,
        model_path,
    )

    with Timer() as batch_timer:
        for tile_path in tile_paths:
            try:
                validate_raster(tile_path)
                tile = load_tile(tile_path)

                with Timer() as prediction_timer:
                    prediction = predict(tile, model)

                metrics.increment(TILES_INFERRED)
                metrics.record_timing(
                    "inference_time_seconds", prediction_timer.duration or 0.0
                )

                results.append(_get_result(model_path, prediction, tile_path))

            except Exception as exc:
                logger.error(
                    "Inference failed for tile %s | error=%s",
                    tile_path.name,
                    exc,
                )
                metrics.increment(TILES_FAILED)

    metrics.record_timing("batch_duration_seconds", batch_timer.duration or 0.0)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(
        "Batch inference completed | tiles=%d | failed=%d | duration=%.3fs",
        metrics.counters.get(TILES_INFERRED, 0),
        metrics.counters.get(TILES_FAILED, 0),
        batch_timer.duration or 0.0,
    )

    logger.info("Metrics snapshot: %s", metrics.snapshot())


def _get_result(
    model_path: Path,
    prediction: Predictions,
    tile_path: Path,
) -> dict[str, str | float | int]:
    """Return prediction and confidence proxy for a tile."""
    return {
        "tile_id": tile_path.stem,
        "model_path": str(model_path),
        "prediction": prediction["prediction"],
        "mean_intensity": prediction["mean_intensity"],
    }


if __name__ == "__main__":
    run_batch_inference(
        tiles_directory=TILES_DIRECTORY,
        model_path=MODELS_DIRECTORY / "latest_model.json",
        output_path=Path("outputs/batch_predictions.json"),
    )
