"""
Structured Data Explorer Agent with Consistent Workflow.

Implements a systematic 5-phase approach for reliable business intelligence
generation with real data integration and consistent output formatting.
"""

import logging

from google.adk.agents import LlmAgent

from ai_sidekick_for_splunk.core.base_agent import AgentMetadata

logger = logging.getLogger(__name__)


class StructuredDataExplorerAgent(LlmAgent):
    """
    Structured Data Explorer Agent for systematic Splunk data analysis.

    Implements a mandatory 5-phase workflow that ensures consistent,
    actionable insights based on real Splunk data with structured output templates.

    Phases:
    1. Index Discovery & Baseline Analysis
    2. Data Composition Analysis
    3. Temporal Patterns & Usage Analysis
    4. Data Quality & Structure Assessment
    5. Business Intelligence Generation

    Each phase has specific SPL queries, output templates, and quality requirements
    to ensure consistent user experience and actionable results.
    """

    def __init__(self) -> None:
        """
        Initialize the structured Data Explorer agent.

        Sets up the agent with structured workflow instructions that enforce
        consistent execution patterns and real data integration.
        """
        from .structured_prompt import DATA_EXPLORER_INSTRUCTIONS

        super().__init__(
            name="DataExplorer",
            model="gemini-2.0-flash",
            instruction=DATA_EXPLORER_INSTRUCTIONS,
            description="Systematic Splunk data exploration with structured 5-phase workflow and consistent business intelligence output",
        )


# Class metadata for discovery system
METADATA = AgentMetadata(
    name="DataExplorer",
    description="Structured Splunk data exploration with consistent 5-phase workflow for reliable business intelligence",
    version="3.0.0",
    author="Saikrishna Gundeti",
    tags=["data-exploration", "business-intelligence", "structured-workflow", "splunk-analysis"],
    dependencies=["SplunkMCP"],
)


def create_data_explorer_agent() -> StructuredDataExplorerAgent:
    """
    Create and return a configured structured Data Explorer agent.

    Returns:
        StructuredDataExplorerAgent: Configured agent instance with systematic workflow
    """
    return StructuredDataExplorerAgent()


# Agent instance for auto-discovery
data_explorer_agent = create_data_explorer_agent()
