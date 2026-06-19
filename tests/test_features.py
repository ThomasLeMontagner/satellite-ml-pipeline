import numpy as np

from model.features import extract_features


def test_extract_features_returns_expected_mean_and_std() -> None:
    tile = np.array([[1, 2], [3, 4]], dtype=np.uint8)

    result = extract_features(tile)

    assert result["mean_intensity"] == 2.5
    assert result["std_intensity"] == float(np.std(tile.astype(np.float32).ravel()))


def test_extract_features_is_deterministic() -> None:
    tile = np.array([[[0, 5], [10, 15]]], dtype=np.int16)

    first = extract_features(tile)
    second = extract_features(tile)

    assert first == second
