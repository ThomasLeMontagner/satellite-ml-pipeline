"""
Feature extraction for satellite image tiles.

Key design decisions:
- Extract simple, interpretable features to keep focus on pipeline mechanics.
- Operate on NumPy arrays to decouple feature logic from I/O.
- Ensure deterministic feature computation for reproducibility.
"""

from __future__ import annotations

import numpy as np


def extract_features(tile: np.ndarray) -> dict[str, float]:
    """Extract simple statistical features from a raster tile."""
    flattened = tile.astype(np.float32).ravel()

    return {
        "mean_intensity": float(np.mean(flattened)),
        "std_intensity": float(np.std(flattened)),
    }
