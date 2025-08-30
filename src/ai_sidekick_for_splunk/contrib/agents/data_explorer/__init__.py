"""
Data Explorer Agent Module

This module provides the DataExplorer agent for comprehensive Splunk data discovery and analysis.
Features a simple 5-step workflow with real-time SplunkMCP integration.
"""

# MAIN: Working DataExplorer agent with proper tool integration
from .agent import DataExplorerAgent, create_data_explorer_agent, data_explorer_agent

__all__ = [
    # MAIN: DataExplorer Agent with Tool Integration
    "DataExplorerAgent",  # DataExplorerAgent with get_adk_agent support
    "create_data_explorer_agent",  # Factory function
    "data_explorer_agent",  # Instance for auto-discovery
]
