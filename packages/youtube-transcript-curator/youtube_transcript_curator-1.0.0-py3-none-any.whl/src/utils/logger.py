"""Logging configuration for YouTube Transcript Curator."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = 'INFO',
    log_file: Optional[Path] = None,
    console_output: bool = True,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Setup application logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        console_output: Whether to output logs to console
        log_format: Optional custom log format string

    Returns:
        Configured root logger
    """
    # Default format
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_formatter = logging.Formatter(log_format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        # Ensure log directory exists
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
