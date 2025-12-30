# Project Structure Improvements

## Overview

This document describes the restructuring of the satellite-ml-pipeline project to reduce interdependencies between packages and create a cleaner, more maintainable architecture.

## Previous Issues

### 1. Circular Dependencies
The project had a circular dependency between `core_pipeline` and `model`:
- `core_pipeline.observability` imported `model.train.Model`
- `core_pipeline.batch_inferences` imported `model.health` and `model.inferences`
- `model.health` imported from `core_pipeline.observability` and `core_pipeline.types_`
- `model.train_from_tiles` imported from `core_pipeline.tile`

This circular dependency made it difficult to:
- Understand the module hierarchy
- Test modules independently
- Reuse modules in other contexts
- Reason about dependency flow

### 2. Root-level constants
The `constants.py` file at the root level was used across multiple packages, creating coupling and making it unclear which package owned the configuration.

### 3. Scattered type definitions
Type definitions were scattered across packages:
- `Model` type was in `model.train`
- `MonitoringMetrics` types were in `core_pipeline.types_`
- This caused cross-package dependencies just for type hints

## New Architecture

### Package Hierarchy

The restructured project now has a clear dependency hierarchy:

```
shared (no dependencies)
  ↓
model (depends only on shared)
  ↓
core_pipeline (depends on shared, model)
  ↓
api, orchestration (depend on core_pipeline, model, shared)
```

### The `shared` Package

A new `shared` package has been created to contain truly shared utilities, types, and constants:

- **`shared/types.py`**: All shared type definitions
  - `Model`: The trained model structure
  - `MonitoringMetrics`, `PredictionDistributionMetrics`, `MeanIntensityMetrics`, `DriftMetrics`: Metrics types
  
- **`shared/config.py`**: Path and configuration constants
  - `DATA_DIRECTORY`, `RAW_DATA_DIRECTORY`, `TILES_DIRECTORY`, `MODELS_DIRECTORY`
  
- **`shared/constants.py`**: Application constants
  - `TILES_INFERRED`, `TILES_FAILED`
  
- **`shared/observability.py`**: Basic logging setup
  - `setup_logger()`: Standard logger configuration
  
- **`shared/data_utils.py`**: Data loading utilities
  - `load_tile()`: Load raster tiles from disk

### Changes to Existing Packages

#### `model` package
- **Removed dependencies on `core_pipeline`**
- Now imports types from `shared.types` instead of `core_pipeline.types_`
- Uses `shared.observability.setup_logger` instead of `core_pipeline.observability.setup_logger`
- Uses `shared.data_utils.load_tile` instead of `core_pipeline.tile.load_tile`

#### `core_pipeline` package
- **Removed dependencies on `model` for types**
- Imports `Model` from `shared.types` instead of `model.train`
- `observability.py` no longer needs to import from `model`
- `pipeline_constants.py` has been removed (constants moved to `shared.constants`)
- `types_.py` has been removed (types moved to `shared.types`)
- `tile.py` no longer contains `load_tile()` (moved to `shared.data_utils`)

#### `api` package
- Updated to import from `shared` package where appropriate

#### `orchestration` package
- No changes to imports, but now benefits from clearer dependency structure

### Removed Files

- `constants.py` (root level) → replaced by `shared/config.py`
- `core_pipeline/pipeline_constants.py` → merged into `shared/constants.py`
- `core_pipeline/types_.py` → moved to `shared/types.py`

## Benefits

1. **No circular dependencies**: Clean, unidirectional dependency flow
2. **Better testability**: Each package can be tested independently
3. **Clearer ownership**: Shared utilities are explicitly in the `shared` package
4. **Easier to understand**: Dependency hierarchy is immediately clear
5. **More maintainable**: Changes to shared types don't require touching multiple packages
6. **Better reusability**: Packages can be reused in different contexts without dragging in unnecessary dependencies

## Dependency Verification

You can verify the dependency structure using a simple script:

```python
# See /tmp/analyze_deps_v2.py for the full implementation
python /tmp/analyze_deps_v2.py /path/to/satellite-ml-pipeline
```

Expected output:
```
=== Package Dependencies ===

api:
  -> core_pipeline
  -> model
  -> shared

core_pipeline:
  -> model
  -> shared

model:
  -> shared

orchestration:
  -> core_pipeline
```

## Migration Guide

If you have existing code that imports from the old locations, update as follows:

### Type Imports
```python
# Old
from model.train import Model
from core_pipeline.types_ import MonitoringMetrics

# New
from shared.types import Model, MonitoringMetrics
```

### Constants
```python
# Old
from constants import MODELS_DIRECTORY, TILES_DIRECTORY
from core_pipeline.pipeline_constants import TILES_INFERRED

# New
from shared.config import MODELS_DIRECTORY, TILES_DIRECTORY
from shared.constants import TILES_INFERRED
```

### Utilities
```python
# Old
from core_pipeline.observability import setup_logger
from core_pipeline.tile import load_tile

# New
from shared.observability import setup_logger
from shared.data_utils import load_tile
```

## Testing

All existing functionality remains unchanged. The restructuring is purely organizational and does not affect the behavior of the code.

To verify:
1. Run the linter: `ruff check .`
2. Test imports: `python -m py_compile shared/*.py model/*.py core_pipeline/*.py api/*.py`
3. Verify dependencies: Use the dependency analyzer script

## Future Improvements

With this cleaner structure, future improvements are easier:

1. **Package extraction**: Individual packages can now be extracted into separate repositories if needed
2. **Independent versioning**: Each package could have its own version
3. **Pluggable implementations**: The clear interfaces make it easier to swap implementations
4. **Better documentation**: Package responsibilities are now clearer
