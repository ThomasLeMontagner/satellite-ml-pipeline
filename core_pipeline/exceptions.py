"""Contains specific exceptions for the pipeline."""

from typing import Any

from rasterio import CRS


class PipelineException(Exception):
    """Base exception class for pipeline."""


class TileSizeTypeError(PipelineException):
    """Raised when a tile size type is invalid."""

    def __init__(self, tile_size: Any) -> None:
        """Initializes the exception with a specific message."""
        message = (
            f"tile_size must be an integer number of pixels. Received {type(tile_size)}"
        )
        super().__init__(message)


class TileSizeValueError(PipelineException):
    """Raised when a tile size value is invalid."""

    def __init__(self, tile_size: int) -> None:
        """Initializes the exception with a specific message."""
        message = f"tile_size must be a positive integer number of pixels. Received {tile_size}"
        super().__init__(message)


class UndefinedCRSError(PipelineException):
    """Raised when a raster has an undefined coordinate reference system."""

    def __init__(self, crs: CRS) -> None:
        """Initializes the exception with a specific message."""
        message = "Raster has no CRS defined"
        super().__init__(message)


class InvalidRasterDimensionsError(PipelineException):
    """Raised when a raster dimension is invalid."""

    def __init__(self, height: int, width: int) -> None:
        """Initializes the exception with a specific message."""
        message = f"Invalid raster dimensions: width={width}, height={height}"
        super().__init__(message)
