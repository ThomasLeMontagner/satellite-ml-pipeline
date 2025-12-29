"""Contains specific exceptions for the pipeline."""

from typing import Any


class PipelineError(Exception):
    """Base exception class for pipeline."""


class TileSizeTypeError(PipelineError):
    """Raised when a tile size type is invalid."""

    def __init__(self, tile_size: Any) -> None:
        """Initializes the exception with a specific message."""
        message = (
            f"tile_size must be an integer number of pixels. Received {type(tile_size)}"
        )
        super().__init__(message)


class TileSizeValueError(PipelineError):
    """Raised when a tile size value is invalid."""

    def __init__(self, tile_size: int) -> None:
        """Initializes the exception with a specific message."""
        message = (
            f"tile_size must be a positive integer number of pixels. Received {tile_size}"
        )
        super().__init__(message)


class UndefinedCRSError(PipelineError):
    """Raised when a raster has an undefined coordinate reference system."""

    def __init__(self) -> None:
        """Initializes the exception with a specific message."""
        message = "Raster has no CRS defined."
        super().__init__(message)


class InvalidRasterDimensionsError(PipelineError):
    """Raised when a raster dimension is invalid."""

    def __init__(self, height: int, width: int) -> None:
        """Initializes the exception with a specific message."""
        message = f"Invalid raster dimensions: width={width}, height={height}"
        super().__init__(message)
