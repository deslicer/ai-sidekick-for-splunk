"""
Conversation recovery utilities for AI Sidekick for Splunk.

This module provides graceful error handling for tool call failures and conversation recovery
to ensure users get helpful responses instead of broken conversations.
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


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


class RobustLlmAgent:
    """Wrapper around LlmAgent with conversation recovery capabilities."""

    def __init__(self, base_agent: Any):
        self.base_agent = base_agent
        self.recovery_handler = ConversationRecoveryHandler()

    async def run_async(self, messages: list[dict[str, Any]], **kwargs) -> dict[str, Any]:
        """Run agent with automatic conversation recovery."""
        try:
            # Try normal execution
            result = await self.base_agent.run_async(messages, **kwargs)
            return {"success": True, "result": result, "recovered": False, "error_type": None}

        except Exception as e:
            error_str = str(e)
            logger.warning(f"Agent execution error: {error_str}")

            # Check if it's a tool call response error
            if self.recovery_handler.is_tool_call_error(error_str):
                logger.info("Detected tool call error, attempting recovery")

                # Extract missing tool call IDs
                missing_calls = self.recovery_handler.extract_missing_tool_calls(error_str)

                if missing_calls:
                    logger.info(
                        f"Found {len(missing_calls)} missing tool calls, creating recovery response"
                    )

                    # Create synthetic tool responses for missing calls
                    recovery_messages = messages.copy()
                    for call_id in missing_calls:
                        tool_response = self.recovery_handler.create_tool_error_response(
                            call_id, "Tool execution was interrupted or failed"
                        )
                        recovery_messages.append(tool_response)

                    # Add recovery message
                    recovery_message = self.recovery_handler.create_recovery_message(missing_calls)
                    recovery_messages.append({"role": "assistant", "content": recovery_message})

                    return {
                        "success": True,
                        "result": {
                            "content": recovery_message,
                            "metadata": {
                                "recovered_from_error": True,
                                "original_error": "Tool call interruption",
                                "missing_tool_calls": len(missing_calls),
                                "recovery_type": "tool_call_failure",
                            },
                        },
                        "recovered": True,
                        "error_type": "tool_call_error",
                    }

            # For other errors, provide generic recovery
            logger.error(f"Unexpected agent error (not recoverable): {error_str}")
            generic_recovery = (
                "I'm experiencing technical difficulties with that request. "
                "Please try rephrasing your question or try again in a moment."
            )

            return {
                "success": False,
                "result": {
                    "content": generic_recovery,
                    "metadata": {
                        "recovered_from_error": True,
                        "original_error": "Unexpected system error",
                        "recovery_type": "generic_error",
                    },
                },
                "recovered": True,
                "error_type": "system_error",
                "original_error": error_str,
            }

    def run_sync(self, messages: list[dict[str, Any]], **kwargs) -> dict[str, Any]:
        """Synchronous version for compatibility."""
        import asyncio

        async def _run():
            return await self.run_async(messages, **kwargs)

        try:
            return asyncio.run(_run())
        except Exception as e:
            logger.error(f"Synchronous execution failed: {e}")
            return {
                "success": False,
                "result": {
                    "content": "A system error occurred. Please try again.",
                    "metadata": {"error": str(e)},
                },
                "recovered": False,
                "error_type": "sync_execution_error",
            }


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
