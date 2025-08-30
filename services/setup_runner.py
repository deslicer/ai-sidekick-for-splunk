"""
Setup Runner for AI Sidekick for Splunk agent execution.

This module provides a runner for setting up and executing the AI Sidekick for Splunk agents
with proper session management, artifact service, and LLM configuration.
"""
import logging
import os
import uuid
from typing import Any

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from ..core.config import Config

logger = logging.getLogger(__name__)

class SetupRunner:
    """
    Runner for AI Sidekick for Splunk agent setup and execution.

    This class handles the setup and execution of the AI Sidekick for Splunk agents
    with the appropriate session management, artifact service, LLM configuration,
    and execution context.
    """

    def __init__(
        self,
        agent=None,
        model: str | None = None,
        config: Config | None = None,
    ):
        """
        Initialize the Setup Runner.

        Args:
            agent: The root agent to use (if None, will import lazily)
            model: LLM model to use, defaults to config.model.primary_model
            config: Configuration instance, defaults to Config()
        """
        self.config = config or Config()
        self.model = model or self.config.model.primary_model

        # Use ADK's InMemorySessionService as recommended starting point
        self.session_service = InMemorySessionService()
        logger.info("Using ADK InMemorySessionService for session management")

        # Initialize ADK's InMemoryArtifactService for artifact storage
        self.artifact_service = InMemoryArtifactService()
        logger.info("Using ADK InMemoryArtifactService for artifact management")

        # Get the agent (import lazily to avoid circular imports)
        if agent is None:
            from ..agent import root_agent
            agent = root_agent

        # Create RunConfig with streaming enabled (configurable via environment)
        enable_streaming = os.getenv("SPLUNK_AI_ENABLE_STREAMING", "true").lower() == "true"
        max_llm_calls = int(os.getenv("SPLUNK_AI_MAX_LLM_CALLS", "200"))

        self.run_config = RunConfig(
            streaming_mode=StreamingMode.SSE if enable_streaming else StreamingMode.NONE,
            max_llm_calls=max_llm_calls
        )

        # Initialize the runner with the root agent, session service, and artifact service
        self.runner = Runner(
            agent=agent,
            app_name="splunk-ai-sidekick",
            session_service=self.session_service,
            artifact_service=self.artifact_service
        )

        logger.info(f"Initialized Setup Runner with model: {self.model}")
        logger.info("Services configured: SessionService, ArtifactService")
        logger.info(f"Streaming enabled: {self.run_config.streaming_mode} with max {self.run_config.max_llm_calls} LLM calls")

    async def execute(
        self,
        user_query: str,
        session_id: str | None = None,
        user_id: str = "default-user",
        context_args: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a user query using the configured agent with proper ADK session management.

        Args:
            user_query: The user's query text
            session_id: Optional session ID (generates one if not provided)
            user_id: User identifier for session management
            context_args: Optional context arguments to include as initial state

        Returns:
            Response dictionary with reply and optional metadata
        """
        # Generate a session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Created new session ID: {session_id}")

        try:
            # Create or get session using proper ADK SessionService API
            # According to ADK docs, create_session will return existing session if it exists
            session = await self.session_service.create_session(
                app_name="splunk-ai-sidekick",
                user_id=user_id,
                state=context_args or {},
                session_id=session_id
            )

            logger.debug(f"Using session: {session.id} for user: {session.user_id}")

            # Create user message content according to ADK patterns
            from google.genai import types
            user_message = types.Content(
                role="user",
                parts=[types.Part(text=user_query)]
            )

            # Execute the query using the runner with proper session and streaming config
            # According to ADK docs, run_async returns an async generator of events
            final_response = None
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=user_message,
                run_config=self.run_config  # Enable streaming with SSE
            ):
                # Process events and capture final response
                if event.is_final_response() and event.content and event.content.parts:
                    final_response = event.content.parts[0].text

            # Get updated session to include latest state and events
            updated_session = await self.session_service.get_session(
                app_name="splunk-ai-sidekick",
                user_id=user_id,
                session_id=session.id
            )

            # Format the response according to ADK response structure
            result = {
                "session_id": session.id,
                "reply": final_response or "No response generated",
                "success": True
            }

            # Add session metadata from updated session if available
            if updated_session:
                result["metadata"] = {
                    "app_name": updated_session.app_name,
                    "user_id": updated_session.user_id,
                    "last_update_time": updated_session.last_update_time,
                    "events_count": len(updated_session.events),
                    "state_keys": list(updated_session.state.keys()) if updated_session.state else []
                }
            else:
                result["metadata"] = {
                    "app_name": "splunk-ai-sidekick",
                    "user_id": user_id,
                    "events_count": 0,
                    "state_keys": []
                }

            return result

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            # Return error response
            return {
                "session_id": session_id,
                "reply": f"I encountered an error processing your request. Please try again. Error: {str(e)}",
                "success": False,
                "error": str(e)
            }

    async def clean_session(
        self,
        session_id: str,
        user_id: str = "default-user"
    ) -> dict[str, Any]:
        """
        Clean up a session by ID using proper ADK SessionService API.

        According to ADK documentation, this removes the session and all associated
        data including events and state from the SessionService storage.

        Args:
            session_id: The session ID to clean up
            user_id: User identifier for session management

        Returns:
            Status dictionary indicating success
        """
        try:
            # Check if session exists before attempting deletion
            existing_session = await self.session_service.get_session(
                app_name="splunk-ai-sidekick",
                user_id=user_id,
                session_id=session_id
            )

            if existing_session is None:
                logger.warning(f"Session {session_id} not found for user {user_id}")
                return {
                    "success": False,
                    "message": f"Session {session_id} not found"
                }

            # Use proper ADK SessionService delete_session method
            await self.session_service.delete_session(
                app_name="splunk-ai-sidekick",
                user_id=user_id,
                session_id=session_id
            )

            logger.info(f"Successfully deleted session {session_id} for user {user_id}")
            return {
                "success": True,
                "message": f"Session {session_id} deleted successfully",
                "deleted_events_count": len(existing_session.events),
                "deleted_state_keys": list(existing_session.state.keys()) if existing_session.state else []
            }
        except Exception as e:
            logger.error(f"Error cleaning session {session_id}: {e}")
            return {
                "success": False,
                "message": f"Error cleaning session: {str(e)}"
            }

    async def list_sessions(self, user_id: str = "default-user") -> dict[str, Any]:
        """
        List all sessions for a user using proper ADK SessionService API.

        According to ADK documentation, this returns all active sessions for the
        specified user within the application scope.

        Args:
            user_id: User identifier for session management

        Returns:
            Dictionary with list of sessions and metadata
        """
        try:
            # Use proper ADK SessionService list_sessions method
            sessions_response = await self.session_service.list_sessions(
                app_name="splunk-ai-sidekick",
                user_id=user_id
            )

            # Handle the response object (it might be a ListSessionsResponse or direct list)
            if hasattr(sessions_response, 'sessions'):
                sessions = sessions_response.sessions
            elif isinstance(sessions_response, list):
                sessions = sessions_response
            else:
                # Handle case where response is iterable but not a list
                sessions = list(sessions_response) if sessions_response else []

            # Format session information according to ADK Session object structure
            session_list = []
            for session in sessions:
                session_info = {
                    "session_id": session.id,
                    "app_name": session.app_name,
                    "user_id": session.user_id,
                    "last_update_time": session.last_update_time,
                    "events_count": len(session.events),
                    "state_keys": list(session.state.keys()) if session.state else [],
                    "has_user_state": any(key.startswith("user:") for key in session.state.keys()) if session.state else False,
                    "has_app_state": any(key.startswith("app:") for key in session.state.keys()) if session.state else False,
                    "has_temp_state": any(key.startswith("temp:") for key in session.state.keys()) if session.state else False
                }
                session_list.append(session_info)

            logger.info(f"Found {len(session_list)} sessions for user {user_id}")
            return {
                "success": True,
                "sessions": session_list,
                "total_count": len(session_list),
                "user_id": user_id,
                "app_name": "splunk-ai-sidekick"
            }
        except Exception as e:
            logger.error(f"Error listing sessions for user {user_id}: {e}")
            return {
                "success": False,
                "message": f"Error listing sessions: {str(e)}",
                "sessions": [],
                "total_count": 0,
                "user_id": user_id
            }

    async def get_session_details(
        self,
        session_id: str,
        user_id: str = "default-user"
    ) -> dict[str, Any]:
        """
        Get detailed information about a specific session using ADK SessionService API.

        According to ADK documentation, this retrieves the complete session object
        including all events, state, and metadata.

        Args:
            session_id: The session ID to retrieve
            user_id: User identifier for session management

        Returns:
            Dictionary with detailed session information
        """
        try:
            # Use proper ADK SessionService get_session method
            session = await self.session_service.get_session(
                app_name="splunk-ai-sidekick",
                user_id=user_id,
                session_id=session_id
            )

            if session is None:
                logger.warning(f"Session {session_id} not found for user {user_id}")
                return {
                    "success": False,
                    "message": f"Session {session_id} not found"
                }

            # Format detailed session information
            session_details = {
                "session_id": session.id,
                "app_name": session.app_name,
                "user_id": session.user_id,
                "last_update_time": session.last_update_time,
                "events_count": len(session.events),
                "state": dict(session.state) if session.state else {},
                "events": [
                    {
                        "id": event.id,
                        "author": event.author,
                        "timestamp": event.timestamp,
                        "content": event.content.parts[0].text if event.content and event.content.parts else None,
                        "is_final_response": event.is_final_response()
                    }
                    for event in session.events
                ],
                "state_analysis": {
                    "session_state_keys": [k for k in session.state.keys() if not k.startswith(("user:", "app:", "temp:"))] if session.state else [],
                    "user_state_keys": [k for k in session.state.keys() if k.startswith("user:")] if session.state else [],
                    "app_state_keys": [k for k in session.state.keys() if k.startswith("app:")] if session.state else [],
                    "temp_state_keys": [k for k in session.state.keys() if k.startswith("temp:")] if session.state else []
                }
            }

            logger.info(f"Retrieved session details for {session_id}")
            return {
                "success": True,
                "session": session_details
            }
        except Exception as e:
            logger.error(f"Error getting session details for {session_id}: {e}")
            return {
                "success": False,
                "message": f"Error getting session details: {str(e)}"
            }
