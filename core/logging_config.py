"""
Centralized logging configuration for Splunk AI Sidekick.

This module configures Python logging for both our application and Google ADK,
following ADK guidance to use the standard logging module.

References:
- ADK Logging docs: https://google.github.io/adk-docs/observability/logging/#how-to-configure-logging
"""

from __future__ import annotations

import logging
import os
from pathlib import Path


def setup_logging(level: str | int | None = None, *, log_to_file: bool = True, unified_file: str = "logs/app.log") -> None:
    """Configure root and package loggers.

    Args:
        level: Desired log level (e.g., "DEBUG", logging.INFO). If None, uses
            env var SPLUNK_AI_LOG_LEVEL or defaults to INFO.
        log_to_file: When True, also writes logs to logs/app.log.
    """
    # Determine log level
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()

    resolved_level: int
    if isinstance(level, int):
        resolved_level = level
    else:
        resolved_level = getattr(logging, str(level).upper(), logging.INFO)

    # Avoid adding duplicate handlers if called multiple times
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(
            level=resolved_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    else:
        root_logger.setLevel(resolved_level)

    # Ensure our package and ADK loggers honor desired levels
    logging.getLogger("ai_sidekick_for_splunk").setLevel(resolved_level)
    # ADK logs appear under this hierarchy in this project
    logging.getLogger("google_adk").setLevel(resolved_level)
    logging.getLogger("google").setLevel(resolved_level)

    # Optional file handler
    if log_to_file:
        try:
            logs_dir = Path(unified_file).parent
            logs_dir.mkdir(parents=True, exist_ok=True)
            file_path = Path(unified_file)

            has_file_handler = any(
                isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", "").endswith(str(file_path))
                for h in root_logger.handlers
            )
            if not has_file_handler:
                file_handler = logging.FileHandler(file_path)
                file_handler.setLevel(resolved_level)
                file_handler.setFormatter(
                    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
                )
                root_logger.addHandler(file_handler)
        except Exception:  # best-effort file logging; never break runtime
            pass
