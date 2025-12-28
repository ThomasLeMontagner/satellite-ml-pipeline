from pathlib import Path

DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data"
RAW_DATA_DIRECTORY: Path = DATA_DIRECTORY / "raw"
TILES_DIRECTORY: Path = DATA_DIRECTORY / "tiles"
