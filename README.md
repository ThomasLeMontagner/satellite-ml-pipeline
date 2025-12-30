# Scalable Satellite Tile Inference Pipeline

## Overview

This project demonstrates a **production-oriented machine learning inference pipeline** for satellite imagery.  
The focus is on **engineering concerns**, data ingestion, reproducibility, model versioning, batch and API inference, and observability, rather than on model complexity or state-of-the-art computer vision techniques.

The pipeline operates on **open satellite imagery**, splits large raster images into tiles, and runs a lightweight ML model on each tile using both batch workflows and an online inference API.

---

## Design Goals

The primary goals of this project are:

- **Scalability**  
  Design the pipeline so that it can scale to large volumes of satellite imagery without changing core abstractions.

- **Reproducibility**  
  Ensure that model outputs can be traced back to a specific model version, configuration, and input data.

- **Production readiness**  
  Favor clear interfaces, deterministic behavior, and explicit error handling over experimental flexibility.

- **Separation of concerns**  
  Clearly separate data processing, model logic, orchestration, and serving.

---

## High-Level Architecture

```
Satellite imagery
        ↓
Data ingestion & validation
        ↓
Tiling / preprocessing
        ↓
Batch inference pipeline
        ↓
Results + metrics storage

                    ┌──────────────┐
                    │  REST API    │
                    │  (FastAPI)   │
                    └──────┬───────┘
                           ↓
                   On-demand inference
```

Two execution modes are supported:

- **Batch inference** for large-scale, scheduled processing
- **Online inference** via a stateless REST API for low-latency requests

---

## Data

The pipeline operates on **open satellite imagery** (e.g. Sentinel-2 or Landsat data).

### Sample Data

The project includes a data ingestion module (`core_pipeline/ingest.py`) that downloads a sample GeoTIFF from the USGS archive for demonstration purposes.

Key assumptions:
- Raster imagery with consistent spatial resolution
- Metadata includes CRS and acquisition time
- Images may be large and require tiling for efficient processing

### Tiling Process

Large raster images are split into fixed-size tiles (default: 256x256 pixels) using `core_pipeline/tile.py`:
- Deterministic tiling using fixed pixel dimensions
- Windowed reads to avoid loading entire images into memory
- Partial tiles at boundaries are skipped for uniform shapes
- Geospatial metadata (CRS and affine transform) is preserved for each tile

Basic validation is performed to ensure:
- Expected image shape and data type
- CRS consistency
- Presence of required metadata

---

## Model

The ML model used in this project is intentionally simple: a **threshold-based classifier**.

### Model Implementation

- **Training**: Calculates a threshold from the mean intensity of training tiles
- **Inference**: Classifies tiles based on whether their mean intensity exceeds the threshold
- **Features**: Extracts basic statistics (mean intensity) from each tile
- **Serialization**: Models are saved as JSON files with unique version IDs

Rationale:
- The objective is to demonstrate **model lifecycle management**, not model performance.
- A lightweight model allows the focus to remain on:
  - Versioning (UUID-based model identifiers)
  - Reproducibility (deterministic training and inference)
  - Deployment mechanics (loading, serving, batch processing)
  - Health monitoring (model drift detection)

Each trained model is assigned a **unique version identifier**, which is logged during inference for full traceability.

---

## Inference Workflows

### Batch Inference

Batch inference processes directories of image tiles and is intended for large-scale workloads.

**Entry Point**: `core_pipeline/batch_inferences.py`

Characteristics:
- Processes all `.tif` files in the tiles directory sequentially
- Loads a single immutable model artifact per batch run
- Deterministic execution with explicit configuration
- Comprehensive logging and failure handling
- Outputs predictions to JSON with batch-level metadata
- Includes monitoring metrics (inference time, success/failure counts)
- Generates model health reports with recommendations

**Output Structure**:
```json
{
  "metadata": {
    "run_id": "uuid",
    "model_path": "path/to/model",
    "tiles_inferred": 100,
    "tiles_failed": 2,
    "monitoring": {...},
    "health_report": {...}
  },
  "predictions": [...]
}
```

