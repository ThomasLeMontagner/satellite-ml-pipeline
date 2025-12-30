"""Contains the constants for the project."""

from pathlib import Path

DATA_DIRECTORY = Path(__file__).resolve().parent / "data"
RAW_DATA_DIRECTORY: Path = DATA_DIRECTORY / "raw"
TILES_DIRECTORY: Path = DATA_DIRECTORY / "tiles"
MODELS_DIRECTORY: Path = Path(__file__).resolve().parent / "model" / "models"
