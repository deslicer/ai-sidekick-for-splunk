"""
Splunk MCP Agent for real-time Splunk environment access.

A specialized agent that connects to Splunk via MCP (Model Context Protocol)
to provide real-time Splunk administration and search capabilities.
"""

import logging
import uuid
from typing import Any, Optional

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

from ai_sidekick_for_splunk.core.base_agent import AgentMetadata, BaseAgent

from .prompt import SPLUNK_MCP_PROMPT

logger = logging.getLogger(__name__)


class SplunkMCPAgent(BaseAgent):
    """
    Splunk MCP agent for connecting to Splunk via Model Context Protocol.

    This agent provides real-time access to Splunk through MCP toolset,
    allowing direct interaction with Splunk searches, configurations, and administration.
    """

    # Class metadata for discovery system
    METADATA = AgentMetadata(
        name="splunk_mcp",
        description="Expert in Splunk administration, search, and configuration via MCP",
        version="1.0.0",
        author="Core",
        tags=["splunk", "mcp", "administration", "search"],
        dependencies=[],
    )

    name = "splunk_mcp"
    description = "Expert in Splunk administration, search, and configuration via MCP"

    @property
    def instructions(self) -> str:
        """Get the agent instructions/prompt."""
        return SPLUNK_MCP_PROMPT

    def __init__(
        self,
        config: Any | None = None,
        metadata: AgentMetadata | None = None,
        tools: list[Any] | None = None,
        session_state: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the Splunk MCP Agent.

        Args:
            config: Configuration object for the agent
            metadata: Metadata for agent registration
            tools: List of tools available to the agent
            session_state: Session state for the agent
        """
        from ai_sidekick_for_splunk.core.config import Config

        # Use default config if none provided
        if config is None:
            config = Config()

        # Create metadata if not provided
        if metadata is None:
            metadata = AgentMetadata(
                name="splunk_mcp",
                description="Expert in Splunk administration, search, and configuration via MCP",
                version="1.0.0",
                author="Core",
                tags=["splunk", "mcp", "administration", "search"],
                dependencies=[],
            )

        super().__init__(config, metadata, tools, session_state)

        # Create and store MCP toolset for direct execution
        self.mcp_toolset = self._create_mcp_toolset()
        if self.mcp_toolset:
            logger.info("✅ MCP toolset created and stored for direct execution")
        else:
            logger.warning("⚠️ MCP toolset creation failed - direct execution not available")

    def _initialize_llm_agent(self) -> None:
        """Initialize the ADK LlmAgent instance with MCP toolset."""
        try:
            # Import at runtime to avoid import errors
            from google.adk.agents import LlmAgent

            # Create MCP toolset
            mcp_toolset = self._create_mcp_toolset()
            if not mcp_toolset:
                logger.error("Cannot create ADK agent without MCP toolset")
                raise RuntimeError("MCP toolset creation failed")

            # Create agent with MCP toolset - wrap the toolset in a list
            # ADK LlmAgent expects tools to be a list, so wrap the MCPToolset in a list
            self._llm_agent = LlmAgent(
                model=self.config.model.primary_model,
                name=self.display_name,  # Use display_name for user-facing name
                description=self.metadata.description,
                instruction=self.instructions,
                tools=[mcp_toolset],  # Wrap MCPToolset in a list for ADK LlmAgent
            )
            self._is_initialized = True
            logger.debug("Created Splunk MCP ADK agent with MCP toolset")
        except ImportError as e:
            logger.error(f"ADK LlmAgent not available for {self.metadata.name}: {e}")
            raise RuntimeError(
                f"ADK LlmAgent is required for agent {self.metadata.name} but not available"
            ) from e
        except Exception as e:
            logger.error(f"Failed to initialize LlmAgent for {self.metadata.name}: {e}")
            raise

    def _create_mcp_toolset(self) -> MCPToolset | None:
        """
        Create MCP toolset with session management and connection parameters.

        Returns:
            MCPToolset instance or None if creation fails
        """
        try:
            # Session management headers
            session_id = f"ai-sidekick-{uuid.uuid4()}"
            headers = {
                "X-Splunk-Host": self.config.splunk.host,
                "X-Splunk-Port": str(self.config.splunk.port),
                "X-Splunk-Username": self.config.splunk.username,
                "X-Splunk-Password": self.config.splunk.password,
                "X-Splunk-Verify-SSL": str(self.config.splunk.verify_ssl).lower(),
                "X-Session-ID": session_id,
                # Session management features
                "X-Session-Persistent": "true",
                # "X-Session-Timeout": "3600",  # 1 hour
                "X-Connection-Keep-Alive": "true",
                "X-Auto-Reconnect": "true",
                "X-Session-Validation": "enabled",
            }

            # Create MCP toolset with connection parameters
            # Temporarily suppress ADK authentication warnings for MCP tools
            import logging

            adk_auth_logger = logging.getLogger(
                "google_adk.google.adk.tools.base_authenticated_tool"
            )
            original_level = adk_auth_logger.level
            adk_auth_logger.setLevel(logging.ERROR)  # Suppress WARNING level messages

            try:
                mcp_toolset = MCPToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url=self.config.splunk.mcp_server_url,
                        headers=headers,
                        timeout=15.0,  # Increased timeout to reduce premature cancellation
                        sse_read_timeout=300.0,  # 5 minutes for long-running operations
                        terminate_on_close=True,  # Changed to True to properly close connections
                        max_retries=2,  # Reduce retries to minimize task group conflicts
                        retry_delay=1.0,  # Short retry delay
                    )
                )
            finally:
                # Restore original logging level
                adk_auth_logger.setLevel(original_level)
            logger.info(
                f"Enhanced MCP toolset created successfully for URL: {self.config.splunk.mcp_server_url}"
            )
            logger.debug(
                f"Session management features enabled: persistent sessions, auto-reconnect, validation (session_id={session_id})"
            )
            return mcp_toolset

        except Exception as e:
            logger.error(f"Failed to create MCP toolset: {e}")
            return None

    def get_adk_agent(self, tools: list[Any] | None = None) -> LlmAgent | None:
        """
        Create ADK LlmAgent for Splunk MCP operations.

        Args:
            tools: Optional list of tools (typically empty for MCP agent as it has its own toolset)

        Returns:
            ADK LlmAgent configured with MCP toolset
        """
        try:
            # Create MCP toolset
            mcp_toolset = self._create_mcp_toolset()
            if not mcp_toolset:
                logger.error("Cannot create ADK agent without MCP toolset")
                return None

            # Create agent with MCP toolset - wrap the toolset in a list
            # ADK LlmAgent expects tools to be a list, so wrap the MCPToolset in a list
            agent = LlmAgent(
                model=self.config.model.primary_model,
                name=self.name,
                description=self.description,
                instruction=SPLUNK_MCP_PROMPT,
                tools=[mcp_toolset],  # Wrap MCPToolset in a list for ADK LlmAgent
            )

            logger.debug("Created Splunk MCP ADK agent with MCP toolset")
            return agent

        except Exception as e:
            logger.error(f"Failed to create Splunk MCP ADK agent: {e}")
            return None

    async def execute(self, task: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Execute a Splunk MCP task using the ADK LlmAgent with MCP toolset.

        Args:
            task: The task description (natural language or SPL query)
            context: Optional context for the task

        Returns:
            Dict[str, Any]: Dictionary containing the task result
        """
        try:
            logger.info(f"SplunkMCPAgent executing task: {task}")

            # Add context parameters if provided
            if context:
                # Format context parameters for the request
                context_params = []
                for key, value in context.items():
                    if key in ["earliest_time", "latest_time"] and value:
                        context_params.append(f"{key}={value}")

                if context_params:
                    task = f"{task}\nParameters: {dict(context)}"

            # Use the ADK LlmAgent which automatically has access to all MCP tools
            result = await self.process_request(task, context)

            logger.info("✅ SplunkMCP task executed successfully")
            return {
                "success": True,
                "task_type": "splunk_mcp",
                "response": result,
                "execution_method": "adk_agent_with_mcp_tools",
            }

        except Exception as e:
            logger.error(f"SplunkMCPAgent execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to execute Splunk MCP task",
            }

    def get_capabilities(self) -> list[str]:
        """
        Get agent capabilities.

        Returns:
            List[str]: List of agent capabilities
        """
        return [
            "splunk_search",
            "splunk_administration",
            "mcp_integration",
            "real_time_splunk_access",
            "configuration_management",
        ]

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """
        Validate input data for the agent.

        Args:
            input_data: Input data to validate

        Returns:
            bool: True if input is valid
        """
        return "task" in input_data or "query" in input_data

    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        logger.info("SplunkMCPAgent cleanup completed")
        pass
