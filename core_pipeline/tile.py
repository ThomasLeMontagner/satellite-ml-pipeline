import logging
from pathlib import Path

import rasterio
from rasterio.windows import Window


def generate_tiles(input_tif: Path, output_path: Path, tile_size: int = 256) -> None:
    """Split a raster image into fixed-size tiles and write them to disk."""
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
        input_tif=Path("data/raw/sample.tif"),
        output_path=Path("data/tiles"),
        tile_size=256,
    )
