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
from pathlib import Path
import urllib.request

logging.getLogger().setLevel(logging.INFO)

DATA_DIRECTORY: Path = Path("data/raw")
DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

SAMPLE_URL: str = "https://download.osgeo.org/geotiff/samples/usgs/o41078a5.tif"

OUTPUT_FILE: Path = DATA_DIRECTORY / "sample.tif"


def download_sample() -> None:
    """Download a sample GeoTIFF file if it does not already exist locally."""
    if OUTPUT_FILE.exists():
        logging.info(f"File already exists: {OUTPUT_FILE}")
        return

    logging.info("Downloading sample GeoTIFF...")
    urllib.request.urlretrieve(SAMPLE_URL, OUTPUT_FILE)
    logging.info(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    download_sample()
