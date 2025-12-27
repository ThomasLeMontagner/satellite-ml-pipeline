# Scalable Satellite Tile Inference Pipeline

## Overview

This project demonstrates a **production-oriented machine learning inference pipeline** for satellite imagery.  
The focus is on **engineering concerns** — data ingestion, reproducibility, model versioning, batch and API inference, and observability — rather than on model complexity or state-of-the-art computer vision techniques.

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

Key assumptions:
- Raster imagery with consistent spatial resolution
- Metadata includes CRS and acquisition time
- Images may be large and require tiling for efficient processing

Basic validation is performed to ensure:
- Expected image shape and data type
- CRS consistency
- Presence of required metadata

---

## Model

The ML model used in this project is intentionally simple.

Rationale:
- The objective is to demonstrate **model lifecycle management**, not model performance.
- A lightweight model allows the focus to remain on:
  - Versioning
  - Reproducibility
  - Deployment mechanics

Each trained model is assigned a **unique version identifier**, which is logged during inference.

---

## Inference Workflows

### Batch Inference

Batch inference processes directories of image tiles and is intended for large-scale workloads.

Characteristics:
- Deterministic execution based on configuration files
- Explicit failure handling and logging
- Designed to be orchestrated by an external scheduler

### Online Inference API

A REST API exposes on-demand inference for individual tiles.

Characteristics:
- Stateless service
- Low latency
- Not orchestrated by a workflow engine
- Designed for horizontal scaling

---

## Orchestration (Optional)

Batch inference workflows can optionally be orchestrated using **Apache Airflow**.

Airflow is used **only** for:
- Scheduling batch jobs
- Managing task dependencies
- Handling retries and failures

Airflow is **not** used for:
- Real-time inference
- Model serving
- Low-latency workloads

This reflects a common production pattern where orchestration frameworks are reserved for batch processing, while online services remain decoupled.

---

## Observability

Basic observability is implemented to support production use:

- Inference latency logging
- Failure counts
- Model version tracking
- Input data hashing for traceability

The goal is awareness and debuggability rather than a full monitoring stack.

---

## Reproducibility

Reproducibility is supported through:

- Configuration-driven execution
- Fixed random seeds
- Deterministic preprocessing steps
- Explicit model versioning

This allows results to be regenerated given the same inputs and configuration.

---

## Running the Project

### Local execution

```bash
# Batch inference
python core_pipeline/run_batch_inference.py --config configs/pipeline.yaml

# Start API
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker-compose up --build
```

---

## Trade-offs and Future Improvements

This project intentionally makes several trade-offs:

- Model complexity is kept low in favor of pipeline clarity.
- Storage backends are simplified.
- Monitoring is lightweight.

Possible extensions:
- Distributed execution for large-scale inference
- More advanced model registry
- Integration with object storage
- Metrics export to a monitoring backend

---

## What This Project Demonstrates

- Designing ML systems with **production constraints in mind**
- Clear separation between batch and online workloads
- Awareness of orchestration trade-offs
- Emphasis on maintainability and scalability over experimentation

---

## Disclaimer

This project is intended as an **engineering demonstration** and not as a production-ready satellite analytics platform.
