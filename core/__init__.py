"""
Core framework components for AI Sidekick for Splunk.

This module contains the foundational classes and utilities for building
modular, extensible Splunk AI agents using Google ADK.
"""

from .base_agent import BaseAgent
from .base_tool import BaseTool
from .config import Config
from .discovery import ComponentDiscovery
from .orchestrator import SplunkOrchestrator
from .registry import AgentRegistry, ToolRegistry

__all__ = [
    "SplunkOrchestrator",
    "BaseAgent",
    "BaseTool",
    "Config",
    "AgentRegistry",
    "ToolRegistry",
    "ComponentDiscovery",
]
