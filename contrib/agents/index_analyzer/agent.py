"""
IndexAnalyzer Agent - Base Implementation.

Index analyzer agent
"""

import logging
from typing import Any

from google.adk.agents import LlmAgent

from splunk_ai_sidekick.core.base_agent import AgentMetadata, BaseAgent
from splunk_ai_sidekick.core.config import Config

logger = logging.getLogger(__name__)


class IndexAnalyzerAgent(BaseAgent):
    """
    Index analyzer agent

    Base agent implementation ready for customization with specific workflows.
    """

    # Class metadata for discovery system
    METADATA = AgentMetadata(
        name="IndexAnalyzer",
        description="Systematic Splunk index analysis to provide actionable insights",
        version="1.0.0",
        author="Workshop Participant",
        tags=["index_analyzer", "agent", "base"],
        dependencies=["splunk_mcp", "result_synthesizer"]
    )

    name = "IndexAnalyzer"
    description = "Index analyzer agent"

    def __init__(
        self,
        config: Config | None = None,
        metadata: AgentMetadata | None = None,
        tools: list[Any] | None = None
    ) -> None:
        """Initialize the IndexAnalyzer agent."""
        logger.info("🔧 Initializing IndexAnalyzer agent", extra={
            "event_type": "index_analyzer_initialization",
            "event_data": {"agent_name": "IndexAnalyzer", "version": "1.0.0"}
        })

        super().__init__(config or Config(), metadata or self.METADATA, tools or [])

        logger.info("✅ IndexAnalyzer agent initialized successfully", extra={
            "event_type": "index_analyzer_created",
            "event_data": {
                "agent_name": self.name,
                "description": self.description,
                "tools_count": len(tools or [])
            }
        })

    @property
    def instructions(self) -> str:
        """Get the agent instructions/prompt."""
        from .prompt import INDEX_ANALYZER_INSTRUCTIONS
        return INDEX_ANALYZER_INSTRUCTIONS

    def get_adk_agent(self, tools: list[Any] | None = None) -> LlmAgent | None:
        """
        Create ADK LlmAgent for orchestrator integration.

        Args:
            tools: List of tools to provide to the agent

        Returns:
            Configured LlmAgent instance
        """
        try:
            logger.info(f"🔧 Creating {self.name} LlmAgent")

            agent = LlmAgent(
                name=self.name,
                model="gemini-2.5-pro",
                instruction=self.instructions,
                description=self.description,
                tools=tools or []
            )

            # Store the ADK agent for use in execute method
            self._adk_agent = agent

            logger.info(f"✅ {self.name} LlmAgent created successfully")
            return agent

        except Exception as e:
            logger.error(f"❌ Failed to create {self.name} LlmAgent: {e}")
            return None

    def execute(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute comprehensive index analysis workflow.

        Args:
            task: The task description from the user
            context: Optional context information

        Returns:
            Dictionary containing the analysis results
        """
        try:
            logger.info(f"IndexAnalyzer executing task: {task}")

            # Extract index name from task
            import re
            index_match = re.search(r'index[=\s]+([^\s]+)', task.lower())
            if not index_match:
                return {
                    "success": False,
                    "error": "No index specified in task",
                    "message": "Please specify an index to analyze (e.g., 'analyze index=pas')"
                }

            index_name = index_match.group(1)
            logger.info(f"Analyzing index: {index_name}")

            return self._execute_analysis_workflow(index_name)

        except Exception as e:
            logger.error(f"IndexAnalyzer execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Index analysis execution failed"
            }

    def _execute_analysis_workflow(self, index_name: str) -> dict[str, Any]:
        """
        Execute comprehensive index analysis workflow with Splunk data collection.

        Args:
            index_name: The index to analyze

        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"🔍 Executing analysis workflow for index={index_name}")

        splunk_agent = self._get_splunk_agent()
        if not splunk_agent:
            return {
                "success": False,
                "error": "splunk_mcp agent not available",
                "message": "Cannot execute searches without splunk_mcp agent"
            }

        # Execute each task with actual Splunk searches
        analysis_results = {}
        workflow_tasks = self._get_workflow_tasks(index_name)

        for task_id, task_config in workflow_tasks.items():
            logger.info(f"Executing {task_config['name']}")

            try:
                # Execute the SPL query through splunk_mcp
                search_result = self._execute_splunk_search(splunk_agent, task_config['spl_query'])

                analysis_results[task_id] = {
                    "name": task_config['name'],
                    "status": "completed",
                    "spl_query": task_config['spl_query'],
                    "search_results": search_result,
                    "findings": self._analyze_task_results(task_id, search_result)
                }

            except Exception as e:
                logger.error(f"Task {task_id} execution failed: {e}")
                analysis_results[task_id] = {
                    "name": task_config['name'],
                    "status": "failed",
                    "spl_query": task_config['spl_query'],
                    "error": str(e),
                    "findings": f"Task execution encountered an error: {str(e)}"
                }

        total_tasks = len(workflow_tasks)
        return {
            "success": True,
            "message": f"🎯 **INDEX ANALYSIS COMPLETE** - {total_tasks}-task workflow executed for index={index_name}",
            "index": index_name,
            "execution_method": "analysis_workflow",
            "analysis_tasks": analysis_results,
            "ready_for_synthesis": True,
            "transfer_message": "🎯 **READY FOR BUSINESS INTELLIGENCE SYNTHESIS** - Analysis complete"
        }

    def _get_splunk_agent(self):
        """Get the splunk_mcp agent from orchestrator."""
        orchestrator = getattr(self, 'orchestrator', None)
        if orchestrator:
            return orchestrator.registry_manager.agent_registry.get_agent('splunk_mcp')
        return None

    def _get_workflow_tasks(self, index_name: str) -> dict[str, dict[str, str]]:
        """
        Get the analysis workflow tasks with their SPL queries.

        Args:
            index_name: The index to analyze

        Returns:
            Dictionary of task configurations
        """
        return {
            "task_1": {
                "name": "📊 Data Types Discovery",
                "spl_query": f"| tstats summariesonly=true count WHERE index={index_name} by _time, sourcetype | timechart span=1h sum(count) by sourcetype"
            },
            "task_2": {
                "name": "🔍 Field Analysis",
                "spl_query": f"index={index_name} | head 5000 | fields * | fieldsummary"
            },
            "task_3": {
                "name": "📋 Sample Data Collection",
                "spl_query": f"index={index_name} | head 10 | table _time, index, source, sourcetype, _raw"
            },
            "task_4": {
                "name": "⚡ Volume Assessment",
                "spl_query": f"| rest /services/data/indexes | search title={index_name} | table title, currentDBSizeMB, totalEventCount, maxTime, minTime"
            },
            "task_5": {
                "name": "🎯 Cross-Reference Analysis",
                "spl_query": f"index={index_name} | stats count by sourcetype, source | sort -count"
            }
        }

    def _execute_splunk_search(self, splunk_agent, spl_query: str) -> dict[str, Any]:
        """
        Execute a Splunk search through the splunk_mcp agent.

        Args:
            splunk_agent: The splunk_mcp agent instance
            spl_query: The SPL query to execute

        Returns:
            Dictionary containing search results
        """
        try:
            # Execute search through splunk_mcp agent
            result = splunk_agent.execute_search(spl_query)
            return result
        except Exception as e:
            logger.error(f"Splunk search execution failed: {e}")
            return {"error": str(e), "results": []}

    def _analyze_task_results(self, task_id: str, search_results: dict[str, Any]) -> str:
        """
        Analyze the results from a specific task.

        Args:
            task_id: The task identifier
            search_results: The results from the Splunk search

        Returns:
            String containing analysis findings
        """
        if "error" in search_results:
            return f"Search execution error: {search_results['error']}"

        results = search_results.get("results", [])
        result_count = len(results)

        task_analysis = {
            "task_1": f"Discovered {result_count} sourcetype patterns with time-based distribution",
            "task_2": f"Analyzed field distribution across {result_count} sample events",
            "task_3": f"Collected {result_count} representative data samples for review",
            "task_4": f"Retrieved volume metrics: {result_count} index statistics",
            "task_5": f"Cross-referenced {result_count} sourcetype and source combinations"
        }

        return task_analysis.get(task_id, f"Processed {result_count} search results")

    def supports_streaming(self, task: str) -> bool:
        """
        Check if the given task supports streaming responses.

        Args:
            task: The task to check

        Returns:
            True if streaming is supported, False otherwise
        """
        # DISABLED: IndexAnalyzer should provide complete, single reports
        # instead of streaming chunks to ensure seamless transfer to result_synthesizer
        # and comprehensive final output
        return False

    def validate_input(self, task: str, context: dict[str, Any] | None = None) -> bool:
        """
        Validate input parameters for the task.

        Args:
            task: The task to validate
            context: Optional context to validate

        Returns:
            True if input is valid, False otherwise
        """
        # Basic validation - contributors can add specific validation
        if not task or not isinstance(task, str) or not task.strip():
            return False
        return True

    def get_capabilities(self) -> list[str]:
        """
        Get list of agent capabilities.

        Returns:
            List of capability strings
        """
        # Default capabilities - contributors should override
        return [
            "Basic task execution",
            "Input validation",
            "ADK integration",
            "Orchestrator compatibility"
        ]


# Factory function for easy instantiation
def create_index_analyzer_agent() -> IndexAnalyzerAgent:
    """
    Create and return a configured IndexAnalyzer agent.

    Returns:
        IndexAnalyzerAgent: Configured agent instance
    """
    return IndexAnalyzerAgent()


# Agent instance for auto-discovery
index_analyzer_agent = create_index_analyzer_agent()
