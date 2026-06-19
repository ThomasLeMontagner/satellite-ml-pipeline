from pathlib import Path

import numpy as np
from fastapi.testclient import TestClient

from api import app as app_module


def test_infer_endpoint_happy_path(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        app_module,
        "load_model",
        lambda _path: {"threshold": 2.0, "training_mean": 2.0, "training_std": 0.5},
    )

    allowed_dir = tmp_path / "tiles"
    allowed_dir.mkdir()
    tile_file = allowed_dir / "tile.tif"
    tile_file.write_text("placeholder")

    monkeypatch.setattr(app_module, "ALLOWED_TILE_DIRECTORY", allowed_dir)
    monkeypatch.setattr(app_module, "MODEL_PATH", tmp_path / "latest_model.json")
    monkeypatch.setattr(app_module, "validate_raster", lambda _path: None)
    monkeypatch.setattr(
        app_module, "load_tile", lambda _path: np.array([[3.0]], dtype=float)
    )
    monkeypatch.setattr(
        app_module,
        "predict",
        lambda _tile, _model: {"prediction": 1, "mean_intensity": 3.0},
    )

    with TestClient(app_module.app) as client:
        response = client.post("/infer", json={"tile_path": "tile.tif"})

    assert response.status_code == 200
    assert response.json() == {
        "prediction": 1,
        "mean_intensity": 3.0,
        "model_path": str(tmp_path / "latest_model.json"),
    }


def test_infer_endpoint_rejects_path_traversal(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(app_module, "ALLOWED_TILE_DIRECTORY", tmp_path / "tiles")

    with TestClient(app_module.app) as client:
        response = client.post("/infer", json={"tile_path": "../outside.tif"})

    assert response.status_code == 403
    assert response.json() == {"detail": "Access to this path is not allowed."}


def test_infer_endpoint_rejects_invalid_or_missing_path(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(app_module, "ALLOWED_TILE_DIRECTORY", tmp_path / "tiles")

    with TestClient(app_module.app) as client:
        response = client.post("/infer", json={"tile_path": "does-not-exist.tif"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Tile file not found."}
