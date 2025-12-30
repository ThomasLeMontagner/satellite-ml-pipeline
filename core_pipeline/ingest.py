"""
Data ingestion module for the satellite ML pipeline.

Key design decisions:
- Keep ingestion deterministic and idempotent: downloading the same dataset multiple
  times should not create duplicates or side effects.
- Separate ingestion from validation and preprocessing to keep responsibilities
  clear and composable.
- Use a small, openly available GeoTIFF sample to demonstrate geospatial handling
  without introducing unnecessary dataset complexity at this stage.
"""

import logging
import urllib.request
from pathlib import Path

from shared.config import RAW_DATA_DIRECTORY

SAMPLE_URL: str = "https://download.osgeo.org/geotiff/samples/usgs/o41078a5.tif"
OUTPUT_FILE: Path = RAW_DATA_DIRECTORY / "sample.tif"


def download_sample() -> None:
    """Download a sample GeoTIFF file if it does not already exist locally."""
    RAW_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

    if OUTPUT_FILE.exists():
        logging.info("File already exists: %s", OUTPUT_FILE)
        return

    logging.info("Downloading sample GeoTIFF...")
    urllib.request.urlretrieve(SAMPLE_URL, OUTPUT_FILE)
    logging.info("Saved to %s", OUTPUT_FILE)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    download_sample()
