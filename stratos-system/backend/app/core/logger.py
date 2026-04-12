import logging
import sys
from typing import Optional
from .config import Settings

settings = Settings.get()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance."""
    logger_name = name or __name__
    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