### Online Inference API

A REST API exposes on-demand inference for individual tiles.

**Entry Point**: `api/app.py`

Characteristics:
- Stateless FastAPI service
- Model loaded once at startup for low latency
- Path validation and security (prevents path traversal)
- Consistent inference logic with batch workflows
- Request/response validation using Pydantic models
- Metrics tracking (latency, success counts)

**API Endpoint**: `POST /infer`

**Request**:
```json
{
  "tile_path": "relative/path/to/tile.tif"
}
```

**Response**:
```json
{
  "prediction": 1,
  "mean_intensity": 123.45,
  "model_path": "model/models/latest_model.json"
}
```

---

## Orchestration (Optional)

Batch inference workflows can optionally be orchestrated using **Apache Airflow**.

### Airflow DAG

The project includes a pre-configured DAG at `orchestration/dags/batch_inference_dag.py` that:
- Runs daily batch inference on all tiles
- Uses the latest trained model
- Saves predictions to a JSON output file

Airflow is used **only** for:
- Scheduling batch jobs
- Managing task dependencies
- Handling retries and failures

Airflow is **not** used for:
- Real-time inference
- Model serving
- Low-latency workloads

### Running with Airflow

To use the Airflow orchestration:

1. Ensure Apache Airflow 3.1.5+ is installed
2. Configure Airflow to discover DAGs from the `orchestration/dags/` directory
3. The DAG will execute the batch inference task on a daily schedule

This reflects a common production pattern where orchestration frameworks are reserved for batch processing, while online services remain decoupled.

---

## Observability

The pipeline implements comprehensive observability to support production use:

### Metrics Tracking

Implemented via `core_pipeline/observability.py`:

- **Inference latency**: Timing for individual tiles and full batch runs
- **Success/failure counts**: Track tiles processed successfully vs failed
- **Prediction distribution**: Count predictions by class
- **Feature statistics**: Mean intensity values across tiles
- **Model health monitoring**: Detect potential model drift

### Structured Logging

All modules use structured logging via `utils/logging.py`:
- Consistent log format across the pipeline
- Contextual information (run_id, tile_id, model_path)
- Separate loggers for different components (API, batch, training)

### Model Health Checks

The `model/health.py` module provides:
- Automated health assessment based on inference metrics
- Recommendations for model retraining or investigation
- Integration with batch inference output

### Traceability

Full traceability is maintained through:
- Unique run IDs for each batch execution
- Model version tracking (UUID-based)
- Input data hashing for reproducibility
- Per-tile prediction logs with metadata

The goal is awareness and debuggability rather than a full monitoring stack.

---

## Reproducibility

Reproducibility is a core design principle supported through:

- **Configuration-driven execution**: All paths and parameters defined in `constants.py`
- **Fixed random seeds**: Deterministic behavior in model training (where applicable)
- **Deterministic preprocessing**: Consistent tiling with fixed sizes and skipping partial tiles
- **Explicit model versioning**: UUID-based identifiers for all trained models
- **Immutable artifacts**: Models are never modified after training, only new versions created
- **Metadata tracking**: Full lineage from raw data → tiles → training → inference
- **Snapshot persistence**: Batch inference outputs include all relevant metadata

Given the same:
- Input raster image
- Tile size configuration
- Model artifact

The pipeline will produce identical results, enabling result regeneration and debugging.

---

## Prerequisites

- Python 3.10 or higher
- pip package manager

---

## Installation

```bash
# Clone the repository
git clone https://github.com/ThomasLeMontagner/satellite-ml-pipeline.git
cd satellite-ml-pipeline

# Install dependencies
pip install -r requirements.txt
```

**Important**: When running Python scripts, you need to set the `PYTHONPATH` to the project root:

```bash
export PYTHONPATH=/path/to/satellite-ml-pipeline
```

Or prefix each command with:

```bash
PYTHONPATH=/path/to/satellite-ml-pipeline python <script.py>
```

Alternatively, you can install the package in editable mode:

