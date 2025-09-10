"""
Index Analysis Guided Agent Flow - Production Ready.

This agent demonstrates the Guided Agent Flows framework by implementing
the enhanced goal-driven index analysis workflow using Reasoning Flow Definitions
with bounded intelligence capabilities.
"""

import logging
import re
from pathlib import Path
from typing import Any, Optional

from google.adk.agents import LlmAgent
from google.adk.events import Event
from google.genai.types import Content, Part

from ...base_agent import AgentMetadata, BaseAgent
from ...config import Config
from ...flows_engine.agent_flow import AgentFlow
from ...flows_engine.flow_engine import FlowEngine, FlowExecutionResult, ProgressUpdate

logger = logging.getLogger(__name__)


class IndexAnalysisFlowAgent(BaseAgent):
    """
    Agent that executes index analysis using the Guided Agent Flows framework.

    This production-ready agent demonstrates how Reasoning Flow Definitions
    with bounded intelligence tasks can create sophisticated, reusable,
    and context-aware analysis agents.
    """

    # Class metadata for discovery system
    METADATA = AgentMetadata(
        name="IndexAnalysisFlow",
        description="Production-ready index analysis using Guided Agent Flows framework with bounded intelligence and ResultSynthesizer integration",
        version="1.0.0",
        author="Saikrishna Gundeti",
        tags=[
            "index_analysis",
            "guided_agent_flows",
            "reasoning_flow_definitions",
            "bounded_intelligence",
            "production",
            "modular",
        ],
        dependencies=["search_guru", "splunk_mcp", "result_synthesizer"],
        disabled=True,  # Disabled - reference implementation, use FlowPilot IndexAnalysis instead
    )

    name = "IndexAnalysisFlow"
    description = "Context-aware index analysis agent using Guided Agent Flows framework with bounded intelligence"

    def __init__(
        self,
        config: Config | None = None,
        metadata: AgentMetadata | None = None,
        tools: list[Any] | None = None,
        session_state: dict[str, Any] | None = None,
        flow_definition_path: str | None = None,
        orchestrator=None,
    ) -> None:
        """
        Initialize the IndexAnalysisFlowAgent.

        Args:
            config: Configuration instance
            metadata: Agent metadata
            tools: List of tools for this agent
            session_state: Shared session state
            flow_definition_path: Path to flow JSON definition
            orchestrator: Main orchestrator for agent coordination
        """
        logger.info(
            "🔧 Initializing IndexAnalysisFlowAgent (POC)",
            extra={
                "event_type": "flow_agent_initialization",
                "event_data": {"agent_name": "IndexAnalysisFlow", "version": "1.0.0-poc"},
            },
        )

        super().__init__(config or Config(), metadata or self.METADATA, tools or [], session_state)

        # Set default flow definition path
        if not flow_definition_path:
            current_dir = Path(__file__).parent
            # Use enhanced LLM loop flow for parallel testing
            flow_definition_path = (
                current_dir.parent.parent / "flows" / "index_analysis" / "index_analysis.json"
            )

        self.flow_definition_path = Path(flow_definition_path)
        self.orchestrator = orchestrator
        self.agent_flow: AgentFlow | None = None
        self.flow_engine: FlowEngine | None = None

        # Load and validate flow definition
        self._load_flow_definition()

    def set_orchestrator(self, orchestrator):
        """
        Set the orchestrator for this agent after initialization.

        This is needed because agents are created during discovery before
        the orchestrator is fully initialized.
        """
        self.orchestrator = orchestrator
        if self.flow_engine:
            self.flow_engine.agent_coordinator.orchestrator = orchestrator
            # Clear agent cache to force re-retrieval with new orchestrator
            self.flow_engine.agent_coordinator._agent_cache.clear()
            logger.info(f"✅ Orchestrator set for {self.name} - agent coordination enabled")

        logger.info(
            "✅ IndexAnalysisFlowAgent initialized successfully",
            extra={
                "event_type": "flow_agent_created",
                "event_data": {
                    "agent_name": self.name,
                    "flow_definition": str(self.flow_definition_path),
                    "flow_loaded": self.agent_flow is not None,
                },
            },
        )

    def _load_flow_definition(self) -> None:
        """Load and validate the agent flow definition."""
        try:
            if not self.flow_definition_path.exists():
                logger.error(f"Flow definition not found: {self.flow_definition_path}")
                return

            # Load flow from JSON
            self.agent_flow = AgentFlow.load_from_json(self.flow_definition_path)

            # Validate flow
            validation_errors = self.agent_flow.validate()
            if validation_errors:
                logger.error(f"Flow validation failed: {validation_errors}")
                self.agent_flow = None
                return

            # Initialize flow engine with progress callback
            self.flow_engine = FlowEngine(self.config, self.orchestrator, self._progress_callback)

            logger.info(
                f"Flow definition loaded successfully: {self.agent_flow.workflow_name} v{self.agent_flow.version}"
            )

        except Exception as e:
            logger.error(f"Failed to load flow definition: {e}")
            self.agent_flow = None
            self.flow_engine = None

    def _progress_callback(self, update: ProgressUpdate) -> None:
        """
        Handle progress updates from the FlowEngine.

        This converts FlowEngine progress updates into ADK Events for streaming.
        """
        # Create a structured log message for progress tracking
        progress_message = f"🔄 **{update.phase_name}**"
        if update.task_id:
            progress_message += f" | Task: {update.task_id}"
        if update.step_number:
            progress_message += f" | Step: {update.step_number}"

        progress_message += f" | Status: {update.status}"
        if update.message:
            progress_message += f"\n{update.message}"

        # Log with structured data for potential streaming pickup
        logger.info(
            progress_message,
            extra={
                "event_type": "flow_progress_update",
                "event_data": {
                    "phase_name": update.phase_name,
                    "task_id": update.task_id,
                    "step_number": update.step_number,
                    "status": update.status,
                    "message": update.message,
                    "data": update.data,
                },
            },
        )

        # Store progress updates for streaming (if we had access to the event stream)
        if not hasattr(self, "_progress_updates"):
            self._progress_updates = []
        self._progress_updates.append(update)

    def _create_progress_event(self, update: ProgressUpdate) -> Event:
        """Convert a ProgressUpdate to an ADK Event for streaming."""
        # Create content with the progress message
        progress_text = f"🔄 **{update.phase_name}**"
        if update.task_id:
            progress_text += f" | Task: {update.task_id}"
        if update.step_number:
            progress_text += f" | Step: {update.step_number}"

        progress_text += f" | Status: {update.status}"
        if update.message:
            progress_text += f"\n{update.message}"

        content = Content(role="model", parts=[Part(text=progress_text)])

        # Create ADK Event
        return Event(
            author=self.name,
            content=content,
            partial=True,  # This is a streaming update, not final
            turn_complete=False,
        )

    @property
    def instructions(self) -> str:
        """Get the agent instructions/prompt."""
        from .prompt import INDEX_ANALYSIS_FLOW_AGENT_INSTRUCTIONS

        return INDEX_ANALYSIS_FLOW_AGENT_INSTRUCTIONS

    def get_adk_agent(self, tools: list[Any] | None = None) -> LlmAgent | None:
        """
        Create ADK LlmAgent for flow-based index analysis.

        Args:
            tools: Optional list of tools

        Returns:
            ADK LlmAgent configured for flow execution
        """
        try:
            if not self.agent_flow:
                logger.error("Cannot create ADK agent without valid flow definition")
                return None

            # Add our execute method as a tool that the LLM can call
            flow_tools = (tools or []).copy()

            # Create a tool function that calls our execute method
            def execute_index_analysis_flow(
                task: str, context: Optional[dict[str, Any]] = None
            ) -> dict[str, Any]:
                """
                Execute the comprehensive index analysis workflow.

                Args:
                    task: The index analysis task (e.g., "analyze index=s4c_www")
                    context: Optional additional context

                Returns:
                    Dictionary containing the comprehensive analysis results
                """
                # Create a synchronous wrapper for the async execute method
                import asyncio

                try:
                    # Try to get the current event loop
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If we're already in an async context, we need to handle this differently
                        # For now, we'll create a new event loop in a thread
                        import concurrent.futures

                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, self.execute(task, context))
                            return future.result()
                    else:
                        # We can run the async method directly
                        return loop.run_until_complete(self.execute(task, context))
                except RuntimeError:
                    # No event loop exists, create one
                    return asyncio.run(self.execute(task, context))

            # Add the execute function as a tool
            flow_tools.append(execute_index_analysis_flow)

            # Create agent with flow-based instructions that tell it to use the tool
            custom_instructions = f"""
You are the IndexAnalysisFlow agent that executes comprehensive Splunk index analysis using Guided Agent Flows.

CRITICAL: When a user requests index analysis, you MUST:
1. 🚀 Call the 'execute_index_analysis_flow' tool with their request
2. 📋 Present the complete analysis results to the user

The execute_index_analysis_flow tool will:
1. 📊 Execute a multi-phase analysis workflow
2. ⚡ Stream progress updates as it works
3. 🤝 Coordinate with specialist agents (search_guru_agent, splunk_mcp_agent, result_synthesizer_agent) using hybrid synthesis approach
4. 📈 Provide real analysis results (not simulated data)
5. 🎯 Automatically generate actionable JSON insights via result_synthesizer when meaningful data is found

Your workflow includes:
- 🔍 Phase 1: Initial Index Overview & Data Volume Analysis
- 🏗️ Phase 2: Field Extraction & Data Quality Assessment
- ⚡ Phase 3: Performance and Efficiency Analysis
- 🔗 Phase 4: Cross-Sourcetype Correlation Analysis
- 💡 Phase 5: Actionable Insights and Recommendations

The workflow automatically handles result synthesis - you just need to present the complete results.

NEVER provide static responses or fabricated data. Always use the execute_index_analysis_flow tool and present its complete output.

{self.instructions}
"""

            # Create agent with flow-based instructions
            agent = LlmAgent(
                model=self.config.model.primary_model,
                name=self.name,
                description=self.description,
                instruction=custom_instructions,
                tools=flow_tools,
            )

            logger.debug(
                f"Created IndexAnalysisFlow ADK agent with flow: {self.agent_flow.workflow_name}"
            )
            return agent

        except Exception as e:
            logger.error(f"Failed to create IndexAnalysisFlow ADK agent: {e}")
            return None

    async def execute(self, task: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Execute index analysis using the loaded agent flow.

        Args:
            task: The task description from the user
            context: Optional context information

        Returns:
            Dictionary containing the comprehensive analysis results
        """
        try:
            logger.info(f"🚀 IndexAnalysisFlowAgent executing task: {task}")
            logger.debug(f"🔍 Agent orchestrator: {self.orchestrator}")
            logger.debug(
                f"🔍 FlowEngine orchestrator: {self.flow_engine.agent_coordinator.orchestrator if self.flow_engine else 'NO_FLOW_ENGINE'}"
            )

            if not self.agent_flow or not self.flow_engine:
                error_msg = "Flow definition not loaded"
                logger.error(f"❌ {error_msg}")
                logger.error(f"❌ Agent flow: {self.agent_flow}")
                logger.error(f"❌ Flow engine: {self.flow_engine}")
                return {
                    "success": False,
                    "error": error_msg,
                    "message": "Agent flow definition could not be loaded. Please check the flow configuration.",
                }

            # Extract index name from task
            index_name = self._extract_index_name(task)
            if not index_name:
                error_msg = "No index specified in task"
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "message": "Please specify an index to analyze (e.g., 'analyze index=pas')",
                }

            # Prepare execution context
            execution_context = {
                "index_name": index_name,
                "INDEX_NAME": index_name,  # Add uppercase version for placeholder resolution
                "task": task,
                **(context or {}),
            }
            logger.debug(f"🔍 Execution context: {execution_context}")

            logger.info(f"🎯 Starting flow execution for index: {index_name}")

            # Execute the flow using the real flow engine
            logger.debug("🔍 About to call flow_engine.execute_flow()")
            flow_result = await self.flow_engine.execute_flow(self.agent_flow, execution_context)
            logger.debug(f"🔍 Flow result type: {type(flow_result)}")
            logger.debug(f"🔍 Flow result: {flow_result}")

            # Format results for user
            if flow_result is None:
                logger.error("❌ CRITICAL: flow_result is None!")
                return {
                    "success": False,
                    "error": "Flow execution returned None",
                    "message": "Flow execution failed - no result returned",
                }

            formatted_result = self._format_flow_results(flow_result)

            return formatted_result

        except Exception as e:
            logger.error(f"IndexAnalysisFlowAgent execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Flow execution failed due to an unexpected error",
            }

    def _extract_index_name(self, task: str) -> str | None:
        """Extract index name from user task."""
        # Look for index=name pattern
        index_match = re.search(r"index[=\s]+([^\s]+)", task.lower())
        if index_match:
            return index_match.group(1)
        return None

    def _format_flow_results(self, flow_result: FlowExecutionResult) -> dict[str, Any]:
        """Format flow execution results for user presentation."""
        if not flow_result.success:
            return {
                "success": False,
                "error": flow_result.error_summary,
                "message": "Flow execution failed",
            }

        # Format comprehensive results
        # Safely handle synthesized_output
        synthesized_output = flow_result.synthesized_output or {}

        # Format insights and recommendations for better readability
        formatted_insights = self._format_insights_for_readability(synthesized_output)
        formatted_recommendations = self._format_recommendations_for_readability(synthesized_output)

        formatted_result = {
            "success": True,
            "flow_name": flow_result.flow_name,
            "execution_summary": {
                "total_execution_time": f"{flow_result.total_execution_time:.1f} seconds",
                "phases_completed": len(flow_result.phase_results),
                "overall_success": flow_result.success,
            },
            "analysis_results": {},
            "key_insights": formatted_insights,
            "discovered_data": synthesized_output.get("discovered_data", {}),
            "recommendations": formatted_recommendations,
            "business_intelligence_summary": self._create_business_summary(synthesized_output),
            "synthesized_output": synthesized_output,  # Include the complete synthesized output
        }

        # Format phase results
        for phase_result in flow_result.phase_results:
            phase_data = {
                "phase_name": phase_result.phase_name,
                "success": phase_result.success,
                "execution_time": f"{phase_result.execution_time:.1f}s",
                "tasks": [],
            }

            for task_result in phase_result.task_results:
                task_data = {
                    "task_id": task_result.task_id,
                    "success": task_result.success,
                    "execution_time": f"{task_result.execution_time:.1f}s"
                    if task_result.execution_time
                    else "N/A",
                }

                if task_result.data:
                    # Extract key information from task data
                    if "search_results" in task_result.data:
                        results = task_result.data["search_results"].get("results", [])
                        task_data["result_count"] = len(results)
                        task_data["sample_results"] = results[:3]  # Show first 3 results

                    if "interpretation" in task_result.data:
                        interp = task_result.data["interpretation"]
                        if interp and isinstance(interp, dict):
                            task_data["interpretation"] = interp.get("interpretation", "")
                            task_data["insights"] = interp.get("insights", [])
                        else:
                            task_data["interpretation"] = ""
                            task_data["insights"] = []

                phase_data["tasks"].append(task_data)

            formatted_result["analysis_results"][phase_result.phase_name] = phase_data

        # Add template-specific insights
        formatted_result["template_insights"] = {
            "workflow_used": self.agent_flow.workflow_name,
            "version": self.agent_flow.version,
            "agent_coordination": f"Coordinated with {len(self.agent_flow.agent_dependencies)} dependent agents",
            "validation_performed": "All searches validated by search_guru",
            "synthesis_method": "Built-in ADK parallel fan-out/gather synthesis pattern",
        }

        return formatted_result

    def _format_insights_for_readability(
        self, synthesized_output: dict[str, Any]
    ) -> dict[str, Any]:
        """Format insights from synthesized output for better readability."""
        formatted_insights = {
            "summary": "🔍 Key insights extracted from the analysis:",
            "by_phase": {},
            "total_insights": 0,
        }

        phase_synthesis = synthesized_output.get("phase_synthesis", {})

        for phase_name, phase_data in phase_synthesis.items():
            if isinstance(phase_data, dict) and "result" in phase_data:
                result = phase_data["result"]
                if isinstance(result, dict) and "key_insights" in result:
                    insights = result["key_insights"]
                    if insights:
                        formatted_phase_insights = []
                        for insight in insights:
                            if isinstance(insight, dict):
                                # Add emojis based on confidence and category
                                confidence = insight.get("confidence", "medium")
                                source = insight.get("source_task", "unknown")

                                # Choose emoji based on confidence
                                confidence_emoji = {"high": "🎯", "medium": "📊", "low": "💡"}.get(
                                    confidence, "📋"
                                )

                                # Choose emoji based on source/category
                                source_emoji = {
                                    "security": "🔒",
                                    "performance": "⚡",
                                    "data_quality": "🏗️",
                                    "business": "💼",
                                    "technical": "🔧",
                                    "unknown": "📈",
                                }.get(
                                    source.lower() if isinstance(source, str) else "unknown", "📋"
                                )

                                insight_text = insight.get("insight", "").strip()
                                formatted_insight = {
                                    "insight": f"{confidence_emoji} {source_emoji} {insight_text}",
                                    "confidence": confidence,
                                    "source": source,
                                }
                                # Clean up the insight text
                                if insight_text and len(insight_text) > 10:
                                    formatted_phase_insights.append(formatted_insight)

                        if formatted_phase_insights:
                            formatted_insights["by_phase"][phase_name] = {
                                "phase_description": phase_data.get("context", ""),
                                "insights": formatted_phase_insights,
                                "insight_count": len(formatted_phase_insights),
                            }
                            formatted_insights["total_insights"] += len(formatted_phase_insights)

        return formatted_insights

    def _format_recommendations_for_readability(
        self, synthesized_output: dict[str, Any]
    ) -> dict[str, Any]:
        """Format recommendations from synthesized output for better readability with emojis."""
        formatted_recommendations = {
            "summary": "💡 Actionable recommendations based on the analysis:",
            "by_priority": {
                "high": {"title": "🚨 High Priority", "items": []},
                "medium": {"title": "⚠️ Medium Priority", "items": []},
                "low": {"title": "💭 Low Priority", "items": []},
            },
            "by_category": {},
            "total_recommendations": 0,
        }

        phase_synthesis = synthesized_output.get("phase_synthesis", {})

        for phase_name, phase_data in phase_synthesis.items():
            if isinstance(phase_data, dict) and "result" in phase_data:
                result = phase_data["result"]
                if isinstance(result, dict) and "recommendations" in result:
                    recommendations = result["recommendations"]
                    if recommendations:
                        for rec in recommendations:
                            if isinstance(rec, dict):
                                priority = rec.get("priority", "medium")
                                category = rec.get("category", "operational")

                                # Choose emojis based on priority and category
                                priority_emoji = {"high": "🚨", "medium": "⚠️", "low": "💭"}.get(
                                    priority, "📋"
                                )

                                category_emoji = {
                                    "security": "🔒",
                                    "performance": "⚡",
                                    "operational": "🔧",
                                    "data_quality": "🏗️",
                                    "business": "💼",
                                    "monitoring": "📊",
                                    "optimization": "🎯",
                                }.get(category, "📋")

                                rec_text = rec.get("recommendation", "").strip()
                                formatted_rec = {
                                    "recommendation": f"{priority_emoji} {category_emoji} {rec_text}",
                                    "priority": priority,
                                    "category": category,
                                    "source_phase": phase_name,
                                    "source_task": rec.get("source_task", "unknown"),
                                }

                                # Clean up the recommendation text
                                if rec_text and len(rec_text) > 20:
                                    # Add to priority groups
                                    if priority in formatted_recommendations["by_priority"]:
                                        formatted_recommendations["by_priority"][priority][
                                            "items"
                                        ].append(formatted_rec)

                                    # Add to category groups
                                    if category not in formatted_recommendations["by_category"]:
                                        category_title = (
                                            f"{category_emoji} {category.replace('_', ' ').title()}"
                                        )
                                        formatted_recommendations["by_category"][category] = {
                                            "title": category_title,
                                            "items": [],
                                        }
                                    formatted_recommendations["by_category"][category][
                                        "items"
                                    ].append(formatted_rec)

                                    formatted_recommendations["total_recommendations"] += 1

        return formatted_recommendations

    def _create_business_summary(self, synthesized_output: dict[str, Any]) -> dict[str, Any]:
        """Create a high-level business intelligence summary with emojis."""
        summary = synthesized_output.get("summary", "")
        phase_synthesis = synthesized_output.get("phase_synthesis", {})

        business_summary = {
            "executive_summary": f"📋 Executive Summary: {summary}",
            "key_findings": [],
            "business_impact": {"title": "💼 Business Impact Assessment", "areas": {}},
            "next_actions": {"title": "🚀 Recommended Next Actions", "items": []},
        }

        # Extract key business findings from phase synthesis
        for phase_name, phase_data in phase_synthesis.items():
            if isinstance(phase_data, dict) and "result" in phase_data:
                result = phase_data["result"]
                if isinstance(result, dict):
                    # Look for business-relevant insights
                    insights = result.get("key_insights", [])
                    for insight in insights:
                        if isinstance(insight, dict):
                            insight_text = insight.get("insight", "")
                            if any(
                                keyword in insight_text.lower()
                                for keyword in [
                                    "error",
                                    "performance",
                                    "volume",
                                    "pattern",
                                    "anomaly",
                                    "correlation",
                                ]
                            ):
                                business_summary["key_findings"].append(
                                    {
                                        "finding": insight_text,
                                        "phase": phase_name,
                                        "confidence": insight.get("confidence", "medium"),
                                    }
                                )

        # Extract business impact indicators
        discovered_data = synthesized_output.get("discovered_data", {})
        if discovered_data:
            business_summary["business_impact"] = {
                "data_patterns_identified": len(discovered_data),
                "analysis_coverage": "Multi-phase comprehensive analysis",
                "reliability_indicators": list(discovered_data.keys()),
            }

        return business_summary


# Factory function for agent discovery
def create_index_analysis_flow_agent(
    config: Config | None = None, orchestrator=None, **kwargs
) -> IndexAnalysisFlowAgent:
    """
    Factory function to create IndexAnalysisFlowAgent instance.

    Args:
        config: Configuration instance
        orchestrator: Main orchestrator instance
        **kwargs: Additional arguments

    Returns:
        IndexAnalysisFlowAgent instance
    """
    return IndexAnalysisFlowAgent(config=config, orchestrator=orchestrator, **kwargs)


# Agent instance for discovery
index_analysis_flow_agent = create_index_analysis_flow_agent()
