"""
Splunk AI Sidekick - Root Agent Entry Point for ADK Web Interface.

This module provides the root_agent that ADK web interface expects to find.
It integrates with our modular orchestrator system and provides proper
error handling for missing dependencies.
"""

import logging
import os
import sys
from typing import Any

from . import create_agent
from .core.utils.logging_config import setup_logging


# Configure logging for ADK web mode BEFORE creating the agent
def _configure_adk_web_logging():
    """Configure logging specifically for ADK web mode to show debug statements."""

    # Get log level from environment variables
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Configure root logger for ADK web mode
    logging.basicConfig(
        level=getattr(logging, log_level, logging.DEBUG),
        format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        stream=sys.stdout,  # Ensure output goes to stdout for web interface
        force=True  # Override any existing configuration
    )

    # Configure specific loggers
    loggers_to_configure = [
        'ai_sidekick_for_splunk',
        # Ensure ADK logs are visible regardless of package name used
        'google_adk',
        'google.adk',
        'google',
        '__main__'
    ]

    for logger_name in loggers_to_configure:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, log_level, logging.DEBUG))

        # Ensure propagation is enabled so logs reach the root logger
        logger.propagate = True

    # Set up console handler with detailed formatting for web mode
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level, logging.DEBUG))
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    console_handler.setFormatter(formatter)

    # Add handler to root logger if not already present
    root_logger = logging.getLogger()
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        root_logger.addHandler(console_handler)

    print(f"🔧 ADK Web Logging configured - Level: {log_level}")
    print("✅ Debug statements should now be visible in ADK web mode")

# Configure logging immediately when module is imported
_configure_adk_web_logging()

# Ensure file logging is also enabled to a single unified file (logs/app.log)
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"), log_to_file=True, unified_file="logs/app.log")

logger = logging.getLogger(__name__)

def _create_root_agent() -> Any:
    """
    Create the root agent using our modular system.

    Returns:
        The root agent instance from our orchestrator

    Raises:
        ImportError: If Google ADK is not available
        RuntimeError: If agent creation fails
    """
    try:
        # Log debug information to test visibility
        logger.debug("🔍 Creating root agent - this is a DEBUG message")
        logger.info("📋 Creating root agent - this is an INFO message")

        # Use our create_agent factory function
        root_agent = create_agent()

        logger.debug("🔍 Root agent created successfully - DEBUG visibility test")
        logger.info("✅ Root agent created successfully using modular orchestrator")
        return root_agent
    except ImportError as e:
        logger.error(f"❌ Google ADK not available: {e}")
        raise ImportError(
            "Google ADK is required to run the Splunk AI Sidekick. "
            "Please install it using: uv add google-adk"
        ) from e
    except Exception as e:
        logger.error(f"❌ Failed to create root agent: {e}")
        raise RuntimeError(f"Root agent creation failed: {e}") from e

# Create the root agent for ADK discovery
try:
    logger.debug("🔍 Initializing root agent for ADK discovery - DEBUG test")
    root_agent = _create_root_agent()
    logger.debug("🔍 Root agent initialization complete - DEBUG test")
    logger.info("✅ Root agent available for ADK web interface")
except Exception as e:
    logger.error(f"❌ Failed to initialize root agent: {e}")
    # Set to None so ADK can handle the error gracefully
    root_agent = None

# Export for ADK discovery
__all__ = ["root_agent"]
