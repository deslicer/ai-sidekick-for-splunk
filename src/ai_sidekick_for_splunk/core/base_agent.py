"""
Base agent class for AI Sidekick for Splunk.

This module provides the foundational BaseAgent class that all Splunk AI agents
should inherit from. It implements common functionality and enforces the
contract for agent implementations.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from .config import Config

logger = logging.getLogger(__name__)


@dataclass
class AgentMetadata:
    """Metadata for agent registration and discovery."""

    name: str
    description: str
    version: str = "1.0.0"
    author: str = "Unknown"
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    display_name: str | None = None  # User-friendly name for web interface
    disabled: bool = False  # If True, agent will be skipped during discovery


class BaseAgent(ABC):
    """
    Base class for all Splunk AI agents.

    This class provides the foundational structure and common functionality
    that all agents in the AI Sidekick for Splunk framework should implement.
    It integrates with Google ADK's LlmAgent pattern while providing
    Splunk-specific abstractions.

    Attributes:
        config: Configuration instance for the agent
        metadata: Agent metadata for registration and discovery
        tools: List of tools available to this agent
        _llm_agent: Internal ADK LlmAgent instance
        _session_state: Shared session state for multi-agent communication
    """

    def __init__(
        self,
        config: Config,
        metadata: AgentMetadata,
        tools: list[Any] | None = None,
        session_state: dict[str, Any] | None = None,
    ):
        """
        Initialize the base agent.

        Args:
            config: Configuration instance
            metadata: Agent metadata
            tools: List of tools for this agent
            session_state: Shared session state
        """
        self.config = config
        self.metadata = metadata
        self.tools = tools or []
        self._session_state = session_state or {}
        self._llm_agent: Any | None = None
        self._is_initialized = False

        logger.info(f"Initializing agent: {self.metadata.name}")

    @property
    @abstractmethod
    def instructions(self) -> str:
        """
        Get the agent instructions/prompt.

        This property must be implemented by all agent subclasses to define
        the agent's behavior and personality.

        Returns:
            String containing the agent instructions
        """
        pass

    @property
    def model_name(self) -> str:
        """
        Get the preferred model for this agent.

        Returns:
            Model name (defaults to config primary model if not overridden)
        """
        return self.config.model.primary_model

    @property
    def display_name(self) -> str:
        """
        Get the display name for this agent.

        Returns:
            Display name (uses display_name from metadata if available, otherwise name)
        """
        return self.metadata.display_name or self.metadata.name

    def get_llm_agent(self) -> Any | None:
        """
        Get the underlying ADK LlmAgent instance.

        Returns:
            LlmAgent instance if available, None otherwise
        """
        if not self._is_initialized:
            self._initialize_llm_agent()
        return self._llm_agent

    def _initialize_llm_agent(self) -> None:
        """Initialize the ADK LlmAgent instance."""
        try:
            # Import at runtime to avoid import errors
            from google.adk.agents import LlmAgent

            self._llm_agent = LlmAgent(
                model=self.model_name,
                name=self.display_name,  # Use display_name for user-facing name
                description=self.metadata.description,
                instruction=self.instructions,
                tools=self.tools,
            )
            self._is_initialized = True
            logger.debug(f"Initialized LlmAgent for: {self.metadata.name}")
        except ImportError as e:
            logger.error(f"ADK LlmAgent not available for {self.metadata.name}: {e}")
            raise RuntimeError(
                f"ADK LlmAgent is required for agent {self.metadata.name} but not available"
            ) from e
        except Exception as e:
            logger.error(f"Failed to initialize LlmAgent for {self.metadata.name}: {e}")
            raise

    async def process_request(self, request: str, context: dict[str, Any] | None = None) -> str:
        """
        Process a request using the agent.

        Args:
            request: The request string to process
            context: Additional context for the request

        Returns:
            Response string from the agent

        Raises:
            RuntimeError: If agent is not properly initialized
        """
        if not self._is_initialized:
            self._initialize_llm_agent()

        if self._llm_agent is None:
            raise RuntimeError(
                f"Agent {self.metadata.name} failed to initialize LlmAgent - cannot process request"
            )

        try:
            # Merge context with session state
            full_context = {**self._session_state, **(context or {})}

            # In a real implementation, this would use ADK's Runner or direct LlmAgent execution
            logger.info(f"Processing request with agent: {self.metadata.name}")

            # This is a placeholder - actual implementation would depend on ADK patterns
            response = await self._execute_with_context(request, full_context)

            return response

        except Exception as e:
            logger.error(f"Error processing request in {self.metadata.name}: {e}")
            raise

    async def _execute_with_context(self, request: str, context: dict[str, Any]) -> str:
        """
        Execute the request with the given context.

        This method can be overridden by subclasses for custom execution logic.

        Args:
            request: The request to execute
            context: Execution context

        Returns:
            Response string
        """
        # This is a placeholder implementation
        # Real implementation would use ADK Runner patterns
        return f"Response from {self.metadata.name} for: {request}"

    def add_tool(self, tool: Any) -> None:
        """
        Add a tool to this agent.

        Args:
            tool: Tool to add
        """
        self.tools.append(tool)
        # If already initialized, we might need to reinitialize with new tools
        if self._is_initialized:
            logger.info(f"Adding tool to initialized agent {self.metadata.name} - reinitializing")
            self._is_initialized = False

    def update_session_state(self, key: str, value: Any) -> None:
        """
        Update the shared session state.

        Args:
            key: State key
            value: State value
        """
        self._session_state[key] = value
        logger.debug(f"Updated session state in {self.metadata.name}: {key}")

    def get_session_state(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the shared session state.

        Args:
            key: State key
            default: Default value if key not found

        Returns:
            State value or default
        """
        return self._session_state.get(key, default)

    def validate_configuration(self) -> list[str]:
        """
        Validate the agent configuration.

        Returns:
            List of validation error messages
        """
        errors = []

        if not self.metadata.name:
            errors.append("Agent metadata must have a name")

        if not self.instructions:
            errors.append("Agent must provide instructions")

        # Validate dependencies
        for dep in self.metadata.dependencies:
            if not isinstance(dep, str):
                errors.append(f"Invalid dependency type: {type(dep)}")

        return errors

    def __repr__(self) -> str:
        """String representation of the agent."""
        return (
            f"BaseAgent("
            f"name='{self.metadata.name}', "
            f"version='{self.metadata.version}', "
            f"tools={len(self.tools)}, "
            f"initialized={self._is_initialized})"
        )
