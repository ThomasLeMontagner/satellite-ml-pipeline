import numpy as np
import pytest

from model.inferences import predict
from model.train import train_model


def test_train_model_returns_expected_threshold_and_stats() -> None:
    aggregated_features = [
        {"mean_intensity": 1.0, "std_intensity": 0.1},
        {"mean_intensity": 3.0, "std_intensity": 0.2},
        {"mean_intensity": 5.0, "std_intensity": 0.3},
    ]

    model = train_model(aggregated_features)

    assert model["threshold"] == 3.0
    assert model["training_mean"] == 3.0
    assert model["training_std"] == float(np.std([1.0, 3.0, 5.0]))


def test_train_model_raises_for_empty_features() -> None:
    with pytest.raises(ValueError, match="aggregated_features"):
        train_model([])


def test_predict_uses_threshold() -> None:
    model = {"threshold": 2.5, "training_mean": 2.5, "training_std": 1.0}
    dark_tile = np.array([[1, 2], [2, 1]], dtype=np.float32)
    bright_tile = np.array([[3, 4], [3, 4]], dtype=np.float32)

    dark_result = predict(dark_tile, model)
    bright_result = predict(bright_tile, model)

    assert dark_result["prediction"] == 0
    assert bright_result["prediction"] == 1


def test_train_to_predict_consistency() -> None:
    training_data = [
        {"mean_intensity": 1.0, "std_intensity": 0.0},
        {"mean_intensity": 3.0, "std_intensity": 0.0},
    ]
    model = train_model(training_data)

    below_threshold = np.array([[1.0, 1.0]], dtype=np.float32)
    above_threshold = np.array([[3.0, 3.0]], dtype=np.float32)

    assert predict(below_threshold, model)["prediction"] == 0
    assert predict(above_threshold, model)["prediction"] == 1