```bash
pip install -e .
```

Note: This requires adding a `setup.py` or configuring `pyproject.toml` with build-system information.

---

## Project Structure

```
satellite-ml-pipeline/
├── api/                    # FastAPI inference service
│   └── app.py              # REST API for on-demand inference
├── core_pipeline/          # Core data processing pipeline
│   ├── ingest.py           # Data ingestion
│   ├── tile.py             # Raster tiling
│   ├── batch_inferences.py # Batch inference execution
│   ├── validate.py         # Data validation
│   └── observability.py    # Metrics and monitoring
├── model/                  # ML model components
│   ├── train.py            # Model training logic
│   ├── train_from_tiles.py # Training entry point
│   ├── inferences.py       # Inference logic
│   ├── features.py         # Feature extraction
│   ├── health.py           # Model health checks
│   └── registry.py         # Model versioning
├── orchestration/          # Airflow orchestration
│   └── dags/
│       └── batch_inference_dag.py
├── utils/                  # Shared utilities
├── constants.py            # Project constants
├── requirements.txt        # Python dependencies
└── pyproject.toml          # Project configuration (ruff linting)
```

---

## Running the Project

**Note**: All commands assume `PYTHONPATH` is set to the project root, or the package is installed in editable mode.

### Step 1: Download Sample Data

```bash
# Download a sample GeoTIFF file
PYTHONPATH=. python core_pipeline/ingest.py
```

### Step 2: Generate Tiles

```bash
# Split the raw image into 256x256 tiles
PYTHONPATH=. python core_pipeline/tile.py
```

### Step 3: Train Model

```bash
# Train a simple threshold-based model from tiles
PYTHONPATH=. python model/train_from_tiles.py
```

### Step 4: Run Batch Inference

```bash
# Process all tiles in the tiles directory
PYTHONPATH=. python core_pipeline/batch_inferences.py
```

### Step 5: Start API Server

```bash
# Start the FastAPI inference service
PYTHONPATH=. uvicorn api.app:app --host 0.0.0.0 --port 8000
```

### Linting and Formatting

```bash
# Run ruff linter
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

---

## Technology Stack

### Core Dependencies

- **Python 3.10+**: Modern Python with type hints
- **FastAPI 0.117+**: High-performance async web framework for API
- **Rasterio 1.4+**: Geospatial raster I/O
- **NumPy 2.4+**: Numerical computing
- **Pydantic 2.12+**: Data validation and settings
- **Apache Airflow 3.1+**: Workflow orchestration (optional)
- **Ruff 0.14+**: Fast Python linter and formatter

### Development Tools

- **Ruff**: Linting and code formatting (configured in `pyproject.toml`)
- **Type hints**: Full type annotations for better IDE support
- **Structured logging**: Consistent logging patterns across modules

---

## Trade-offs and Future Improvements

This project intentionally makes several trade-offs to emphasize engineering clarity:

### Current Limitations

- Model complexity is kept low (simple threshold classifier)
- Storage backends are simplified (local filesystem only)
- Monitoring is lightweight (metrics in-memory, not exported)
- No distributed processing (sequential tile processing)
- No Docker containerization yet

### Possible Extensions

- **Scalability**: Distributed execution for large-scale inference (Dask, Ray)
- **Storage**: Integration with object storage (S3, GCS, Azure Blob)
- **Model registry**: More advanced versioning and deployment (MLflow, W&B)
- **Monitoring**: Metrics export to Prometheus/Grafana
- **Containerization**: Docker and Kubernetes deployment
- **Testing**: Comprehensive unit and integration tests
- **CI/CD**: Automated testing and deployment pipelines
- **Advanced models**: Integration with deep learning frameworks (PyTorch, TensorFlow)

---

## What This Project Demonstrates

- Designing ML systems with **production constraints in mind**
- Clear separation between batch and online workloads
- Awareness of orchestration trade-offs
- Emphasis on maintainability and scalability over experimentation

---

## Disclaimer

This project is intended as an **engineering demonstration** and not as a production-ready satellite analytics platform.
