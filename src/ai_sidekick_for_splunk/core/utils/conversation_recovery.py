"""
Conversation recovery utilities for AI Sidekick for Splunk.

This module provides graceful error handling for tool call failures and conversation recovery
to ensure users get helpful responses instead of broken conversations.
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Import ADK BaseAgent for proper inheritance
try:
    from google.adk.agents.base_agent import BaseAgent as ADKBaseAgent
except ImportError:
    # Fallback if ADK not available during import
    ADKBaseAgent = object


class ConversationRecoveryHandler:
    """Handles tool call failures and conversation recovery."""

    @staticmethod
    def create_tool_error_response(tool_call_id: str, error_message: str) -> dict[str, Any]:
        """Create a proper tool response for failed tool calls."""
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": f"⚠️ Tool execution failed: {error_message}. The operation could not be completed.",
        }

    @staticmethod
    def extract_missing_tool_calls(error_message: str) -> list[str]:
        """Extract missing tool call IDs from OpenAI/LiteLLM error message."""
        pattern = r"call_[a-zA-Z0-9]+"
        return re.findall(pattern, error_message)

    @staticmethod
    def create_recovery_message(missing_calls: list[str]) -> str:
        """Create user-friendly recovery message."""
        return (
            "🔄 I encountered a technical issue while processing your request. "
            "Let me help you with a fresh approach. Could you please rephrase "
            "your question or try a different way to accomplish your goal?"
        )

    @staticmethod
    def is_tool_call_error(error_message: str) -> bool:
        """Check if error is related to missing tool call responses."""
        indicators = [
            "tool_call_id",
            "did not have response messages",
            "tool messages responding to each 'tool_call_id'",
            "assistant message with 'tool_calls' must be followed",
        ]
        return any(indicator in error_message for indicator in indicators)


class RobustLlmAgent(ADKBaseAgent):
    """Wrapper around LlmAgent with conversation recovery capabilities."""

    def __init__(self, base_agent: Any):
        # Don't call super().__init__() - we're a pure wrapper, not a real BaseAgent
        # Just store the base agent and recovery handler
        self.base_agent = base_agent
        self.recovery_handler = ConversationRecoveryHandler()

    def _run_async_impl(self, *args, **kwargs):
        """Delegate _run_async_impl to the base agent."""
        return self.base_agent._run_async_impl(*args, **kwargs)

    def _run_live_impl(self, *args, **kwargs):
        """Delegate _run_live_impl to the base agent."""
        return self.base_agent._run_live_impl(*args, **kwargs)

    @property
    def tools(self):
        """Delegate tools property to the base agent."""
        return self.base_agent.tools

    @tools.setter
    def tools(self, value):
        """Delegate tools setter to the base agent."""
        self.base_agent.tools = value

    @property
    def description(self):
        """Delegate description property to the base agent."""
        return self.base_agent.description

    @description.setter
    def description(self, value):
        """Delegate description setter to the base agent."""
        self.base_agent.description = value

    @property
    def model(self):
        """Delegate model property to the base agent."""
        return self.base_agent.model

    @model.setter
    def model(self, value):
        """Delegate model setter to the base agent."""
        self.base_agent.model = value

    @property
    def instruction(self):
        """Delegate instruction property to the base agent."""
        return getattr(self.base_agent, "instruction", None)

    @instruction.setter
    def instruction(self, value):
        """Delegate instruction setter to the base agent."""
        if hasattr(self.base_agent, "instruction"):
            self.base_agent.instruction = value

    @property
    def name(self):
        """Delegate name property to the base agent."""
        return getattr(self.base_agent, "name", "RobustLlmAgent")

    @name.setter
    def name(self, value):
        """Delegate name setter to the base agent."""
        if hasattr(self.base_agent, "name"):
            self.base_agent.name = value

    def _resolve_tools(self, *args, **kwargs):
        """Delegate _resolve_tools to the base agent."""
        return self.base_agent._resolve_tools(*args, **kwargs)

    def __getattribute__(self, name: str) -> Any:
        """Intercept ALL attribute access to ensure proper delegation."""
        # Handle our own attributes first
        if name in ["base_agent", "recovery_handler"]:
            return object.__getattribute__(self, name)

        # Handle critical ADK properties that need delegation
        if name in ["model", "instruction", "tools", "name", "description"]:
            try:
                base_agent = object.__getattribute__(self, "base_agent")
                result = getattr(base_agent, name)
                return result
            except AttributeError:
                return object.__getattribute__(self, name)

        # For all other attributes, try base_agent first, then self
        try:
            base_agent = object.__getattribute__(self, "base_agent")
            if hasattr(base_agent, name):
                result = getattr(base_agent, name)
                return result
        except AttributeError:
            pass

        # Fall back to normal attribute access
        return object.__getattribute__(self, name)

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the base agent (fallback)."""
        # Always delegate to base_agent first (both public and private attributes)
        if hasattr(self.base_agent, name):
            result = getattr(self.base_agent, name)
            return result
        else:
            # Fall back to BaseAgent's implementation for attributes not in base_agent
            return getattr(super(), name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Delegate attribute setting, but keep our own attributes."""
        if name in ["base_agent", "recovery_handler"]:
            self.__dict__[name] = value
        else:
            # Delegate to base agent if it exists and has the attribute
            if hasattr(self, "base_agent") and hasattr(self.base_agent, name):
                setattr(self.base_agent, name, value)
            else:
                # Fall back to setting on self for initialization
                self.__dict__[name] = value

    def __repr__(self) -> str:
        """Return representation of the base agent."""
        return repr(self.base_agent)

    def __str__(self) -> str:
        """Return string representation of the base agent."""
        return str(self.base_agent)


class RecoveryAwareOrchestrator:
    """Orchestrator mixin that provides recovery capabilities."""

    def __init__(self):
        self.conversation_recovery = ConversationRecoveryHandler()

    def wrap_agent_with_recovery(self, agent: Any) -> RobustLlmAgent:
        """Wrap any agent with recovery capabilities."""
        return RobustLlmAgent(agent)

    def handle_conversation_error(
        self, error: Exception, context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Handle conversation errors with appropriate recovery strategies."""
        error_str = str(error)
        context = context or {}

        # Tool call errors
        if self.conversation_recovery.is_tool_call_error(error_str):
            missing_calls = self.conversation_recovery.extract_missing_tool_calls(error_str)

            return {
                "recovery_needed": True,
                "recovery_type": "tool_call_error",
                "user_message": self.conversation_recovery.create_recovery_message(missing_calls),
                "technical_details": {
                    "error_type": "tool_call_error",
                    "missing_calls": missing_calls,
                    "original_error": error_str,
                },
            }

        # Network/API errors
        elif any(
            keyword in error_str.lower() for keyword in ["timeout", "connection", "network", "api"]
        ):
            return {
                "recovery_needed": True,
                "recovery_type": "network_error",
                "user_message": "I'm having trouble connecting to external services. Please try again in a moment.",
                "technical_details": {"error_type": "network_error", "original_error": error_str},
            }

        # Rate limit errors
        elif any(keyword in error_str.lower() for keyword in ["rate limit", "quota", "429"]):
            return {
                "recovery_needed": True,
                "recovery_type": "rate_limit_error",
                "user_message": "The service is currently busy. Please wait a moment before trying again.",
                "technical_details": {
                    "error_type": "rate_limit_error",
                    "original_error": error_str,
                },
            }

        # Generic system errors
        else:
            return {
                "recovery_needed": True,
                "recovery_type": "system_error",
                "user_message": "I encountered an unexpected issue. Please try rephrasing your request.",
                "technical_details": {"error_type": "system_error", "original_error": error_str},
            }
