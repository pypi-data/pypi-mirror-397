"""
Utility functions for the alembic-converger package.
"""

import logging
from pathlib import Path
from typing import Optional


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging for the package.

    Args:
        verbose: If True, set log level to DEBUG, otherwise INFO.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger("alembic_converger")

    if logger.handlers:
        # Already configured
        return logger

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    return logger


def get_logger() -> logging.Logger:
    """Get the package logger.

    Returns:
        Logger instance.
    """
    return logging.getLogger("alembic_converger")


def resolve_config_path(config_path: Optional[str] = None) -> Path:
    """Resolve the Alembic configuration file path.

    Args:
        config_path: Path to alembic.ini file. If None, looks for alembic.ini
                    in the current directory.

    Returns:
        Resolved Path object.

    Raises:
        FileNotFoundError: If the configuration file doesn't exist.
    """
    if config_path is None:
        config_path = "alembic.ini"

    path = Path(config_path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"Alembic configuration file not found: {path}")

    return path


def format_revision_id(revision: Optional[str]) -> str:
    """Format a revision ID for display.

    Args:
        revision: Revision ID or None.

    Returns:
        Formatted string.
    """
    if revision is None:
        return "<none>"
    return revision[:12] if len(revision) > 12 else revision
