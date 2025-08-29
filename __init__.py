"""
Splunk AI Sidekick - Modular Multi-Agent System

A contribution-driven, modular architecture for Splunk AI agents using Google ADK.
This package provides a core framework for building extensible Splunk AI capabilities
with dynamic discovery of community-contributed agents and tools.

Key Features:
- Dynamic agent and tool discovery
- Contribution-driven development model
- Clear separation between core framework and community extensions
- Google ADK-based multi-agent orchestration
- Developer-first experience with scripted workflows
"""

__version__ = "0.1.0"
__author__ = "Splunk AI Sidekick Team"

# Core exports for framework consumers
from .core.base_agent import AgentMetadata, BaseAgent
from .core.base_tool import BaseTool, ToolMetadata
from .core.config import Config
from .core.discovery import ComponentDiscovery
from .core.orchestrator import SplunkOrchestrator, create_agent
from .core.registry import AgentRegistry, RegistryManager, ToolRegistry
from .services import SetupRunner

__all__ = [
    "SplunkOrchestrator",
    "BaseAgent",
    "AgentMetadata",
    "BaseTool",
    "ToolMetadata",
    "Config",
    "AgentRegistry",
    "ToolRegistry",
    "RegistryManager",
    "ComponentDiscovery",
    "SetupRunner",
    "create_agent",
]
