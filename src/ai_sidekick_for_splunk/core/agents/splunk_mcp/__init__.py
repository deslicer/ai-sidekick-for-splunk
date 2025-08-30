"""
Splunk MCP Agent - Core agent for Splunk Model Context Protocol integration.

This agent provides real-time access to Splunk through MCP toolset,
allowing direct interaction with Splunk searches, configurations, and administration.
"""

from .agent import SplunkMCPAgent

__version__ = "1.0.0"
__all__ = ["SplunkMCPAgent"]
