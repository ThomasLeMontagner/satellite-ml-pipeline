"""
API inference service for satellite image tiles.

Key design decisions:
- Expose inference via a stateless REST API.
- Load the model artifact once at startup to minimize request latency.
- Reuse the same inference logic as batch workflows to ensure consistency.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core_pipeline.tile import load_tile
from core_pipeline.validate import validate_raster
from model.inferences import load_model, predict


MODEL_PATH = Path("model/models/latest_model.json")

app = FastAPI(
    title="Satellite Tile Inference API",
    description="Run ML inference on satellite image tiles.",
    version="0.1.0",
)


class InferenceRequest(BaseModel):
    """Request payload for tile inference."""
    tile_path: str


class InferenceResponse(BaseModel):
    """Response payload for tile inference."""
    prediction: int
    mean_intensity: float
    model_path: str


@app.on_event("startup")
def load_model_on_startup() -> None:
    """Load the ML model artifact at application startup."""
    global model
    model = load_model(str(MODEL_PATH))



@app.post("/inference", response_model=InferenceResponse)
def infer_tile(request: InferenceRequest) -> dict[str, object]:
    """Run inference on a single satellite image tile."""
    tile_path = Path(request.tile_path)

    try:
        validate_raster(tile_path)
        tile = load_tile(tile_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    result = predict(tile, model)

    return {
        "prediction": result["prediction"],
        "mean_intensity": result["mean_intensity"],
        "model_path": str(MODEL_PATH),
    }
