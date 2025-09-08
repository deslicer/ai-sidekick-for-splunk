"""
Search Guru - A community-contributed agent for Splunk search assistance.

This agent specializes in helping users construct, execute, and analyze
Splunk searches. It provides expert guidance on SPL (Search Processing Language)
and can help optimize search performance.
"""

from .agent import SearchGuru, create_search_guru_agent, search_guru_agent

__version__ = "1.0.0"
__all__ = ["SearchGuru", "create_search_guru_agent", "search_guru_agent"]
