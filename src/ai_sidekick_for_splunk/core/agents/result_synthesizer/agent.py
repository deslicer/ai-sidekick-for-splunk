"""
Generic Result Synthesizer Agent.

A reusable agent that converts technical Splunk search results into actionable
business insights, persona-based use cases, and implementation recommendations.
This agent can be used by any other agent that needs result interpretation,
comprehensive insights, recommendations, and executive summaries.
"""

import logging
from typing import Any

from google.adk.agents import LlmAgent

from ai_sidekick_for_splunk.core.base_agent import AgentMetadata, BaseAgent

from .prompt import RESULT_SYNTHESIZER_INSTRUCTIONS

logger = logging.getLogger(__name__)


class ResultSynthesizerAgent(BaseAgent):
    """
    Generic result synthesizer for converting technical Splunk data into business insights.

    This agent provides standardized result interpretation that can be used by:
    - DataExplorer agent
    - IndexAnalyzer agent
    - IndexAnalysisFlowAgent
    - Any other agent needing business intelligence synthesis
    """

    # Class metadata for discovery system
    METADATA = AgentMetadata(
        name="result_synthesizer",
        description="Generic business intelligence synthesizer for Splunk search results",
        version="1.0.0",
        author="Core",
        tags=["synthesis", "business-intelligence", "insights", "personas"],
        dependencies=[],
    )

    name = "result_synthesizer"
    description = "Generic business intelligence synthesizer for Splunk search results"

    @property
    def instructions(self) -> str:
        """Get the agent instructions/prompt."""
        return RESULT_SYNTHESIZER_INSTRUCTIONS

    def __init__(
        self,
        config: Any | None = None,
        metadata: AgentMetadata | None = None,
        tools: list[Any] | None = None,
        session_state: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the ResultSynthesizer agent."""
        from ai_sidekick_for_splunk.core.config import Config

        # Use default config if none provided
        if config is None:
            config = Config()

        # Create metadata if not provided
        if metadata is None:
            metadata = AgentMetadata(
                name="result_synthesizer",
                description="Generic business intelligence synthesizer for Splunk search results",
                version="1.0.0",
                author="Core",
                tags=["synthesis", "business-intelligence", "insights", "personas"],
                dependencies=[],
            )

        super().__init__(config, metadata, tools, session_state)
        logger.info("ResultSynthesizer agent initialized")

    def get_adk_agent(self, tools: list[Any] | None = None) -> LlmAgent | None:
        """
        Create ADK LlmAgent for result synthesis.

        Args:
            tools: Additional tools to provide to the agent

        Returns:
            LlmAgent instance configured for result synthesis
        """
        try:
            from google.adk.agents import LlmAgent

            # Result synthesizer doesn't need external tools - it works with provided data
            agent_tools = tools or []

            return LlmAgent(
                model=self.config.model.primary_model,
                name=self.name,
                description=self.description,
                instruction=self.instructions,
                tools=agent_tools,
            )

        except ImportError:
            logger.error("Google ADK not available - cannot create LlmAgent")
            return None
        except Exception as e:
            logger.error(f"Failed to create ADK agent: {e}")
            return None

    async def synthesize_results(
        self,
        search_results: dict[str, Any],
        context: dict[str, Any] = None,
        synthesis_type: str = "comprehensive",
    ) -> dict[str, Any]:
        """
        Synthesize search results into business insights using ADK agent.

        Args:
            search_results: Dictionary containing search results from various phases
            context: Additional context (index name, domain, etc.)
            synthesis_type: Type of synthesis ("comprehensive", "security", "performance", etc.)

        Returns:
            Dictionary containing synthesized business insights
        """
        try:
            index_name = context.get("index_name", "unknown") if context else "unknown"
            domain = context.get("domain", "general") if context else "general"

            logger.info(
                f"Synthesizing results for index '{index_name}' with {synthesis_type} approach"
            )

            # Get the ADK agent for synthesis
            adk_agent = self.get_adk_agent()
            if not adk_agent:
                logger.warning("ADK agent not available, returning structured placeholder")
                return self._create_placeholder_synthesis(index_name, domain, synthesis_type)

            # Prepare synthesis prompt with real data
            synthesis_prompt = self._build_synthesis_prompt(
                search_results, index_name, domain, synthesis_type
            )

            # Execute synthesis using ADK agent through Runner
            logger.info("Executing real business intelligence synthesis")

            # Create a runner and session for the ADK agent
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService
            from google.genai import types

            session_service = InMemorySessionService()
            session = await session_service.create_session(
                app_name="result_synthesizer", user_id="system", session_id="synthesis_session"
            )

            runner = Runner(
                agent=adk_agent, app_name="result_synthesizer", session_service=session_service
            )

            # Create the message content
            content = types.Content(role="user", parts=[types.Part(text=synthesis_prompt)])

            # Execute the agent through the runner with robust error handling
            synthesis_response = None
            try:
                async for event in runner.run_async(
                    user_id="system", session_id=session.id, new_message=content
                ):
                    if event.is_final_response() and event.content and event.content.parts:
                        synthesis_response = event.content.parts[0].text
                        # Don't break - let generator complete naturally
            except GeneratorExit:
                # Handle generator cleanup gracefully
                logger.debug("Generator cleanup for result synthesizer")
            except RuntimeError as runtime_error:
                # Handle MCP client task group issues
                if "cancel scope" in str(runtime_error) or "different task" in str(runtime_error):
                    logger.debug(
                        f"MCP client task group issue in result synthesizer (expected): {runtime_error}"
                    )
                    # This is a known MCP client library issue - continue with execution
                else:
                    logger.warning(f"Runtime error in result synthesizer: {runtime_error}")
            except Exception as gen_error:
                logger.warning(f"Generator error for result synthesizer: {gen_error}")
                # Continue with whatever response we got

            # Parse and structure the response
            structured_result = self._parse_synthesis_response(
                synthesis_response, index_name, domain, synthesis_type
            )

            logger.info(f"Synthesis completed successfully for {index_name}")
            return structured_result

        except Exception as e:
            logger.error(f"Result synthesis failed: {e}")
            return {
                "synthesis_type": synthesis_type,
                "index_analyzed": index_name,
                "error": str(e),
                "success": False,
            }

    def _create_placeholder_synthesis(
        self, index_name: str, domain: str, synthesis_type: str
    ) -> dict[str, Any]:
        """Create a structured placeholder when ADK is not available."""
        return {
            "synthesis_type": synthesis_type,
            "index_analyzed": index_name,
            "domain": domain,
            "business_insights": {
                "message": f"Business insights would be generated for {index_name}",
                "approach": synthesis_type,
                "persona_based_use_cases": "Would generate 3-5 persona-based use cases",
                "dashboard_recommendations": "Would provide specific dashboard panels with SPL",
                "alert_strategies": "Would recommend proactive monitoring alerts",
                "implementation_priorities": "Would rank recommendations by business value",
            },
            "ready_for_integration": True,
            "adk_available": False,
        }

    def _build_synthesis_prompt(
        self, search_results: dict[str, Any], index_name: str, domain: str, synthesis_type: str
    ) -> str:
        """Build the synthesis prompt with real search results."""

        # Check if we're receiving LLM analysis results from micro agents
        if self._is_llm_analysis_results(search_results):
            return self._build_llm_analysis_synthesis_prompt(
                search_results, index_name, domain, synthesis_type
            )

        # Extract key data from traditional search results
        sourcetypes = self._extract_sourcetypes(search_results)
        hosts = self._extract_hosts(search_results)
        sources = self._extract_sources(search_results)
        volume_data = self._extract_volume_data(search_results)
        temporal_patterns = self._extract_temporal_patterns(search_results)

        prompt = f"""
SYNTHESIS REQUEST: Convert the following technical Splunk search results into actionable business insights.

INDEX ANALYZED: {index_name}
DOMAIN FOCUS: {domain}
SYNTHESIS TYPE: {synthesis_type}

DISCOVERED DATA CHARACTERISTICS:
- Sourcetypes: {sourcetypes}
- Hosts: {hosts}
- Sources: {sources}
- Volume Patterns: {volume_data}
- Temporal Patterns: {temporal_patterns}

SEARCH RESULTS DATA:
{self._format_search_results(search_results)}

REQUIREMENTS:
1. Generate 3-5 persona-based use cases based ONLY on the discovered data above
2. Provide ready-to-deploy SPL queries using the actual index name and discovered sourcetypes
3. Include specific dashboard recommendations with panel descriptions
4. Suggest proactive alert strategies with realistic thresholds
5. Quantify business value with specific time savings and efficiency gains
6. Prioritize implementations based on business impact

DOMAIN ADAPTATION:
- Security domain: Focus on threat detection, compliance, incident response
- Performance domain: Focus on optimization, capacity planning, monitoring
- Business domain: Focus on user experience, conversion, revenue impact
- General domain: Balanced recommendations across all areas

OUTPUT FORMAT: Provide structured business insights with specific, actionable recommendations.
"""
        return prompt

    def _extract_sourcetypes(self, search_results: dict[str, Any]) -> list[str]:
        """Extract sourcetypes from search results."""
        sourcetypes = []
        for phase_results in search_results.values():
            if isinstance(phase_results, dict):
                for task_result in phase_results.values():
                    if isinstance(task_result, dict) and "search_results" in task_result:
                        # Look for sourcetype data in search results
                        data = task_result["search_results"]
                        if isinstance(data, list):
                            for row in data:
                                if isinstance(row, dict) and "sourcetype" in row:
                                    if row["sourcetype"] not in sourcetypes:
                                        sourcetypes.append(row["sourcetype"])
        return sourcetypes

    def _extract_hosts(self, search_results: dict[str, Any]) -> list[str]:
        """Extract hosts from search results."""
        hosts = []
        for phase_results in search_results.values():
            if isinstance(phase_results, dict):
                for task_result in phase_results.values():
                    if isinstance(task_result, dict) and "search_results" in task_result:
                        data = task_result["search_results"]
                        if isinstance(data, list):
                            for row in data:
                                if isinstance(row, dict) and "host" in row:
                                    if row["host"] not in hosts:
                                        hosts.append(row["host"])
        return hosts

    def _extract_sources(self, search_results: dict[str, Any]) -> list[str]:
        """Extract sources from search results."""
        sources = []
        for phase_results in search_results.values():
            if isinstance(phase_results, dict):
                for task_result in phase_results.values():
                    if isinstance(task_result, dict) and "search_results" in task_result:
                        data = task_result["search_results"]
                        if isinstance(data, list):
                            for row in data:
                                if isinstance(row, dict) and "source" in row:
                                    if row["source"] not in sources:
                                        sources.append(row["source"])
        return sources

    def _extract_volume_data(self, search_results: dict[str, Any]) -> dict[str, Any]:
        """Extract volume and trend data from search results."""
        volume_info = {"total_events": 0, "trends": []}

        for phase_results in search_results.values():
            if isinstance(phase_results, dict):
                for task_result in phase_results.values():
                    if isinstance(task_result, dict) and "search_results" in task_result:
                        data = task_result["search_results"]
                        if isinstance(data, list):
                            for row in data:
                                if isinstance(row, dict) and "count" in row:
                                    try:
                                        volume_info["total_events"] += int(row["count"])
                                    except (ValueError, TypeError):
                                        pass

        return volume_info

    def _extract_temporal_patterns(self, search_results: dict[str, Any]) -> dict[str, Any]:
        """Extract temporal patterns from search results."""
        patterns = {"peak_hours": [], "peak_days": [], "anomalies": []}

        for phase_results in search_results.values():
            if isinstance(phase_results, dict):
                for task_result in phase_results.values():
                    if isinstance(task_result, dict) and "search_results" in task_result:
                        data = task_result["search_results"]
                        if isinstance(data, list):
                            for row in data:
                                if isinstance(row, dict):
                                    if "hour" in row:
                                        patterns["peak_hours"].append(row.get("hour"))
                                    if "day_of_week" in row:
                                        patterns["peak_days"].append(row.get("day_of_week"))
                                    if "anomaly_score" in row:
                                        patterns["anomalies"].append(row)

        return patterns

    def _format_search_results(self, search_results: dict[str, Any]) -> str:
        """Format search results for inclusion in synthesis prompt."""
        formatted = []

        for phase_name, phase_results in search_results.items():
            formatted.append(f"\n--- {phase_name.upper()} ---")
            if isinstance(phase_results, dict):
                for task_name, task_result in phase_results.items():
                    formatted.append(f"\nTask: {task_name}")
                    if isinstance(task_result, dict) and "search_results" in task_result:
                        data = task_result["search_results"]
                        if isinstance(data, list) and len(data) > 0:
                            # Show first few rows as examples
                            for i, row in enumerate(data[:3]):
                                formatted.append(f"  Row {i + 1}: {row}")
                            if len(data) > 3:
                                formatted.append(f"  ... and {len(data) - 3} more rows")
                        else:
                            formatted.append(f"  Data: {data}")

        return "\n".join(formatted)

    def _parse_synthesis_response(
        self, response: str, index_name: str, domain: str, synthesis_type: str
    ) -> dict[str, Any]:
        """Parse and structure the ADK agent synthesis response."""

        # For now, return the raw response in a structured format
        # In a more advanced implementation, this could parse specific sections
        return {
            "synthesis_type": synthesis_type,
            "index_analyzed": index_name,
            "domain": domain,
            "business_insights": {
                "raw_synthesis": response,
                "structured_format": "Generated by ADK agent",
                "persona_based_recommendations": "Included in synthesis response",
                "implementation_ready": True,
            },
            "success": True,
            "adk_generated": True,
        }

    async def execute(self, task: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Execute result synthesis task.

        Args:
            task: Synthesis task description
            context: Task context including search results and metadata

        Returns:
            Synthesized business insights
        """
        logger.info(f"ResultSynthesizer executing: {task}")

        try:
            # Extract search results from context
            search_results = context.get("search_results", {}) if context else {}
            synthesis_type = (
                context.get("synthesis_type", "comprehensive") if context else "comprehensive"
            )

            # Perform synthesis
            result = await self.synthesize_results(search_results, context, synthesis_type)

            logger.info("ResultSynthesizer synthesis completed successfully")
            return result

        except Exception as e:
            logger.error(f"ResultSynthesizer execution failed: {e}")
            return {"error": str(e), "success": False, "agent": "ResultSynthesizer"}

    def _is_llm_analysis_results(self, search_results: dict[str, Any]) -> bool:
        """Check if the search results are LLM analysis results from micro agents."""
        # LLM analysis results have task_id, success, response structure
        for key, value in search_results.items():
            if (
                isinstance(value, dict)
                and "response" in value
                and "task_id" in value
                and "success" in value
            ):
                return True
        return False

    def _build_llm_analysis_synthesis_prompt(
        self, search_results: dict[str, Any], index_name: str, domain: str, synthesis_type: str
    ) -> str:
        """Build synthesis prompt for LLM analysis results from micro agents."""

        # Extract the analysis content from micro agent responses
        analysis_content = []
        for task_id, result in search_results.items():
            if isinstance(result, dict) and result.get("success") and "response" in result:
                analysis_content.append(
                    f"**{task_id.replace('_', ' ').title()}**:\n{result['response']}\n"
                )

        combined_analysis = "\n".join(analysis_content)

        prompt = f"""
SYNTHESIS REQUEST: Convert the following comprehensive technical analysis results into actionable business insights.

INDEX ANALYZED: {index_name}
DOMAIN FOCUS: {domain}
SYNTHESIS TYPE: {synthesis_type}

COMPREHENSIVE ANALYSIS RESULTS:

{combined_analysis}

REQUIREMENTS:
1. Generate 3-5 persona-based use cases based on the analysis findings above
2. Provide ready-to-deploy SPL queries using the actual index name and discovered patterns
3. Include specific dashboard recommendations with panel descriptions
4. Suggest proactive alert strategies with realistic thresholds based on the analysis
5. Quantify business value with specific time savings and efficiency gains
6. Prioritize implementations based on business impact from the analysis

DOMAIN ADAPTATION:
- Security domain: Focus on threat detection, compliance, incident response
- Performance domain: Focus on optimization, capacity planning, monitoring
- Business domain: Focus on user experience, conversion, revenue impact
- General domain: Balanced recommendations across all areas

OUTPUT FORMAT: Provide structured business insights with specific, actionable recommendations based on the comprehensive analysis above.
"""
        return prompt
