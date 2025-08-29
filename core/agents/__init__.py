"""
Core Agents - Reusable System Agents.

This module contains core system agents that provide reusable functionality
across the entire Splunk AI Sidekick system, including workflow execution agents.
"""

from .flow_pilot import FlowPilot, create_dynamic_flowpilot_agents, get_all_dynamic_agents
from .index_analysis_flow import IndexAnalysisFlowAgent
from .result_synthesizer import ResultSynthesizerAgent
from .splunk_mcp import SplunkMCPAgent

# Agent instances for auto-discovery
result_synthesizer_agent = ResultSynthesizerAgent()
splunk_mcp_agent = SplunkMCPAgent()

# Specialized agents (not replaced by dynamic system)
index_analysis_flow_agent = IndexAnalysisFlowAgent()

# Dynamic FlowPilot agents from discovered workflows
# Note: These will be created dynamically during module import
_dynamic_agents = {}

# Initialize dynamic agents immediately during module import
# This ensures they're available for discovery by the orchestrator
try:
    _dynamic_agents = create_dynamic_flowpilot_agents()

    # Collect dynamic agent attribute names for __all__
    _dynamic_attr_names = []

    # Add dynamic agents as module attributes so they can be discovered
    for agent_name, agent_instance in _dynamic_agents.items():
        # Create a valid Python identifier from the agent name
        attr_name = f"dynamic_{agent_name.lower().replace(' ', '_').replace('-', '_')}"
        globals()[attr_name] = agent_instance
        _dynamic_attr_names.append(attr_name)

    print(f"✅ Initialized {len(_dynamic_agents)} dynamic FlowPilot agents during module import")
    print(f"   Dynamic agent attributes: {_dynamic_attr_names}")

except Exception as e:
    print(f"⚠️ Failed to initialize dynamic agents during import: {e}")
    _dynamic_attr_names = []
    # Don't fail the entire module import, just log the error


def initialize_dynamic_agents(orchestrator=None):
    """
    Initialize dynamic FlowPilot agents from discovered workflows.

    This function should be called by the orchestrator during initialization
    to ensure all discovered workflows are available as agents.

    Args:
        orchestrator: The orchestrator instance to inject into agents
    """
    global _dynamic_agents
    try:
        _dynamic_agents = create_dynamic_flowpilot_agents(orchestrator)
        print(f"✅ Initialized {len(_dynamic_agents)} dynamic FlowPilot agents")
        return _dynamic_agents
    except Exception as e:
        print(f"❌ Failed to initialize dynamic agents: {e}")
        return {}


def get_all_agents():
    """
    Get all agents including static and dynamic ones.

    Returns:
        Dictionary of all available agents
    """
    agents = {
        "result_synthesizer_agent": result_synthesizer_agent,
        "splunk_mcp_agent": splunk_mcp_agent,
        "index_analysis_flow_agent": index_analysis_flow_agent,
    }

    # Add dynamic FlowPilot agents (automatically discovered workflows)
    agents.update(_dynamic_agents)

    return agents

# Base __all__ list
__all__ = [
    "ResultSynthesizerAgent", "result_synthesizer_agent",
    "SplunkMCPAgent", "splunk_mcp_agent",
    "FlowPilot",
    "IndexAnalysisFlowAgent", "index_analysis_flow_agent",
    "initialize_dynamic_agents", "get_all_agents", "create_dynamic_flowpilot_agents", "get_all_dynamic_agents"
]

# Add dynamic agent names to __all__ after they're created
if '_dynamic_attr_names' in globals():
    __all__.extend(_dynamic_attr_names)
