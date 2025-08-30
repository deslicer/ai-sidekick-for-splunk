"""
Data Explorer Agent - Multi-step business intelligence workflow for Splunk data analysis.

Implements a three-stage workflow: Data Collection → Insights Generation → Quality Assessment
with proper escalation criteria for iterative refinement and business value discovery.
"""

import logging
from collections.abc import AsyncGenerator

from google.adk.agents import BaseAgent, LlmAgent, LoopAgent
from google.adk.events import Event, EventActions

logger = logging.getLogger(__name__)


class DataCollectorAgent(LlmAgent):
    """
    Specialized agent for systematic data collection from Splunk environments.

    Focuses on gathering comprehensive data systematically through the orchestrator,
    returning structured data requests for execution.
    """

    def __init__(self) -> None:
        """Initialize the DataCollector agent."""
        from .prompt import DATA_COLLECTOR_INSTRUCTIONS

        super().__init__(
            name="DataCollector",
            model="gemini-2.0-flash",
            instruction=DATA_COLLECTOR_INSTRUCTIONS,
            description="Systematic data collection specialist for Splunk index analysis",
        )


class InsightGeneratorAgent(LlmAgent):
    """
    Specialized agent for transforming collected data into business insights.

    Takes structured data from collection phase and generates actionable business
    intelligence with quantified value propositions.
    """

    def __init__(self) -> None:
        """Initialize the InsightGenerator agent."""
        from .prompt import INSIGHT_GENERATOR_INSTRUCTIONS

        super().__init__(
            name="InsightGenerator",
            model="gemini-2.0-flash",
            instruction=INSIGHT_GENERATOR_INSTRUCTIONS,
            description="Business insights specialist for data-driven value discovery",
        )


class QualityCheckerAgent(BaseAgent):
    """
    Programmatic quality assessment agent with escalation criteria.

    Provides deterministic quality scoring and escalation decisions for the
    LoopAgent workflow based on explicit criteria and thresholds.
    """

    def __init__(self) -> None:
        """Initialize the QualityChecker agent."""
        super().__init__(
            name="QualityChecker",
            description="Programmatic quality assessment with escalation criteria",
        )

    async def _run_async_impl(self, invocation_context) -> AsyncGenerator[Event, None]:
        """
        Assess insights quality and determine if workflow should continue or escalate.

        Implements programmatic quality checks with scoring and feedback generation.
        """
        # Get the latest insights from session state
        session = invocation_context.session
        insights_data = session.state.get("insights_generated", {})
        collected_data = session.state.get("data_collected", {})

        if not insights_data:
            # No insights available - need to trigger data collection and insights generation
            yield Event(
                author="QualityChecker",
                actions=EventActions(
                    escalate=False,
                    state_delta={
                        "workflow_status": "needs_data_collection",
                        "next_step": "collect_data",
                        "quality_feedback": "No insights data found. Starting data collection workflow.",
                    },
                ),
            )
            return

        # Quality scoring based on multiple criteria
        score = 0
        feedback = []
        max_score = 100

        # 1. Completeness Check (25 points)
        required_fields = ["insights", "data_evidence", "business_impact", "implementation_plan"]
        completeness_score = sum(
            25 // len(required_fields)
            for field in required_fields
            if field in insights_data and insights_data[field]
        )
        score += completeness_score

        if completeness_score < 20:
            feedback.append(
                "Insights lack required sections (insights, evidence, impact, implementation)"
            )

        # 2. Data Foundation Check (25 points)
        if collected_data:
            data_sources = len(collected_data.get("search_results", []))
            if data_sources >= 3:
                score += 25
            elif data_sources >= 2:
                score += 15
                feedback.append("Consider gathering additional data sources for stronger analysis")
            else:
                score += 5
                feedback.append(
                    "Insufficient data sources - need more comprehensive data collection"
                )
        else:
            feedback.append("No data collection found - insights must be based on actual data")

        # 3. Business Value Quantification (25 points)
        insights = insights_data.get("insights", [])
        quantified_insights = 0
        for insight in insights:
            if isinstance(insight, dict):
                impact = insight.get("business_impact", "")
                if any(
                    indicator in str(impact).lower()
                    for indicator in [
                        "$",
                        "%",
                        "reduce",
                        "increase",
                        "save",
                        "improve",
                        "hours",
                        "minutes",
                    ]
                ):
                    quantified_insights += 1

        if len(insights) > 0:
            value_score = min(25, (quantified_insights / len(insights)) * 25)
            score += value_score
            if value_score < 15:
                feedback.append(
                    "Insights need more quantified business value (costs, savings, time, percentages)"
                )
        else:
            feedback.append("No insights generated")

        # 4. Implementation Viability (25 points)
        implementation = insights_data.get("implementation_plan", {})
        if implementation:
            impl_score = 0
            if implementation.get("spl_queries"):
                impl_score += 10
            if implementation.get("dashboards"):
                impl_score += 8
            if implementation.get("alerts"):
                impl_score += 7
            score += impl_score

            if impl_score < 15:
                feedback.append(
                    "Implementation plan needs more specific SPL queries, dashboards, or alerts"
                )
        else:
            feedback.append("Missing implementation plan with actionable next steps")

        # Escalation Decision Logic
        is_complete = score >= 75  # 75% threshold for completion

        # Generate feedback text
        feedback_text = f"Quality Assessment Score: {score}/{max_score}\n"
        if feedback:
            feedback_text += "Areas for improvement:\n• " + "\n• ".join(feedback)
        else:
            feedback_text += "All quality criteria met. Insights are comprehensive and actionable."

        # Store quality metrics in session
        session.state["quality_score"] = score
        session.state["quality_feedback"] = feedback

        yield Event(
            author="QualityChecker",
            actions=EventActions(
                escalate=is_complete,
                state_delta={
                    "workflow_status": "complete" if is_complete else "needs_improvement",
                    "quality_score": score,
                    "quality_feedback": feedback_text,
                    "next_step": "workflow_complete" if is_complete else "refine_insights",
                },
            ),
        )


