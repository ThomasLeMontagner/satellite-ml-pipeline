"""Shared utilities for logging."""

import logging


def setup_logger(name: str) -> logging.Logger:
    """Configure and return a module-level logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False  # Prevent duplicate log messages due to propagation.
    return logger
