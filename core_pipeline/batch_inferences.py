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
import uuid
from pathlib import Path

from constants import MODELS_DIRECTORY, TILES_DIRECTORY
from core_pipeline.observability import (
    MetricsRecorder,
    Timer,
    build_monitoring_metrics,
    setup_logger,
)
from core_pipeline.pipeline_constants import TILES_FAILED, TILES_INFERRED
from core_pipeline.tile import load_tile
from core_pipeline.validate import validate_raster
from model.inferences import Predictions, load_model, predict

logger = setup_logger(__name__)
metrics = MetricsRecorder()


def run_batch_inference(
    tiles_directory: Path,
    model_path: Path,
    output_path: Path,
) -> None:
    """Run batch inference on all tiles in a directory and save predictions."""
    metrics.reset()  # Reset metrics at the start to prevent unbounded memory growth

    run_id = str(uuid.uuid4())

    model = load_model(str(model_path))
    results = []
    tile_paths = sorted(tiles_directory.glob("*.tif"))

    if not tile_paths:
        raise FileNotFoundError(f"No tiles found in {tiles_directory}")

    logger.info(
        "Starting batch inference | run_id=%s | tiles_dir=%s | model_path=%s",
        run_id,
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
                metrics.increment(f"prediction_{prediction['prediction']}")
                metrics.record_timing(
                    "inference_time_seconds", prediction_timer.duration or 0.0
                )
                metrics.record_value("mean_intensity", prediction["mean_intensity"])

                results.append(_get_result(model_path, prediction, tile_path, run_id))

            except Exception as exc:
                logger.error(
                    "Inference failed for tile %s | error=%s",
                    tile_path.name,
                    exc,
                )
                metrics.increment(TILES_FAILED)

    metrics.record_timing("batch_duration_seconds", batch_timer.duration or 0.0)

    monitoring = build_monitoring_metrics(model, metrics)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Structure output with batch-level metadata and results
    output = {
        "metadata": {
            "run_id": run_id,
            "model_path": str(model_path),
            "tiles_directory": str(tiles_directory),
            "tiles_inferred": metrics.counters.get(TILES_INFERRED, 0),
            "tiles_failed": metrics.counters.get(TILES_FAILED, 0),
            "batch_duration_seconds": batch_timer.duration or 0.0,
            "monitoring": monitoring,
        },
        "predictions": results,
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    logger.info(
        "Batch inference completed | run_id=%s | tiles=%d | failed=%d | duration=%.3fs",
        run_id,
        metrics.counters.get(TILES_INFERRED, 0),
        metrics.counters.get(TILES_FAILED, 0),
        batch_timer.duration or 0.0,
    )

    logger.info("Monitoring metrics: %s", monitoring)
    logger.info("Metrics snapshot: %s", metrics.snapshot())


def _get_result(
    model_path: Path,
    prediction: Predictions,
    tile_path: Path,
    run_id: str,
) -> dict[str, str | float | int]:
    """Return prediction and confidence proxy for a tile."""
    return {
        "tile_id": tile_path.stem,
        "run_id": run_id,
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
