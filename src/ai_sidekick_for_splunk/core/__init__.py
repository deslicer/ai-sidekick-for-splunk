"""
Core framework components for AI Sidekick for Splunk.

This module contains the foundational classes and utilities for building
modular, extensible Splunk AI agents using Google ADK.
"""

from .base_agent import AgentMetadata, BaseAgent
from .base_tool import BaseTool, ToolMetadata
from .config import Config
from .discovery import ComponentDiscovery
from .orchestrator import SplunkOrchestrator, create_agent, create_orchestrator
from .registry import AgentRegistry, RegistryManager, ToolRegistry

__all__ = [
    "SplunkOrchestrator",
    "create_orchestrator",
    "create_agent",
    "BaseAgent",
    "AgentMetadata",
    "BaseTool",
    "ToolMetadata",
    "Config",
    "AgentRegistry",
    "ToolRegistry",
    "RegistryManager",
    "ComponentDiscovery",
]
