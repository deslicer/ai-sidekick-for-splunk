"""
Researcher agent for AI Sidekick for Splunk.

A specialized core agent for research operations using Google Search grounding
to access real-time information from the internet.
"""

import logging
from typing import Any

from google.adk.agents import Agent

from ai_sidekick_for_splunk.core.base_agent import AgentMetadata, BaseAgent

from .prompt import RESEARCHER_PROMPT
from .tools.search import google_search_grounding

logger = logging.getLogger(__name__)


class ResearcherAgent(BaseAgent):
    """
    Researcher agent for complex analysis and investigation of Splunk-related topics.
    Focuses on deep analysis, pattern recognition, and providing comprehensive insights.
    The root agent handles current information gathering via Google Search.
    """

    # Class metadata for discovery system
    METADATA = AgentMetadata(
        name="researcher",
        description="Research agent with Google Search grounding for real-time information gathering",
        version="1.0.0",
        author="Core",
        tags=["research", "google-search", "internet", "information"],
        dependencies=[],
    )

    name = "researcher"
    description = "Performs complex analysis, investigation, and provides comprehensive insights on Splunk topics, configurations, and troubleshooting scenarios"

    def __init__(
        self,
        config: Any | None = None,
        metadata: AgentMetadata | None = None,
        tools: list[Any] | None = None,
        session_state: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the Researcher Agent.

        Args:
            config: Configuration object for the agent
            metadata: Metadata for agent registration
            tools: List of tools available to the agent
            session_state: Session state for the agent
        """
        from ai_sidekick_for_splunk.core.config import Config

        # Use default config if none provided
        if config is None:
            config = Config()

        # Create metadata if not provided
        if metadata is None:
            metadata = AgentMetadata(
                name="researcher",
                description="Research agent with Google Search grounding for real-time information gathering",
                version="1.0.0",
                author="Core",
                tags=["research", "google-search", "internet", "information"],
                dependencies=[],
            )

        super().__init__(config, metadata, tools, session_state)

    def get_metadata(self) -> AgentMetadata:
        """
        Get agent metadata for registration.

        Returns:
            AgentMetadata: The agent's metadata
        """
        return self.metadata

    @property
    def instructions(self) -> str:
        """
        Get the agent instructions/prompt.

        Returns:
            str: The agent's system instructions
        """
        from .prompt import RESEARCHER_PROMPT

        return RESEARCHER_PROMPT

    def get_adk_agent(self, tools: list[Any] | None = None) -> Agent:
        """
        Create ADK Agent for researcher.
        Focuses on analysis capabilities without built-in tools.

        Args:
            tools: Optional list of tools (typically empty for sub-agents)

        Returns:
            ADK LlmAgent configured for research and analysis
        """

        agent = Agent(
            model=self.config.model.primary_model,
            name=self.name,
            description=self.description,
            instruction=RESEARCHER_PROMPT,
            tools=[google_search_grounding],
        )

        logger.debug("Created researcher ADK agent with google search grounding tool")
        return agent

    def _get_instructions(self) -> str:
        """Get detailed instructions for the researcher agent."""
        return """You are the Researcher Agent, a specialized sub-agent of the AI Sidekick for Splunk focused on
deep analysis, investigation, and comprehensive insights for Splunk-related topics.

## Your Expertise Areas

### Complex Analysis:
- Splunk architecture design and optimization
- Advanced troubleshooting methodologies
- Performance analysis and capacity planning
- Security incident investigation workflows
- Data model design and knowledge object optimization

### Investigation Capabilities:
- Root cause analysis for Splunk issues
- Log pattern analysis and anomaly detection
- Search performance investigation
- Index and storage optimization analysis
- Cluster health and distributed deployment analysis

### Knowledge Synthesis:
- Comprehensive reporting on complex topics
- Multi-faceted problem solving approaches
- Integration planning and strategy development
- Compliance and governance framework analysis
- Technical documentation and procedure development

## Your Role

You handle tasks that require:
- Deep technical analysis and reasoning
- Complex multi-step investigation processes
- Synthesis of information from multiple sources
- Comprehensive troubleshooting methodologies
- Strategic planning and architectural guidance

## Response Approach

1. **Thorough Analysis**: Break down complex problems into manageable components
2. **Systematic Investigation**: Follow logical troubleshooting sequences
3. **Comprehensive Insights**: Provide detailed explanations with context
4. **Actionable Recommendations**: Offer practical, implementable solutions
5. **Knowledge Integration**: Connect related concepts and dependencies

## Key Principles

- Focus on analysis and reasoning rather than information gathering
- Provide comprehensive, well-structured responses
- Consider multiple perspectives and potential solutions
- Explain the "why" behind recommendations
- Account for enterprise-scale considerations and constraints

Note: For current information or recent developments, the root agent will handle information
gathering via its direct access to current sources. Your role is to analyze and provide
insights based on provided information and your expertise.
"""

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute a research task.

        Args:
            task: The research task description
            context: Optional context for the task

        Returns:
            Dict[str, Any]: Dictionary containing the research result
        """
        try:
            logger.info(f"ResearcherAgent executing task: {task}")

            # Basic task routing based on research type
            if any(
                keyword in task.lower()
                for keyword in ["cve", "vulnerability", "security", "advisory"]
            ):
                return await self._handle_security_research(task, context)
            elif any(keyword in task.lower() for keyword in ["splunk", "spl", "search"]):
                return await self._handle_splunk_research(task, context)
            elif any(
                keyword in task.lower() for keyword in ["conf", "event", "training", "webinar"]
            ):
                return await self._handle_event_research(task, context)
            else:
                return await self._handle_general_research(task, context)

        except Exception as e:
            logger.error(f"ResearcherAgent execution failed: {e}")
            return {"success": False, "error": str(e), "message": "Failed to execute research task"}

    async def _handle_security_research(
        self, task: str, context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Handle security-related research tasks."""
        return {
            "success": True,
            "task_type": "security_research",
            "research_areas": [
                "Latest CVE alerts for Splunk products",
                "Security advisories and patches",
                "Threat intelligence updates",
                "Security best practices",
            ],
            "message": "Security research capabilities available - use Google Search for current threats",
        }

    async def _handle_splunk_research(
        self, task: str, context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Handle Splunk-specific research tasks."""
        return {
            "success": True,
            "task_type": "splunk_research",
            "research_areas": [
                "Latest Splunk documentation updates",
                "Community best practices",
                "Performance optimization guides",
                "New feature announcements",
            ],
            "message": "Splunk research capabilities available - use Google Search for current information",
        }

    async def _handle_event_research(
        self, task: str, context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Handle event and training research tasks."""
        return {
            "success": True,
            "task_type": "event_research",
            "research_areas": [
                "Splunk .conf conference information",
                "Training and certification updates",
                "Webinars and virtual events",
                "Community meetups",
            ],
            "message": "Event research capabilities available - use Google Search for current schedules",
        }

    async def _handle_general_research(
        self, task: str, context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Handle general research tasks."""
        return {
            "success": True,
            "task_type": "general_research",
            "capabilities": [
                "Real-time web research",
                "Technology trend analysis",
                "Best practices research",
                "Documentation updates",
            ],
            "message": "General research capabilities available - use Google Search for current information",
        }

    def get_capabilities(self) -> list[str]:
        """
        Get agent capabilities.

        Returns:
            List[str]: List of agent capabilities
        """
        return [
            "web_research",
            "google_search",
            "security_research",
            "splunk_research",
            "event_research",
            "documentation_research",
            "real_time_information",
        ]

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """
        Validate input data for the agent.

        Args:
            input_data: Input data to validate

        Returns:
            bool: True if input is valid
        """
        # Basic validation - ensure we have a research task
        return "task" in input_data or "query" in input_data or "research" in input_data

    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        logger.info("ResearcherAgent cleanup completed")
        pass
