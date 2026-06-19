from constants import TILES_INFERRED
from core_pipeline.observability import MetricsRecorder, build_monitoring_metrics


def test_metrics_recorder_records_and_resets_metrics() -> None:
    recorder = MetricsRecorder()

    recorder.increment("count")
    recorder.increment("count", 2)
    recorder.record_timing("latency", 0.1)
    recorder.record_timing("latency", 0.2)
    recorder.record_value("score", 0.4)

    snapshot = recorder.snapshot()
    assert snapshot["counters"]["count"] == 3
    assert snapshot["timings"]["latency"] == [0.1, 0.2]
    assert snapshot["values"]["score"] == [0.4]

    recorder.reset()
    assert recorder.snapshot() == {"counters": {}, "timings": {}, "values": {}}


def test_build_monitoring_metrics_aggregates_distribution_and_drift() -> None:
    recorder = MetricsRecorder()
    recorder.increment(TILES_INFERRED, 4)
    recorder.increment("prediction_1", 3)
    recorder.increment("prediction_0", 1)
    recorder.record_value("mean_intensity", 10.0)
    recorder.record_value("mean_intensity", 14.0)

    model = {"threshold": 11.0, "training_mean": 8.0, "training_std": 1.0}

    metrics = build_monitoring_metrics(model, recorder)

    assert metrics["prediction_distribution"] == {
        "bright_percentage": 75.0,
        "bright_count": 3,
        "dark_count": 1,
    }
    assert metrics["mean_intensity"]["mean"] == 12.0
    assert metrics["mean_intensity"]["std"] == 2.0
    assert metrics["drift"]["mean_intensity_delta"] == 4.0
    assert metrics["drift"]["std_intensity_delta"] == 1.0
