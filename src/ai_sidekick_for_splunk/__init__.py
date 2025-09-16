"""
AI Sidekick for Splunk - Modular Multi-Agent System

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

__version__ = "0.3.0"
__author__ = "AI Sidekick for Splunk Team"

# Core exports for framework consumers
from .core.base_agent import AgentMetadata, BaseAgent
from .core.base_tool import BaseTool, ToolMetadata
from .core.config import Config
from .core.discovery import ComponentDiscovery
from .core.orchestrator import SplunkOrchestrator, create_agent, create_orchestrator
from .core.registry import AgentRegistry, RegistryManager, ToolRegistry

# Import services with graceful fallback for optional dependencies
_services_available = True
try:
    from .services import SetupRunner
except ImportError:
    # SetupRunner requires Google ADK - provide a placeholder
    _services_available = False

    class SetupRunner:
        """Placeholder for SetupRunner when Google ADK is not available."""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "SetupRunner requires Google ADK. Install with: pip install google-adk"
            )


from .core.agents.flow_pilot.agent import create_flow_pilot
from .core.agents.search_guru.agent import create_search_guru_agent
from .core.agents.index_analysis_flow.agent import create_index_analysis_flow_agent

# Build __all__ dynamically based on available imports
_base_exports = [
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
    # Agent factory functions
    "create_flow_pilot",
    "create_search_guru_agent",
    "create_index_analysis_flow_agent",
]

__all__ = _base_exports + (["SetupRunner"] if _services_available else [])
