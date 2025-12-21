# Scalable Satellite Tile Inference Pipeline

## Overview

This project demonstrates a **production-oriented machine learning inference pipeline** for satellite imagery.  
The focus is on **engineering concerns** (data ingestion, reproducibility, model versioning, batch and API inference, and observability) rather than on model complexity or state-of-the-art computer vision techniques.

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

