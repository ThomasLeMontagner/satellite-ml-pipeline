"""Shared configuration and path constants."""

from pathlib import Path

DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data"
RAW_DATA_DIRECTORY: Path = DATA_DIRECTORY / "raw"
TILES_DIRECTORY: Path = DATA_DIRECTORY / "tiles"
MODELS_DIRECTORY: Path = Path(__file__).resolve().parent.parent / "model" / "models"
