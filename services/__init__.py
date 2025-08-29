"""
Services for Splunk AI Sidekick.

This package contains services for managing sessions, execution,
and other infrastructure concerns for the Splunk AI Sidekick agent.
"""

from .setup_runner import SetupRunner

__all__ = [
    "SetupRunner"
]