class DataExplorerAgent(LoopAgent):
    """
    Multi-step data exploration workflow agent.

    Orchestrates systematic data collection, insights generation, and quality assessment
    through iterative refinement cycles until quality criteria are met.

    ## Workflow:
    1. **Data Collection**: Systematic gathering of index data and patterns
    2. **Insights Generation**: Transform data into business intelligence
    3. **Quality Assessment**: Programmatic evaluation with escalation criteria
    4. **Iterative Refinement**: Continue until quality thresholds are met

    ## Quality Criteria:
    - Completeness: All required insight sections present
    - Data Foundation: Multiple data sources analyzed
    - Business Value: Quantified impact and ROI
    - Implementation: Actionable SPL queries and next steps
    """

    def __init__(self) -> None:
        """Initialize the DataExplorer workflow agent."""
        super().__init__(
            name="DataExplorer",
            description="Multi-step data exploration and business intelligence workflow",
            sub_agents=[DataCollectorAgent(), InsightGeneratorAgent(), QualityCheckerAgent()],
            max_iterations=3,
        )

    async def _run_async_impl(self, invocation_context):
        """Override to initialize session state with index information."""
        # Extract index name from various possible input sources
        user_input = None

        # Try different ways to get the user input
        if hasattr(invocation_context, "new_message") and invocation_context.new_message:
            # Get text from ADK message object
            if hasattr(invocation_context.new_message, "parts"):
                for part in invocation_context.new_message.parts:
                    if hasattr(part, "text") and part.text:
                        user_input = part.text
                        break
            elif hasattr(invocation_context.new_message, "text"):
                user_input = invocation_context.new_message.text

        # Fallback: try other possible attributes
        if not user_input:
            for attr in ["message", "input", "query", "content"]:
                if hasattr(invocation_context, attr):
                    potential_input = getattr(invocation_context, attr)
                    if isinstance(potential_input, str):
                        user_input = potential_input
                        break

        # Parse index name if we found input
        if user_input and isinstance(user_input, str):
            import re

            index_match = re.search(r"index\s*=\s*(\w+)", user_input, re.IGNORECASE)
            if index_match:
                index_name = index_match.group(1)
                invocation_context.session.state["target_index"] = index_name
                invocation_context.session.state["user_request"] = user_input
                logger.info(f"DataExplorer: Extracted index '{index_name}' from user input")

        # Call parent implementation to start workflow
        async for event in super()._run_async_impl(invocation_context):
            yield event


# Factory function for easy instantiation
def create_data_explorer_agent() -> DataExplorerAgent:
    """
    Create and return a configured Data Explorer workflow agent.

    Returns:
        DataExplorerAgent: Configured multi-step workflow agent for comprehensive
        data exploration and business insight generation.
    """
    return DataExplorerAgent()


# Export the main agent for discovery system
data_explorer_agent = create_data_explorer_agent()
