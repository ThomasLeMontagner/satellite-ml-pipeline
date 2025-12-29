"""
API inference service for satellite image tiles.

Key design decisions:
- Expose inference via a stateless REST API.
- Load the model artifact once at startup to minimize request latency.
- Reuse the same inference logic as batch workflows to ensure consistency.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from constants import MODELS_DIRECTORY
from core_pipeline.tile import load_tile
from core_pipeline.validate import validate_raster
from model.inferences import load_model, predict
from model.train import Model

MODEL_PATH = MODELS_DIRECTORY / "latest_model.json"


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application lifespan: load and clean up resources."""
    global model
    model = load_model(str(MODEL_PATH))
    yield


app = FastAPI(
    title="Satellite Tile Inference API",
    description="Run ML inference on satellite image tiles.",
    version="0.1.0",
    lifespan=lifespan,
)

model: Model | None = None


class InferenceRequest(BaseModel):
    """Request payload for tile inference."""

    tile_path: str


class InferenceResponse(BaseModel):
    """Response payload for tile inference."""

    prediction: int
    mean_intensity: float
    model_path: str


@app.post("/infer", response_model=InferenceResponse)
def infer_tile(request: InferenceRequest) -> dict[str, object]:
    """Run inference on a single satellite image tile."""
    tile_path = Path(request.tile_path)

    try:
        validate_raster(tile_path)
        tile = load_tile(tile_path)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    result = predict(tile, model)

    return {
        "prediction": result["prediction"],
        "mean_intensity": result["mean_intensity"],
        "model_path": str(MODEL_PATH),
    }
