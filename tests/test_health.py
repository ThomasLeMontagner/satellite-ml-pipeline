from model.health import CONSIDER_RETRAINING_MODEL, check_model_health


def test_check_model_health_no_drift() -> None:
    model = {"threshold": 2.0, "training_mean": 10.0, "training_std": 2.0}
    monitoring = {
        "prediction_distribution": {
            "bright_percentage": 50.0,
            "bright_count": 5,
            "dark_count": 5,
        },
        "mean_intensity": {"mean": 10.2, "std": 2.1},
        "drift": {"mean_intensity_delta": 0.2, "std_intensity_delta": 0.1},
    }

    report = check_model_health(model, monitoring, drift_threshold=0.5)

    assert report["drift_detected"] is False
    assert report["recommendations"] == []
    assert report["mean_intensity_delta"] == 0.2
    assert report["std_intensity_delta"] == 0.1


def test_check_model_health_detects_drift_and_recommends_retraining() -> None:
    model = {"threshold": 2.0, "training_mean": 10.0, "training_std": 2.0}
    monitoring = {
        "prediction_distribution": {
            "bright_percentage": 80.0,
            "bright_count": 8,
            "dark_count": 2,
        },
        "mean_intensity": {"mean": 12.0, "std": 3.0},
        "drift": {"mean_intensity_delta": 2.0, "std_intensity_delta": 1.0},
    }

    report = check_model_health(model, monitoring, drift_threshold=0.5)

    assert report["drift_detected"] is True
    assert report["recommendations"] == [CONSIDER_RETRAINING_MODEL]
    assert report["mean_intensity_delta"] == 2.0
    assert report["std_intensity_delta"] == 1.0
