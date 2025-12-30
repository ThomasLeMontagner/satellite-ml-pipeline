"""
API inference service for satellite image tiles.

Key design decisions:
- Expose inference via a stateless REST API.
- Load the model artifact once at startup to minimize request latency.
- Reuse the same inference logic as batch workflows to ensure consistency.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from constants import MODELS_DIRECTORY, TILES_DIRECTORY
from core_pipeline.exceptions import PipelineError
from core_pipeline.observability import MetricsRecorder, Timer
from core_pipeline.validate import validate_raster
from model.inferences import load_model, predict
from utils.data import load_tile
from utils.logging import setup_logger
from utils.types_ import Model

logger = setup_logger("api")
metrics = MetricsRecorder()

MODEL_PATH = MODELS_DIRECTORY / "latest_model.json"
ALLOWED_TILE_DIRECTORY = TILES_DIRECTORY

model: Model | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application lifespan: load and clean up resources."""
    global model

    try:
        model = load_model(str(MODEL_PATH))
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"Model file not found at '{MODEL_PATH}'. "
            "Ensure the model is trained and exported before starting the API service."
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to load model from '{MODEL_PATH}': {exc}") from exc

    yield


app = FastAPI(
    title="Satellite Tile Inference API",
    description="Run ML inference on satellite image tiles.",
    version="0.1.0",
    lifespan=lifespan,
)


class InferenceRequest(BaseModel):
    """Request payload for tile inference."""

    tile_path: str


class InferenceResponse(BaseModel):
    """Response payload for tile inference."""

    prediction: int
    mean_intensity: float
    model_path: str


def _validate_tile_path(user_path: str) -> Path:
    """Validate and resolve a user-provided tile path safely.

    Prevents path traversal by ensuring the resolved path stays within
    ALLOWED_TILE_DIRECTORY.
    """
    try:
        resolved_path = (ALLOWED_TILE_DIRECTORY / user_path).resolve()
    except (OSError, ValueError) as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tile path.",
        ) from err

    if not resolved_path.is_relative_to(ALLOWED_TILE_DIRECTORY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this path is not allowed.",
        )
    if not resolved_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tile file not found.",
        )

    return resolved_path


@app.post("/infer", response_model=InferenceResponse)
def infer_tile(request: InferenceRequest) -> dict[str, str | float | int]:
    """Run inference on a single satellite image tile."""
    tile_path = _validate_tile_path(request.tile_path)

    try:
        validate_raster(tile_path)
        tile = load_tile(tile_path)
    except (PipelineError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    current_model = model
    if current_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded. Please try again later.",
        )

    with Timer() as timer:
        result = predict(tile, current_model)

    metrics.increment("api_requests_success")
    metrics.record_timing("api_inference_seconds", timer.duration or 0.0)

    logger.info(
        "Inference succeeded | tile=%s | duration=%.4fs",
        tile_path.name,
        timer.duration or 0.0,
    )

    return {
        "prediction": result["prediction"],
        "mean_intensity": result["mean_intensity"],
        "model_path": str(MODEL_PATH),
    }
