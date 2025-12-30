"""Contains the constants for the project."""

from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
DATA_DIRECTORY: Path = PROJECT_ROOT / "data"
RAW_DATA_DIRECTORY: Path = DATA_DIRECTORY / "raw"
TILES_DIRECTORY: Path = DATA_DIRECTORY / "tiles"
MODELS_DIRECTORY: Path = Path(__file__).resolve().parent / "model" / "models"
