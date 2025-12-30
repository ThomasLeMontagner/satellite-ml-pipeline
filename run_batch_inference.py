#!/usr/bin/env python3
"""
Wrapper script to run batch inference.

This script ensures the project root is in the Python path before running
the batch inference module.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import and run the batch inference function
from core_pipeline.batch_inferences import run_batch_inference
from constants import MODELS_DIRECTORY, TILES_DIRECTORY

if __name__ == "__main__":
    run_batch_inference(
        tiles_directory=TILES_DIRECTORY,
        model_path=MODELS_DIRECTORY / "latest_model.json",
        output_path=Path("outputs/batch_predictions.json"),
    )
