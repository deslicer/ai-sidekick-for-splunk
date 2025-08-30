"""
IndexAnalysisFlow Agent - Specialized Workflow Executor

The IndexAnalysisFlow agent is a specialized agent that executes comprehensive
index analysis using the Guided Agent Flows framework. It demonstrates how
to create custom workflow agents that leverage the flow engine while maintaining
specialized behavior and optimizations.

This agent serves as a reference implementation for creating specialized
workflow agents that go beyond the universal FlowPilot approach.

Key Features:
- Guided Agent Flows framework integration
- Bounded intelligence task execution
- Multi-agent coordination (splunk_mcp, search_guru, result_synthesizer)
- Comprehensive index analysis workflows
- Professional business intelligence synthesis
- Error recovery and fallback mechanisms

Usage:
    from ai_sidekick_for_splunk.core.agents.index_analysis_flow import IndexAnalysisFlowAgent

    # Create specialized index analysis agent
    agent = IndexAnalysisFlowAgent()

    # Execute index analysis workflow
    result = await agent.execute("analyze index=main")
"""

from .agent import IndexAnalysisFlowAgent

__all__ = [
    "IndexAnalysisFlowAgent"
]
