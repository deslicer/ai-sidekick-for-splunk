"""
Observability utilities for AI Sidekick for Splunk.

This module provides AgentOps integration for comprehensive observability,
session tracking, and performance monitoring of ADK agents.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class ObservabilityManager:
    """
    Manages observability integration for AI Sidekick using AgentOps.

    Provides session management, tracing, and monitoring capabilities
    for ADK agents with minimal setup overhead.
    """

    _initialized = False
    _session_active = False

    @classmethod
    def initialize(
        cls,
        trace_name: Optional[str] = None,
        api_key: Optional[str] = None,
        auto_start_session: bool = True,
    ) -> bool:
        """
        Initialize AgentOps observability.

        Args:
            trace_name: Name for the trace session (defaults to "ai-sidekick-for-splunk")
            api_key: AgentOps API key (defaults to AGENTOPS_API_KEY env var)
            auto_start_session: Whether to automatically start a session

        Returns:
            True if initialization successful, False otherwise
        """
        if cls._initialized:
            logger.debug("AgentOps already initialized")
            return True

        # Get API key from parameter or environment
        api_key = api_key or os.getenv("AGENTOPS_API_KEY")
        if not api_key:
            logger.info("AgentOps API key not found, observability disabled")
            return False

        try:
            import agentops

            # Initialize AgentOps with configuration
            agentops.init(
                api_key=api_key,
                trace_name=trace_name or "ai-sidekick-for-splunk",
                auto_start_session=auto_start_session,
            )

            cls._initialized = True
            cls._session_active = auto_start_session

            logger.info("✅ AgentOps observability initialized successfully")
            if auto_start_session:
                logger.info("📊 AgentOps session started for comprehensive tracing")

            return True

        except ImportError:
            logger.warning("AgentOps package not installed, observability disabled")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize AgentOps: {e}")
            return False

    @classmethod
    def start_session(cls, session_name: Optional[str] = None) -> bool:
        """
        Start a new AgentOps session.

        Args:
            session_name: Optional name for the session

        Returns:
            True if session started successfully, False otherwise
        """
        if not cls._initialized:
            logger.warning("AgentOps not initialized, cannot start session")
            return False

        if cls._session_active:
            logger.debug("AgentOps session already active")
            return True

        try:
            import agentops

            agentops.start_session(session_name)
            cls._session_active = True
            logger.info(f"📊 AgentOps session started: {session_name or 'default'}")
            return True

        except Exception as e:
            logger.error(f"Failed to start AgentOps session: {e}")
            return False

    @classmethod
    def end_session(cls, end_state: str = "Success") -> None:
        """
        End the current AgentOps session.

        Args:
            end_state: State to end the session with (Success, Fail, etc.)
        """
        if not cls._initialized or not cls._session_active:
            return

        try:
            import agentops

            agentops.end_session(end_state)
            cls._session_active = False
            logger.info(f"📊 AgentOps session ended with state: {end_state}")

        except Exception as e:
            logger.error(f"Failed to end AgentOps session: {e}")

    @classmethod
    def record_event(cls, event_type: str, event_data: dict) -> None:
        """
        Record a custom event in AgentOps.

        Args:
            event_type: Type of event to record
            event_data: Data associated with the event
        """
        if not cls._initialized or not cls._session_active:
            return

        try:
            import agentops

            agentops.record(event_type, event_data)
            logger.debug(f"📊 Recorded AgentOps event: {event_type}")

        except Exception as e:
            logger.error(f"Failed to record AgentOps event: {e}")

    @classmethod
    def is_enabled(cls) -> bool:
        """
        Check if AgentOps observability is enabled and initialized.

        Returns:
            True if AgentOps is enabled and initialized, False otherwise
        """
        return cls._initialized

    @classmethod
    def is_session_active(cls) -> bool:
        """
        Check if an AgentOps session is currently active.

        Returns:
            True if a session is active, False otherwise
        """
        return cls._initialized and cls._session_active

    @classmethod
    def get_session_url(cls) -> Optional[str]:
        """
        Get the URL for the current AgentOps session.

        Returns:
            Session URL if available, None otherwise
        """
        if not cls._initialized or not cls._session_active:
            return None

        try:
            import agentops

            # AgentOps typically provides session info
            # This is a placeholder - actual implementation may vary
            return getattr(agentops, "session_url", None)

        except Exception as e:
            logger.error(f"Failed to get AgentOps session URL: {e}")
            return None


def initialize_observability(
    trace_name: Optional[str] = None, api_key: Optional[str] = None, auto_start_session: bool = True
) -> bool:
    """
    Convenience function to initialize AgentOps observability.

    Args:
        trace_name: Name for the trace session
        api_key: AgentOps API key
        auto_start_session: Whether to automatically start a session

    Returns:
        True if initialization successful, False otherwise
    """
    return ObservabilityManager.initialize(
        trace_name=trace_name, api_key=api_key, auto_start_session=auto_start_session
    )


def end_observability_session(end_state: str = "Success") -> None:
    """
    Convenience function to end the current AgentOps session.

    Args:
        end_state: State to end the session with
    """
    ObservabilityManager.end_session(end_state)
