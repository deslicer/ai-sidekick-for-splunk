"""
Simplified Data Explorer Agent - Single LlmAgent Implementation.

This replaces the complex LoopAgent workflow with a straightforward LlmAgent
that handles the complete data exploration through systematic delegation.
"""

import logging
from typing import Any

from google.adk.agents import LlmAgent

from ai_sidekick_for_splunk.core.base_agent import AgentMetadata, BaseAgent
from ai_sidekick_for_splunk.core.config import Config

logger = logging.getLogger(__name__)


class DataExplorerAgent(BaseAgent):
    """
    Simplified Data Explorer Agent for comprehensive Splunk data analysis.

    Uses a single LlmAgent with systematic delegation to SplunkMCP for real data collection,
    then generates business insights based on actual search results.
    """

    # Class metadata for discovery system
    METADATA = AgentMetadata(
        name="DataExplorer",
        description="Systematic Splunk data exploration and business insight generation",
        version="2.0.0",
        author="Saikrishna Gundeti",
        tags=["data-exploration", "business-intelligence", "splunk-analysis"],
        dependencies=["SplunkMCP"],
    )

    name = "DataExplorer"
    description = (
        "Systematic Splunk data exploration and business insight generation using real data"
    )

    @property
    def instructions(self) -> str:
        """Get the agent instructions/prompt."""
        from .prompt import DATA_EXPLORER_INSTRUCTIONS

        return DATA_EXPLORER_INSTRUCTIONS

    def __init__(
        self,
        config: Config | None = None,
        metadata: AgentMetadata | None = None,
        tools: list[Any] | None = None,
    ) -> None:
        """Initialize the simplified Data Explorer agent."""
        logger.info(
            "🔧 Initializing DataExplorer agent",
            extra={
                "event_type": "dataexplorer_initialization",
                "event_data": {"agent_name": "DataExplorer", "version": "simple_agent"},
            },
        )

        super().__init__(config or Config(), metadata or self.METADATA, tools or [])

        logger.info(
            "✅ DataExplorer agent initialized successfully",
            extra={
                "event_type": "dataexplorer_created",
                "event_data": {
                    "agent_name": self.name,
                    "instruction_length": len(self.instructions),
                    "description": self.description,
                    "tools_count": len(tools or []),
                },
            },
        )

    def get_adk_agent(self, tools: list[Any] | None = None) -> LlmAgent | None:
        """
        Create ADK LlmAgent for data exploration operations.

        Args:
            tools: List of tools to provide to the agent (should include SplunkMCP_agent access)

        Returns:
            Configured LlmAgent instance
        """
        try:
            logger.info(
                "🔧 Creating DataExplorer LlmAgent",
                extra={
                    "event_type": "dataexplorer_adk_creation",
                    "event_data": {
                        "agent_name": self.name,
                        "tools_provided": len(tools or []),
                        "model": self.config.model.primary_model,
                    },
                },
            )

            agent = LlmAgent(
                name=self.name,
                model="gemini-1.5-pro-latest",
                instruction=self.instructions,
                description=self.description,
                tools=tools or [],
            )

            logger.info(
                "✅ DataExplorer LlmAgent created successfully",
                extra={
                    "event_type": "dataexplorer_adk_created",
                    "event_data": {
                        "agent_name": self.name,
                        "model": agent.model,
                        "tools_count": len(agent.tools or []),
                        "instruction_length": len(agent.instruction),
                    },
                },
            )
            return agent

        except Exception as e:
            logger.error(
                "❌ Failed to create DataExplorer LlmAgent",
                extra={
                    "event_type": "dataexplorer_adk_creation_failed",
                    "event_data": {
                        "agent_name": self.name,
                        "error": str(e),
                        "tools_provided": len(tools or []),
                    },
                },
            )
            return None


# Factory function for easy instantiation
def create_data_explorer_agent() -> DataExplorerAgent:
    """
    Create and return a configured Data Explorer agent.

    Returns:
        DataExplorerAgent: Configured agent instance
    """
    return DataExplorerAgent()


# Agent instance for auto-discovery - TEMPORARILY DISABLED FOR AGENT FLOW TESTING
# data_explorer_agent = create_data_explorer_agent()
