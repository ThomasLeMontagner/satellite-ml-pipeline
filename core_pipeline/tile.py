"""
Raster tiling module for satellite imagery.

Key design decisions:
- Tile raster images using fixed pixel dimensions to keep tiling simple,
  deterministic, and independent of geographic resolution.
- Avoid loading entire images into memory by reading windowed subsets of the raster.
- Skip partial tiles at image boundaries to keep tile shapes uniform, which
  simplifies downstream batch processing and ML inference.
- Preserve geospatial metadata (CRS and affine transform) for each tile to ensure
  spatial correctness in downstream pipelines.
"""

import logging
from pathlib import Path

import rasterio
from rasterio.windows import Window

from core_pipeline.constants import DATA_DIRECTORY


def generate_tiles(input_tif: Path, output_path: Path, tile_size: int = 256) -> None:
    """Split a raster image into fixed-size tiles and write them to disk."""
    if not isinstance(tile_size, int):
        raise TypeError(f"tile_size must be an integer number of pixels. Received {type(tile_size)}")
    if tile_size <= 0:
        raise ValueError(f"tile_size must be a positive integer number of pixels. Received {tile_size}")

    output_path.mkdir(parents=True, exist_ok=True)

    with rasterio.open(input_tif) as source:
        width = source.width
        height = source.height
        transform = source.transform

        tile_id = 0

        for row in range(0, height, tile_size):
            for column in range(0, width, tile_size):
                # Skip partial tiles at image boundaries
                if row + tile_size > height or column + tile_size > width:
                    continue

                window = Window(column, row, tile_size, tile_size)
                tile_data = source.read(window=window)

                tile_transform = rasterio.windows.transform(window, transform)

                tile_meta = source.meta.copy()
                tile_meta.update(
                    {
                        "height": height,
                        "width": width,
                        "transform": tile_transform,
                    }
                )

                tile_path = output_path / f"{tile_id:05d}.tif"

                with rasterio.open(tile_path, "w", **tile_meta) as dst:
                    dst.write(tile_data)

                tile_id += 1

    logging.info(f"Generated {tile_id} tiles")


if __name__ == "__main__":
    generate_tiles(
        input_tif=DATA_DIRECTORY / "sample.tif",
        output_path=Path("../data/tiles"),
        tile_size=256,
    )
