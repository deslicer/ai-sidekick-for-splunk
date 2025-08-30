"""
AI Sidekick for Splunk Orchestrator - Main coordination system.

This module provides the SplunkOrchestrator class that coordinates between
agents, tools, and external systems using our modular architecture.
"""

import logging
import os
import sys
from typing import Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from .config import Config
from .discovery import ComponentDiscovery
from .registry import RegistryManager

# Import Google ADK components

logger = logging.getLogger(__name__)

class SplunkOrchestrator:
    """
    Main orchestrator for the AI Sidekick for Splunk system.

    Coordinates between agents, tools, and external systems using our
    modular architecture with dynamic discovery and registration.
    """

    def __init__(self, config: Config | None = None) -> None:
        """
        Initialize the orchestrator with configuration and registries.

        Args:
            config: Configuration object, uses default if None
        """
        self.config = config or Config()

        # Logging is configured at the application entry point (e.g., agent.py) per ADK docs.
        # Avoid duplicate logging configuration here.
        self.registry_manager = RegistryManager(self.config)
        self.discovery = ComponentDiscovery(self.registry_manager, self.config)
        self._adk_agent: Any | None = None

        # Perform discovery on initialization
        self._discover_components()

        # Create ADK agent after discovery to ensure all tools are available
        try:
            self.create_adk_agent()
            logger.info("SplunkOrchestrator initialized with ADK agent")
        except Exception as e:
            logger.warning(f"SplunkOrchestrator initialized but ADK agent creation failed: {e}")
            logger.info("SplunkOrchestrator initialized")

    def _discover_components(self) -> None:
        """Discover components using the enhanced discovery system."""

        # Define discovery paths avoiding 'src.' namespace collision
        # Import directly from the module hierarchy
        agent_paths = [
            "ai_sidekick_for_splunk.contrib.agents",
            "ai_sidekick_for_splunk.core.agents"  # Includes all core agents (flow_pilot, index_analysis_flow, etc.)
        ]
        tool_paths = [
            "ai_sidekick_for_splunk.contrib.tools",
            "ai_sidekick_for_splunk.core.tools"
        ]

        # Use enhanced discovery with tool-to-agent mapping
        discovery_result = self.discovery.discover_all(agent_paths, tool_paths)

        logger.info(f"Discovery complete: {discovery_result['agents']} agents, {discovery_result['tools']} tools")

    def create_adk_agent(self) -> Any:
        """Create the main ADK agent that can route to sub-agents.

        Returns:
            ADK LlmAgent configured for the AI Sidekick for Splunk
        """
        if self._adk_agent is not None:
            return self._adk_agent

        try:
            # Get agent tools for seamless delegation workflow
            agent_tools = self._get_adk_agent_tools()
            logger.debug(f"Total agent tools: {len(agent_tools)}")
            logger.debug(f"Agent tools: {agent_tools}")

            root_tools = self._get_adk_tools()

            # Combine standalone tools with agent tools
            all_tools = root_tools + agent_tools

            logger.debug(f"Total tools for root agent: {len(root_tools)} root tools + {len(agent_tools)} agent tools = {len(all_tools)} total")
            logger.debug(f"All tools: {all_tools}")

            # Create main ADK agent using LlmAgent for simpler, more reliable coordination
            # LlmAgent provides better call-return patterns
            from google.adk.agents import LlmAgent
            self._adk_agent = LlmAgent(
                model=self.config.model.primary_model,  # Use Gemini 2.0 model for Google Search compatibility
                name="ai_sidekick_for_splunk",
                description="AI Sidekick for Splunk orchestrator with specialized agent tools for collaborative workflows",
                instruction=self._get_main_agent_instructions(),
                tools=all_tools
            )

            logger.info(f"Created main ADK agent with {len(all_tools)} tools ({len(root_tools)} standalone + {len(agent_tools)} agent tools)")
            return self._adk_agent

        except ImportError:
            logger.error("Google ADK not available - cannot create LlmAgent")
            raise RuntimeError("Google ADK is required for agent creation")
        except Exception as e:
            logger.error(f"Failed to create main ADK agent: {e}")
            raise

    def _get_adk_tools(self) -> list[Any]:
        """Get ADK-compatible tools for the ROOT agent only.

        Note: Following ADK patterns, built-in tools like Google Search can only be in root agents.
        The framework handles automatic delegation to sub-agents without explicit transfer tools.

        Returns:
            List of ADK-compatible tools for the root agent
        """
        root_tools = []

        # Get standalone tools that are not associated with any specific agent
        agent_tool_mapping = self.discovery.get_agent_tool_mapping()
        all_tool_entries = self.registry_manager.tool_registry.list_all()

        for tool_name, entry in all_tool_entries.items():
            # Skip google_search tool as it's already added via grounding tool
            if tool_name == "google_search":
                logger.debug("Skipping google_search tool - already added via grounding tool")
                continue

            # Only include tools that are NOT associated with any sub-agent
            if not agent_tool_mapping.get_tool_agent(tool_name):
                try:
                    # Create tool instance
                    tool_instance = entry.cls(self.config, entry.metadata)

                    # Check if it's an ADK tool wrapper with get_adk_tool method
                    if hasattr(tool_instance, 'get_adk_tool'):
                        adk_tool = tool_instance.get_adk_tool()
                        if adk_tool:
                            root_tools.append(adk_tool)
                            logger.debug(f"Added root tool: {tool_name}")
                except Exception as e:
                    logger.error(f"Error creating root tool instance {tool_name}: {e}")

        return root_tools

    def _get_adk_agent_tools(self) -> list[Any]:
        """Get discovered agents wrapped as AgentTools for seamless delegation.

        This enables the call/return pattern instead of handoff, allowing the orchestrator
        to maintain control of multi-turn workflows between specialist agents.

        Returns:
            List of AgentTool instances wrapping discovered agents
        """
        from google.adk.tools import AgentTool

        agent_tools = []
        agent_tool_mapping = self.discovery.get_agent_tool_mapping()

        # Get all registered agents from our registry
        agent_entries = self.registry_manager.agent_registry.list_all()

        for name, entry in agent_entries.items():
            try:
                # Use existing instance if available, otherwise create new one
                if entry.instance:
                    agent_instance = entry.instance
                    logger.debug(f"Using existing instance for {name}")
                else:
                    agent_instance = entry.cls(self.config, entry.metadata)
                    logger.debug(f"Created new instance for {name}")

                # Check if it's an ADK agent wrapper
                if hasattr(agent_instance, 'get_adk_agent'):
                    # Get associated tools for this agent
                    agent_tool_names = agent_tool_mapping.get_agent_tools(name)
                    agent_instance_tools = self._get_tools_for_sub_agent(agent_tool_names)

                # CRITICAL: Set orchestrator on agent before creating ADK agent
                # This allows agents to access other agents through the orchestrator
                if hasattr(agent_instance, 'set_orchestrator'):
                    agent_instance.set_orchestrator(self)
                    logger.debug(f"✅ Set orchestrator on agent: {name}")
                elif hasattr(agent_instance, 'orchestrator'):
                    agent_instance.orchestrator = self
                    logger.debug(f"✅ Set orchestrator property on agent: {name}")

                # CRITICAL: Update the registry entry to use this orchestrator-injected instance
                # This ensures that get_instance() returns the same instance with orchestrator
                try:
                    registry_entry = self.registry_manager.agent_registry._entries.get(name)
                    if registry_entry:
                        registry_entry.instance = agent_instance
                        logger.debug(f"✅ Updated registry with orchestrator-injected agent: {name}")
                except Exception as e:
                    logger.warning(f"Could not update registry entry for {name}: {e}")

                # Create ADK agent (sub-agents use LlmAgent, not Agent class)
                adk_agent = agent_instance.get_adk_agent(tools=agent_instance_tools)

                if adk_agent:
                    # Wrap agent as AgentTool for seamless delegation
                    agent_tool = AgentTool(
                        agent=adk_agent,
                        skip_summarization=False
                    )
                    agent_tools.append(agent_tool)
                    logger.debug(f"Created AgentTool: {name}_agent with {len(agent_instance_tools)} tools")
                else:
                    logger.debug(f"Agent {name} is not ADK-compatible - skipping AgentTool creation")

            except Exception as e:
                logger.error(f"Error creating AgentTool for {name}: {e}")

        return agent_tools

    def _get_adk_sub_agents(self) -> list[Any]:
        """Get all discovered agents as sub-agents for the root agent with their associated tools.

        Returns:
            List of ADK-compatible sub-agents with their tools
        """
        sub_agents = []
        agent_tool_mapping = self.discovery.get_agent_tool_mapping()

        # Get all registered agents from our registry
        agent_entries = self.registry_manager.agent_registry.list_all()

        for name, entry in agent_entries.items():
            try:
                # Create agent instance
                agent_instance = entry.cls(self.config, entry.metadata)

                # Check if it's an ADK agent wrapper
                if hasattr(agent_instance, 'get_adk_agent'):
                    # Get associated tools for this agent
                    agent_tool_names = agent_tool_mapping.get_agent_tools(name)
                    agent_tools = self._get_tools_for_sub_agent(agent_tool_names)

                    # Create ADK agent (sub-agents use LlmAgent, not Agent class)
                    adk_agent = agent_instance.get_adk_agent(tools=agent_tools)

                    if adk_agent:
                        sub_agents.append(adk_agent)
                        logger.debug(f"Added sub-agent: {name} with {len(agent_tools)} tools")
                else:
                    logger.debug(f"Agent {name} is not ADK-compatible - skipping sub-agent registration")

            except Exception as e:
                logger.error(f"Error creating sub-agent instance {name}: {e}")

        return sub_agents

    def _get_tools_for_sub_agent(self, tool_names: list[str]) -> list[Any]:
        """Get ADK-compatible tools for a specific sub-agent.

        Args:
            tool_names: List of tool names associated with the agent

        Returns:
            List of ADK-compatible tools
        """
        tools = []

        for tool_name in tool_names:
            try:
                tool_entry = self.registry_manager.tool_registry.get(tool_name)
                if tool_entry:
                    # Create tool instance
                    tool_instance = tool_entry.cls(self.config, tool_entry.metadata)

                    # Check if it's an ADK tool wrapper
                    if hasattr(tool_instance, 'get_adk_tool'):
                        adk_tool = tool_instance.get_adk_tool()
                        if adk_tool:
                            tools.append(adk_tool)
                            logger.debug(f"Added tool {tool_name} to sub-agent")
            except Exception as e:
                logger.error(f"Error creating tool instance {tool_name}: {e}")

        return tools

    def _get_main_agent_instructions(self) -> str:
        """Get instructions for the main ADK agent.

        Returns:
            Instructions string for the root agent
        """
        from .orchestrator_prompt_lab import (
            ORCHESTRATOR_INSTRUCTIONS_LAB as ORCHESTRATOR_INSTRUCTIONS,
        )
        return ORCHESTRATOR_INSTRUCTIONS

    def _get_main_agent_instructions_no_tools(self) -> str:
        """Get instructions for the main orchestrating agent when tools are disabled.

        Returns:
            Instruction string for the main agent without tool references
        """
        from .orchestrator_prompt_lab import (
            ORCHESTRATOR_INSTRUCTIONS_LAB as ORCHESTRATOR_INSTRUCTIONS_NO_TOOLS,
        )
        return ORCHESTRATOR_INSTRUCTIONS_NO_TOOLS

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of the orchestrator state.

        Returns:
            Dictionary containing orchestrator information
        """
        # Get registry data
        agent_entries = self.registry_manager.agent_registry.list_all()
        tool_entries = self.registry_manager.tool_registry.list_all()

        # Get agent-tool mapping
        agent_tool_mapping = self.discovery.get_agent_tool_mapping()

        return {
            "agent_count": len(agent_entries),
            "tool_count": len(tool_entries),
            "agents": {name: {"description": entry.metadata.description}
                      for name, entry in agent_entries.items()},
            "tools": {name: {"description": entry.metadata.description}
                     for name, entry in tool_entries.items()},
            "agent_tool_mapping": agent_tool_mapping.get_all_agent_tool_mappings(),
            "config": {
                "model": self.config.model.primary_model,
                "use_vertex_ai": self.config.model.use_vertex_ai
            },
            "adk_agent_created": self._adk_agent is not None
        }


def create_agent(config: Config | None = None) -> Any:
    """Factory function to create the main AI Sidekick for Splunk agent.

    Args:
        config: Optional configuration instance

    Returns:
        ADK LlmAgent instance
    """
    orchestrator = SplunkOrchestrator(config)
    return orchestrator.create_adk_agent()


def create_orchestrator(config: Config | None = None) -> SplunkOrchestrator:
    """Factory function to create the orchestrator.

    Args:
        config: Optional configuration instance

    Returns:
        SplunkOrchestrator instance
    """
    return SplunkOrchestrator(config)
