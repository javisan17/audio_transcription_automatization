"""Central logging configuration for the project.

Usage:
    from logger import setup_logging, get_logger
    setup_logging()  # optional; get_logger calls it lazily
    logger = get_logger(__name__)
"""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler


DEFAULT_LEVEL = logging.INFO
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOGFILE = os.environ.get(
    "AUDIO_APP_LOG", os.path.join(os.path.dirname(__file__), "..", "logs", "app.log")
)


def setup_logging(level: int = DEFAULT_LEVEL, log_file: str | None = None) -> None:
    """Configure the root logger once.

    - Adds a StreamHandler with a simple formatter.
    - Optionally adds a RotatingFileHandler when `log_file` is provided.
    - No-op if the root logger already has handlers (to avoid double configuration).
    """
    root = logging.getLogger()
    if root.handlers:
        return

    fmt = logging.Formatter(DEFAULT_FORMAT)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    root.addHandler(sh)

    root.setLevel(level)

    if log_file is None:
        log_file = DEFAULT_LOGFILE

    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        fh = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024,
                                backupCount=3, encoding="utf-8")
        fh.setFormatter(fmt)
        root.addHandler(fh)
    except Exception:
        # Best-effort: if file handler cannot be created, continue with stream handler.
        root.debug("Failed to create file handler for logging," \
        " continuing with stream handler only.")


def get_logger(name: str) -> logging.Logger:
    """Return a module logger; ensures logging is configured.

    This helper centralizes setup and usage across the codebase.
    """
    setup_logging()
    return logging.getLogger(name)
