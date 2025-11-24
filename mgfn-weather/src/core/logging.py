"""Logging configuration."""

import logging

from src.core.config import settings


def configure_logging():
    """Configures logging."""

    logging_level = logging.DEBUG if settings.DEBUG else logging.INFO
    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s: %(lineno)d - %(message)s",
        datefmt="%H:%M:%S",
    )
