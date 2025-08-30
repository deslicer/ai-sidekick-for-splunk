"""
Services for AI Sidekick for Splunk.

This package contains services for managing sessions, execution,
and other infrastructure concerns for the AI Sidekick for Splunk agent.
"""

from .setup_runner import SetupRunner

__all__ = [
    "SetupRunner"
]
