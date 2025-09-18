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

__version__ = "0.4.0"
__author__ = "AI Sidekick for Splunk Team"

# Core exports for framework consumers
from .core.base_agent import AgentMetadata, BaseAgent  # noqa: F401
from .core.base_tool import BaseTool, ToolMetadata  # noqa: F401
from .core.config import Config  # noqa: F401
from .core.discovery import ComponentDiscovery  # noqa: F401
from .core.orchestrator import (
    SplunkOrchestrator,  # noqa: F401
    create_agent,  # noqa: F401
    create_orchestrator,  # noqa: F401
)
from .core.registry import AgentRegistry, RegistryManager, ToolRegistry  # noqa: F401

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


from .core.agents.flow_pilot.agent import create_flow_pilot  # noqa: F401
from .core.agents.index_analysis_flow.agent import (
    create_index_analysis_flow_agent,  # noqa: F401
)
from .core.agents.search_guru.agent import create_search_guru_agent  # noqa: F401

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
