"""
Validation module for satellite raster inputs.

Key design decisions:
- Fail fast: invalid inputs should stop the pipeline early rather than
  propagate subtle errors downstream.
- Validate only properties that are critical for correctness and scalability
  (CRS, dimensions, data type), not dataset-specific semantics.
- Keep validation lightweight and deterministic so it can be run as part of
  every batch or scheduled workflow.
"""

from __future__ import annotations

import logging
from pathlib import Path

import rasterio
from rasterio.crs import CRS

from core_pipeline.exceptions import UndefinedCRSError, InvalidRasterDimensionsError


def validate_raster_exists(path: Path) -> None:
    """Ensure that the raster file exists on disk.

    :raises: FileNotFoundError if the raster file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Raster file not found: {path}")


def validate_crs(crs: CRS | None) -> None:
    """Ensure that the raster has a defined coordinate reference system.

    :raises: UndefinedCRSError if the raster has no coordinate reference system.
    """
    if crs is None:
        raise UndefinedCRSError()


def validate_dimensions(width: int, height: int) -> None:
    """Ensure that raster dimensions are positive and non-zero.

    :raises: InvalidRasterDimensionsError if the raster dimensions are invalid.
    """
    if width <= 0 or height <= 0:
        raise InvalidRasterDimensionsError(width=width, height=height)


def validate_dtype(dtype: str) -> None:
    """Ensure that raster data type is suitable for numerical processing.

    :raises: ValueError if the raster data type is invalid.
    """
    allowed_dtypes: tuple[str, ...] = (
        "uint8",
        "uint16",
        "int16",
        "float32",
        "float64",
    )

    if dtype not in allowed_dtypes:
        raise ValueError(
            f"Unsupported raster dtype '{dtype}'. Expected one of {allowed_dtypes}."
        )


def validate_raster(path: Path) -> None:
    """Run a sequence of validation checks on a raster file before processing.

    The following checks are performed:
    - The raster file exists on disk.
    - The raster has a defined coordinate reference system (CRS).
    - The raster width and height are positive, non-zero values.
    - The raster band data type is one of the supported numeric types.

    :raises FileNotFoundError: If the raster file does not exist.
    :raises UndefinedCRSError: If the raster has no defined CRS.
    :raises InvalidRasterDimensionsError: If the raster dimensions are invalid.
    :raises ValueError: If the raster data type is not supported.
    """
    validate_raster_exists(path)

    with rasterio.open(path) as src:
        validate_crs(src.crs)
        validate_dimensions(src.width, src.height)
        validate_dtype(src.dtypes[0])

    logging.info("Validation passed for raster: %s", path)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    validate_raster(Path("data/raw/sample.tif"))
