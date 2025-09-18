"""
LLM Model management for AI Sidekick for Splunk.

This module provides multi-model support through LiteLLM integration,
allowing seamless switching between different LLM providers while
maintaining compatibility with Google ADK.
"""

from .factory import ModelFactory
from .litellm_wrapper import LiteLlmWrapper

__all__ = ["ModelFactory", "LiteLlmWrapper"]
