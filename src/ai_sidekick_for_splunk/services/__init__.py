"""
Services for AI Sidekick for Splunk.

This package contains services for managing sessions, execution,
and other infrastructure concerns for the AI Sidekick for Splunk agent.
"""

# Import with graceful fallback for optional dependencies
try:
    from .setup_runner import SetupRunner  # noqa: F401
    __all__ = ["SetupRunner"]
except ImportError:
    # Google ADK not available - services not available
    __all__ = []
