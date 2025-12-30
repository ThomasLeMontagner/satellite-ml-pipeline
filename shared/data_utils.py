"""Shared data utilities for loading raster data."""

from pathlib import Path

import numpy as np
import rasterio


def load_tile(path: Path) -> np.ndarray:
    """Load a raster tile from disk as a NumPy array."""
    with rasterio.open(path) as source:
        return source.read()
