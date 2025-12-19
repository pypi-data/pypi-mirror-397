"""Logging and utility functions."""

import logging
from pathlib import Path

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging for the package."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("dwf_sim")

def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path