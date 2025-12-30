# Architecture Diagrams

## Before Restructuring

```
┌─────────────────────────────────────────────────────────┐
│                    Root Constants                       │
│                    constants.py                         │
│        (DATA_DIR, TILES_DIR, MODELS_DIR)               │
└──────────────────┬──────────────────────────────────────┘
                   │ (used by all packages)
                   │
        ┌──────────┴────────────┐
        ↓                       ↓
┌───────────────┐        ┌────────────────┐
│ core_pipeline │◄───────┤     model      │
│               │        │                │
│ - types_      │        │ - train        │
│ - observ.     │        │ - inferences   │
│ - tile        │        │ - health       │
│ - batch_inf.  │────────► - train_tiles  │
│               │        │                │
└───────┬───────┘        └────────────────┘
        │                         ↑
        │                         │
        │                    (circular!)
        │
        ↓
┌───────────────┐
│      api      │
└───────────────┘
        ↓
┌───────────────┐
│ orchestration │
└───────────────┘

Issues:
❌ Circular dependency between core_pipeline ↔ model
❌ Root-level constants used everywhere
❌ Unclear ownership of types
```

## After Restructuring

```
┌─────────────────────────────────────────────────────────┐
│                   shared package                        │
│                                                         │
│  - types.py      (Model, MonitoringMetrics, etc.)     │
│  - config.py     (DATA_DIR, TILES_DIR, etc.)          │
│  - constants.py  (TILES_INFERRED, TILES_FAILED)       │
│  - observability.py (setup_logger)                     │
│  - data_utils.py    (load_tile)                       │
│                                                         │
└────────────┬────────────────────────────────────────────┘
             │
             │ (no dependencies)
             │
             ↓
      ┌─────────────┐
      │    model    │
      │             │
      │ - train     │
      │ - inferences│
      │ - health    │
      │ - features  │
      │ - train_tiles│
      │             │
      └──────┬──────┘
             │
             │ (depends on shared only)
             │
             ↓
   ┌─────────────────┐
   │  core_pipeline  │
   │                 │
   │ - tile          │
   │ - validate      │
   │ - observability │
   │ - batch_inf.    │
   │ - ingest        │
   │ - exceptions    │
   │                 │
   └────────┬────────┘
            │
            │ (depends on shared + model)
            │
            ↓
     ┌──────┴──────┐
     ↓             ↓
┌─────────┐  ┌──────────────┐
│   api   │  │orchestration │
│         │  │              │
└─────────┘  └──────────────┘

Benefits:
✅ No circular dependencies
✅ Clear dependency hierarchy
✅ Shared utilities in one place
✅ Better testability
✅ Easier to understand
```

## Dependency Flow

```
Level 0: shared
         └─ No dependencies
            Pure utilities, types, and constants

Level 1: model
         └─ Depends on: shared
            ML model logic, training, inference

Level 2: core_pipeline
         └─ Depends on: shared, model
            Data processing, validation, batch operations

Level 3: api, orchestration
         └─ Depends on: shared, model, core_pipeline
            Application layer, service interfaces
```

## Module Responsibilities

```
┌────────────────────────────────────────────────────────┐
│                     shared                             │
│ Responsibilities:                                      │
│ • Shared type definitions                              │
│ • Configuration and path constants                     │
│ • Basic utilities (logging, data loading)              │
│ • NO business logic                                    │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                      model                             │
│ Responsibilities:                                      │
│ • Model training and serialization                     │
│ • Feature extraction                                   │
│ • Inference logic                                      │
│ • Model health checks                                  │
│ • NO data pipeline logic                               │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                  core_pipeline                         │
│ Responsibilities:                                      │
│ • Data ingestion and validation                        │
│ • Tiling and preprocessing                             │
│ • Batch inference orchestration                        │
│ • Observability and metrics                            │
│ • Error handling                                       │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                   api                                  │
│ Responsibilities:                                      │
│ • REST API endpoints                                   │
│ • Request/response handling                            │
│ • API-level error handling                             │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│               orchestration                            │
│ Responsibilities:                                      │
│ • Airflow DAG definitions                              │
│ • Task scheduling                                      │
│ • Workflow coordination                                │
└────────────────────────────────────────────────────────┘
```
