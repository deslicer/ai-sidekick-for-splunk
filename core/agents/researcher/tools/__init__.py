"""
Official AI Sidekick for Splunk tools.

This package contains officially maintained and supported tools that are
part of the core framework. These tools provide essential Splunk functionality
and integrations that agents can use.
"""

from .search import google_search_grounding

__version__ = "1.0.0"
__all__ = ["google_search_grounding"]
