"""
Researcher Agent for Splunk AI Sidekick.

A specialized core agent that provides research capabilities using Google Search grounding
to access real-time information from the internet. This agent is used by the root agent
for delegation of research tasks requiring current information.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent import ResearcherAgent

__all__ = ["ResearcherAgent"]

# Agent is discovered automatically by the discovery system
# No manual imports needed - discovery handles loading
