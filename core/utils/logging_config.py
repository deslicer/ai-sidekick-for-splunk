"""
Centralized logging configuration for Splunk AI Sidekick.

Follows ADK guidance to use Python's logging and config from the application
entrypoint. Exposes setup_logging for unified stdout + file logging.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path


def setup_logging(level: str | int | None = None, *, log_to_file: bool = True, unified_file: str = "logs/app.log") -> None:
    """Configure root and package loggers.

    Args:
        level: Desired log level (e.g., "DEBUG", logging.INFO). If None, uses
            env var LOG_LEVEL or defaults to INFO.
        log_to_file: When True, also writes logs to unified_file.
        unified_file: Path to the single unified log file.
    """
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()

    resolved_level: int
    if isinstance(level, int):
        resolved_level = level
    else:
        resolved_level = getattr(logging, str(level).upper(), logging.INFO)

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(
            level=resolved_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    else:
        root_logger.setLevel(resolved_level)

    logging.getLogger("splunk_ai_sidekick").setLevel(resolved_level)
    logging.getLogger("google_adk").setLevel(resolved_level)
    logging.getLogger("google").setLevel(resolved_level)

    if log_to_file:
        try:
            file_path = Path(unified_file)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            has_file = any(
                isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", "").endswith(str(file_path))
                for h in root_logger.handlers
            )
            if not has_file:
                fh = logging.FileHandler(file_path)
                fh.setLevel(resolved_level)
                fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
                root_logger.addHandler(fh)
        except Exception:
            pass


