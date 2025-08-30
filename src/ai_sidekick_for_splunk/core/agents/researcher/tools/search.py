"""
Google Search Grounding Tool for AI Sidekick for Splunk.

Provides centralized Google Search grounding capability for agents that need
real-time web search functionality. This tool uses ADK's built-in Google Search
grounding rather than custom implementations.

Note: Google Search grounding is only supported in root agents, not sub-agents.
"""

import logging

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import google_search

from ai_sidekick_for_splunk.core.config import Config

logger = logging.getLogger(__name__)

config = Config()

_researcher = Agent(
    model=config.model.primary_model,
    name="researcher",
    description="Search a topic on google.",
    instruction="""
    Answer the user's question directly using Google's search engine; provide a brief but concise answer.
    Instead of a detailed answer, provide the developer with an immediate action item in a single sentence.
    Don't ask the user to verify or look up information on their own; that's your job; do your best to be informative.
    """,
    tools=[google_search],
)

google_search_grounding = AgentTool(agent=_researcher)

# def create_google_search_grounding() -> Optional[Any]:
#     """
#     Create Google Search grounding tool using ADK's built-in capability.

#     Note: This is only supported in root agents, not sub-agents per ADK limitations.

#     Returns:
#         Optional[Any]: Google Search grounding tool or None if not available
#     """
#     try:
#         from google.adk.tools import google_search

#         # Use ADK's built-in Google Search tool directly
#         logger.debug("Using Google Search grounding tool from ADK")
#         return google_search

#     except ImportError:
#         logger.warning("Google Search grounding not available - missing ADK dependencies")
#         return None
#     except Exception as e:
#         logger.error(f"Error accessing Google Search grounding tool: {e}")
#         return None


# # Export the centralized Google Search grounding tool
# google_search_grounding = create_google_search_grounding()
