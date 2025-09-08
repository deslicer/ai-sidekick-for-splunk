"""
Search Guru implementation for AI Sidekick for Splunk.

A specialized agent for Splunk search operations, SPL guidance, search optimization,
and comprehensive index data analysis with insights generation.
"""

import logging
import re
from collections.abc import AsyncGenerator
from typing import Any

from ai_sidekick_for_splunk.core.base_agent import AgentMetadata, BaseAgent

logger = logging.getLogger(__name__)


class SearchGuru(BaseAgent):
    """
    A comprehensive Splunk search specialist agent.

    This agent provides complete search lifecycle support including:
    - SPL Generation with documentation references
    - SPL Optimization using best practices
    - Search execution via ADK transfer to splunk_mcp
    - Result analysis and interpretation
    - Index Data Insights with automated workflow
    """

    # Class metadata for discovery system
    METADATA = AgentMetadata(
        name="search_guru",
        description="SPL Expert & Performance Consultant for search optimization and strategy",
        version="4.0.0",
        author="Saikrishna Gundeti",
        tags=["search", "spl", "optimization", "performance", ""],
        dependencies=["SplunkMCP"],
    )

    def __init__(
        self,
        config: Any | None = None,
        metadata: AgentMetadata | None = None,
        tools: list[Any] | None = None,
        session_state: dict[str, Any] | None = None,
    ):
        """Initialize the Search Guru."""
        from ai_sidekick_for_splunk.core.config import Config

        # Use default config if none provided
        if config is None:
            config = Config()

        # Create metadata if not provided
        if metadata is None:
            metadata = AgentMetadata(
                name="search_guru",
                description="Comprehensive Splunk search specialist for SPL generation, optimization, execution, and insights",
                version="3.0.0",
                author="Saikrishna Gundeti",
                tags=["search", "spl", "optimization", "insights", "analysis"],
                dependencies=["splunk_mcp"],
            )

        super().__init__(config, metadata, tools, session_state)
        self.name = "search_guru"
        self.description = "Comprehensive Splunk search specialist for SPL generation, optimization, execution, and insights"

    def get_metadata(self) -> AgentMetadata:
        """Get agent metadata for registration."""
        return self.metadata

    @property
    def instructions(self) -> str:
        """Get the comprehensive agent instructions/prompt."""
        # Import and return the updated prompt
        from .search_guru_prompt import SEARCH_GURU_INSTRUCTIONS

        return SEARCH_GURU_INSTRUCTIONS

    async def execute(
        self, task: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any] | AsyncGenerator[dict[str, Any], None]:
        """
        Execute a comprehensive search-related task using ADK native transfers.

        Args:
            task: The task description
            context: Optional context for the task

        Returns:
            Dictionary containing the result for simple tasks, or AsyncGenerator for streaming workflows
        """
        try:
            logger.info(f"SearchGuru executing task: {task}")

            # Route to specific SPL capability handlers
            task_lower = task.lower()
            if any(keyword in task_lower for keyword in ["optimize", "performance", "improve"]):
                return await self._handle_spl_optimization(task, context)
            elif any(keyword in task_lower for keyword in ["generate", "create", "build", "write"]):
                return await self._handle_spl_generation(task, context)
            elif any(keyword in task_lower for keyword in ["run", "execute", "search"]):
                return await self._handle_search_transfer(task, context)
            else:
                return await self._handle_general_task(task, context)

        except Exception as e:
            logger.error(f"SearchGuru execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to execute search task",
                "task_type": "error",
            }

    async def _handle_spl_generation(
        self, task: str, context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Handle SPL generation tasks with MCP tool references."""
        return {
            "success": True,
            "task_type": "spl_generation",
            "approach": "Use MCP tools for documentation-backed SPL generation",
            "mcp_tools_recommended": {
                "get_spl_reference": "Get official SPL command syntax and examples",
                "get_splunk_documentation": "Access current best practices and patterns",
                "get_splunk_cheat_sheet": "Quick reference for common SPL patterns",
                "list_spl_commands": "Discover available commands for specific use cases",
            },
            "transfer_suggestion": """
For complex SPL generation, transfer to @splunk_mcp:

@splunk_mcp: I need help generating SPL for [specific use case]. Please use:
- get_spl_reference for syntax validation
- get_splunk_documentation for best practices
- Return optimized SPL with explanations
""",
            "best_practices": [
                "Start with specific index and sourcetype filters",
                "Use time range filtering for performance",
                "Apply field filters early in the search pipeline",
                "Leverage statistical commands efficiently",
            ],
        }

    async def _handle_spl_optimization(
        self, task: str, context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Handle SPL optimization tasks with orchestrator coordination when needed."""

        # Check if task contains a specific SPL query that needs optimization
        if any(keyword in task.lower() for keyword in ["index=", "search", "|"]):
            # Return ORCHESTRATOR REQUEST for SPL validation and optimization
            orchestrator_request = f"""ORCHESTRATOR REQUEST:
Agent: splunk_mcp
Action: Analyze SPL query for optimization opportunities and performance validation
Context: User requested SPL optimization for: {task}
Expected_Result: Performance analysis, optimization recommendations, and validated improved SPL
Next_Step: I'll provide strategic optimization guidance and best practices based on the analysis"""

            return {
                "success": True,
                "task_type": "spl_optimization",
                "approach": "Orchestrator-coordinated performance analysis",
                "orchestrator_request": orchestrator_request,
                "message": f"🔧 Optimization analysis requested for SPL\n\n{orchestrator_request}",
            }
        else:
            # For general optimization guidance, provide strategic advice directly
            return {
                "success": True,
                "task_type": "spl_optimization",
                "approach": "Strategic optimization guidance",
                "mcp_tools_available": {
                    "get_troubleshooting_guide": "Performance optimization best practices",
                    "get_admin_guide": "Administrative optimizations and efficiency tips",
                    "list_troubleshooting_topics": "Find specific performance topics",
                    "list_admin_topics": "Access administrative guidance",
                },
                "optimization_principles": [
                    "Search-time vs index-time operations optimization",
                    "Statistical command efficiency and placement",
                    "Memory usage and resource optimization",
                    "Search acceleration and indexing strategies",
                ],
                "message": "🧠 I can provide strategic SPL optimization guidance. For specific query analysis, please provide the SPL query you'd like optimized.",
            }

    async def _handle_search_transfer(
        self, task: str, context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Handle search execution by requesting orchestrator coordination."""
        search_query = self._extract_search_query(task)

        # Return proper ORCHESTRATOR REQUEST format
        orchestrator_request = f"""ORCHESTRATOR REQUEST:
Agent: splunk_mcp
Action: Execute Splunk search and return formatted results
Context: User requested search execution: {search_query}
Expected_Result: Search results with execution status, result count, key findings, and performance metrics
Next_Step: I'll analyze the search results and provide insights and recommendations"""

        return {
            "success": True,
            "task_type": "search_execution",
            "search_query": search_query,
            "orchestrator_request": orchestrator_request,
            "approach": "Orchestrator-coordinated execution",
            "message": f"🔍 Search ready for execution: {search_query}\n\n{orchestrator_request}",
        }

    def _extract_search_query(self, task: str) -> str:
        """Extract SPL search query from task description."""
        # Simple extraction - look for patterns like "run search:" or "execute:"

        # Look for explicit search commands
        search_patterns = [
            r"(?:run|execute)\s+(?:search:?\s*)?(.+)",
            r"search:?\s*(.+)",
            r"index=\w+.*",
        ]

        for pattern in search_patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)

        # If no explicit search found, return the task as potential SPL
        return task.strip()

    async def _handle_general_task(
        self, task: str, context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Handle general search-related tasks."""
        return {
            "success": True,
            "task_type": "general",
            "message": "Comprehensive search assistance available with ADK native transfers",
            "capabilities": [
                "SPL Generation with MCP documentation support",
                "SPL Optimization with performance analysis",
                "Search Execution via @splunk_mcp transfers",
                "Result Analysis with business context",
                "Index Data Insights automated workflow",
            ],
            "mcp_integration": {
                "documentation_tools": [
                    "get_spl_reference",
                    "get_splunk_documentation",
                    "get_splunk_cheat_sheet",
                ],
                "troubleshooting_tools": ["get_troubleshooting_guide", "get_admin_guide"],
                "execution_tools": ["run_one_shot", "run_splunk_search"],
                "discovery_tools": [
                    "list_spl_commands",
                    "list_troubleshooting_topics",
                    "list_admin_topics",
                ],
            },
            "transfer_pattern": "Use @splunk_mcp for all Splunk environment operations",
        }

    def get_capabilities(self) -> list[str]:
        """Get comprehensive agent capabilities."""
        return [
            "spl_generation",
            "spl_optimization",
            "search_execution_transfer",
            "result_analysis",
            "index_data_insights",
            "performance_tuning",
            "documentation_integration",
            "adk_native_transfers",
        ]

    def get_adk_agent(self, tools: list[Any] | None = None) -> Any:
        """
        Get ADK-compatible agent for sub-agent delegation.

        This version uses ADK's native transfer mechanism instead of custom delegation.
        """
        try:
            from google.adk.agents import LlmAgent

            # Store tools in the agent instance
            if tools:
                self.tools = tools
                logger.debug(f"SearchGuru agent received {len(tools)} tools")

            # Use provided tools or empty list
            agent_tools = tools or []

            # Create ADK agent with native transfer support
            adk_agent = LlmAgent(
                model=self.config.model.primary_model,
                name=self.name,
                description=f"{self.description} - Uses ADK native transfers to splunk_mcp",
                instruction=self.instructions,
                tools=agent_tools,
            )

            logger.debug(f"Created ADK agent for {self.name} with native transfer support")
            return adk_agent

        except ImportError:
            logger.warning(f"Google ADK not available - {self.name} cannot be used as sub-agent")
            return None
        except Exception as e:
            logger.error(f"Failed to create ADK sub-agent for {self.name}: {e}")
            return None

    def supports_streaming(self, task: str) -> bool:
        """Check if the given task supports streaming responses."""
        # SearchGuru focuses on SPL optimization - no streaming needed
        return False

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data for the agent."""
        if not isinstance(input_data, dict):
            return False

        # Check for required task or query field - SearchGuru handles SPL optimization tasks
        return "task" in input_data or "query" in input_data

    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        logger.info("SearchGuru cleanup completed")
        pass


# Factory function for easy instantiation
def create_search_guru_agent() -> SearchGuru:
    """
    Create and return a configured Search Guru agent instance.

    Returns:
        SearchGuru: Configured agent ready for SPL optimization and search strategy.
    """
    return SearchGuru()


# Export the main agent for discovery system
search_guru_agent = create_search_guru_agent()
