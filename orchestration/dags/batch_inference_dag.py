"""
Airflow DAG for batch inference on satellite image tiles.

Key design decisions:
- Airflow is used only for orchestration, not business logic.
- Core ML logic remains in Python modules and is reusable outside Airflow.
- The DAG triggers a deterministic batch inference run over existing tiles.
"""

from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core_pipeline.batch_inferences import run_batch_inference


DEFAULT_ARGS = {
    "owner": "ml-platform",
    "retries": 1,
}


def run_batch_inference_task() -> None:
    """Wrapper task to execute batch inference."""
    run_batch_inference(
        tiles_directory=Path("/opt/airflow/data/tiles"),
        model_path=Path("/opt/airflow/models/latest_model.json"),
        output_path=Path("/opt/airflow/outputs/batch_predictions.json"),
    )


with DAG(
    dag_id="satellite_batch_inference",
    description="Run batch ML inference over satellite image tiles",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2025, 12, 30),
    schedule="@daily",
    catchup=False,
    tags={"ml", "batch", "satellite"},
) as dag:

    batch_inference = PythonOperator(
        task_id="run_batch_inference",
        python_callable=run_batch_inference_task,
    )

    batch_inference
