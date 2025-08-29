"""
Configuration management for Splunk AI Sidekick.

This module provides centralized configuration management for the framework,
including model settings, discovery paths, and runtime parameters.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for LLM models."""
    # Default to Gemini models for Google ADK compatibility
    # Note: Using 2.0-flash for better multi-tool support (Google Search + sub-agents)
    # See: https://ai.google.dev/gemini-api/docs/function-calling for supported models
    primary_model: str = field(default_factory=lambda: os.getenv("SPLUNK_AI_MODEL", "gemini-2.0-flash"))
    fallback_model: str = field(default_factory=lambda: os.getenv("SPLUNK_AI_FALLBACK_MODEL", "gemini-2.0-flash"))
    temperature: float = field(default_factory=lambda: float(os.getenv("SPLUNK_AI_TEMPERATURE", "0.7")))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("SPLUNK_AI_MAX_TOKENS", "4096")))
    timeout: int = field(default_factory=lambda: int(os.getenv("SPLUNK_AI_TIMEOUT", "30")))

    # Google ADK specific settings
    use_vertex_ai: bool = field(default_factory=lambda: os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true")
    google_api_key: str | None = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY"))
    google_cloud_project: str | None = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_PROJECT"))
    google_cloud_location: str = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))


@dataclass
class DiscoveryConfig:
    """Configuration for agent and tool discovery."""
    contrib_agents_paths: list[str] = field(default_factory=lambda: [
        "src/splunk_ai_sidekick/contrib/agents",
        "src/splunk_ai_sidekick/agents"
    ])
    contrib_tools_paths: list[str] = field(default_factory=lambda: [
        "src/splunk_ai_sidekick/contrib/tools",
        "src/splunk_ai_sidekick/tools"
    ])
    auto_discover: bool = True
    discovery_patterns: list[str] = field(default_factory=lambda: [
        "agent.py",
        "tool.py",
        "*_agent.py",
        "*_tool.py"
    ])


@dataclass
class SplunkConfig:
    """Splunk-specific configuration."""
    host: str = field(default_factory=lambda: os.getenv("SPLUNK_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("SPLUNK_PORT", "8089")))
    username: str = field(default_factory=lambda: os.getenv("SPLUNK_USERNAME", "admin"))
    password: str = field(default_factory=lambda: os.getenv("SPLUNK_PASSWORD", "Chang3d!"))
    app_context: str = field(default_factory=lambda: os.getenv("SPLUNK_APP_CONTEXT", "search"))
    enable_ssl: bool = field(default_factory=lambda: os.getenv("SPLUNK_ENABLE_SSL", "true").lower() == "true")
    verify_ssl: bool = field(default_factory=lambda: os.getenv("SPLUNK_VERIFY_SSL", "false").lower() == "true")
    mcp_server_url: str = field(default_factory=lambda: os.getenv("SPLUNK_MCP_SERVER_URL", "http://localhost:8003/mcp/"))


@dataclass
class Config:
    """
    Main configuration class for Splunk AI Sidekick.

    This class manages all configuration aspects of the framework including
    model settings, discovery paths, Splunk connection details, and runtime parameters.
    All configuration values can be overridden via environment variables.
    """

    # Core configurations
    model: ModelConfig = field(default_factory=ModelConfig)
    discovery: DiscoveryConfig = field(default_factory=DiscoveryConfig)
    splunk: SplunkConfig = field(default_factory=SplunkConfig)

    # Framework settings
    project_root: Path = field(default_factory=Path.cwd)
    debug_mode: bool = field(default_factory=lambda: os.getenv("SPLUNK_AI_DEBUG", "false").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper())
    max_concurrent_agents: int = field(default_factory=lambda: int(os.getenv("SPLUNK_AI_MAX_CONCURRENT_AGENTS", "5")))
    session_timeout: int = field(default_factory=lambda: int(os.getenv("SPLUNK_AI_SESSION_TIMEOUT", "3600")))  # 1 hour

    # Parallel execution settings for Guided Agent Flows
    max_parallel_tasks: int = field(default_factory=lambda: int(os.getenv("SPLUNK_AI_MAX_PARALLEL_TASKS", "4")))
    task_timeout_default: int = field(default_factory=lambda: int(os.getenv("SPLUNK_AI_TASK_TIMEOUT", "300")))  # 5 minutes
    micro_agent_timeout: int = field(default_factory=lambda: int(os.getenv("SPLUNK_AI_MICRO_AGENT_TIMEOUT", "180")))  # 3 minutes

    # Custom extensions
    custom_settings: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize configuration after creation."""
        # Load environment variables from .env file first
        self._load_dotenv()

        # Ensure project_root is a Path object
        if not isinstance(self.project_root, Path):
            self.project_root = Path(self.project_root)

        # Re-load and validate environment variables
        self._validate_and_load_environment()

        # Set up logging
        self._configure_logging()

    def _load_dotenv(self) -> None:
        """Load environment variables from .env file."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            logger.debug("✅ Environment variables loaded from .env file")

            # Reload SplunkConfig fields after .env is loaded
            self.splunk = SplunkConfig()
        except ImportError:
            logger.debug("⚠️ python-dotenv not available, relying on system environment variables")

    def _validate_and_load_environment(self) -> None:
        """Validate and load configuration from environment variables."""
        try:
            # Validate numeric values
            if temp_str := os.getenv("SPLUNK_AI_TEMPERATURE"):
                temp = float(temp_str)
                if not 0 <= temp <= 2:
                    logger.warning(f"Temperature {temp} out of range [0,2], using default")
                else:
                    self.model.temperature = temp

            if tokens_str := os.getenv("SPLUNK_AI_MAX_TOKENS"):
                tokens = int(tokens_str)
                if tokens <= 0:
                    logger.warning(f"Max tokens {tokens} must be positive, using default")
                else:
                    self.model.max_tokens = tokens

            if timeout_str := os.getenv("SPLUNK_AI_TIMEOUT"):
                timeout = int(timeout_str)
                if timeout <= 0:
                    logger.warning(f"Timeout {timeout} must be positive, using default")
                else:
                    self.model.timeout = timeout

            # Validate Splunk port
            if port_str := os.getenv("SPLUNK_PORT"):
                port = int(port_str)
                if not 1 <= port <= 65535:
                    logger.warning(f"Splunk port {port} out of range [1,65535], using default")
                else:
                    self.splunk.port = port

            # Validate concurrent agents
            if agents_str := os.getenv("SPLUNK_AI_MAX_CONCURRENT_AGENTS"):
                agents = int(agents_str)
                if agents <= 0:
                    logger.warning(f"Max concurrent agents {agents} must be positive, using default")
                else:
                    self.max_concurrent_agents = agents

            # Validate session timeout
            if timeout_str := os.getenv("SPLUNK_AI_SESSION_TIMEOUT"):
                timeout = int(timeout_str)
                if timeout <= 0:
                    logger.warning(f"Session timeout {timeout} must be positive, using default")
                else:
                    self.session_timeout = timeout

        except (ValueError, TypeError) as e:
            logger.warning(f"Error parsing environment variable: {e}")

        # Validate Google ADK configuration
        self._validate_google_adk_config()

    def _validate_google_adk_config(self) -> None:
        """Validate Google ADK specific configuration."""
        if self.model.use_vertex_ai:
            if not self.model.google_cloud_project:
                logger.warning(
                    "GOOGLE_GENAI_USE_VERTEXAI is true but GOOGLE_CLOUD_PROJECT is not set. "
                    "This may cause authentication issues."
                )
            if not self.model.google_cloud_location:
                logger.warning(
                    "GOOGLE_CLOUD_LOCATION is not set, using default: us-central1"
                )
        else:
            if not self.model.google_api_key:
                logger.warning(
                    "GOOGLE_GENAI_USE_VERTEXAI is false but GOOGLE_API_KEY is not set. "
                    "This may cause authentication issues with Google AI Studio."
                )

    def _load_from_environment(self) -> None:
        """
        Legacy method for backward compatibility.

        Note: Environment variables are now loaded in field default_factory functions
        and validated in _validate_and_load_environment().
        """
        logger.debug("Environment variables are loaded automatically via field defaults")

    def _configure_logging(self) -> None:
        """Configure logging based on current settings."""
        logging.basicConfig(
            level=getattr(logging, self.log_level, logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        if self.debug_mode:
            logger.setLevel(logging.DEBUG)

    def get_contrib_paths(self) -> dict[str, list[Path]]:
        """
        Get resolved contrib paths for agents and tools.

        Returns:
            Dictionary with 'agents' and 'tools' keys containing resolved paths
        """
        result = {
            'agents': [],
            'tools': []
        }

        # Resolve agent paths
        for path_str in self.discovery.contrib_agents_paths:
            path = self.project_root / path_str
            if path.exists():
                result['agents'].append(path)
            else:
                logger.debug(f"Agent path does not exist: {path}")

        # Resolve tool paths
        for path_str in self.discovery.contrib_tools_paths:
            path = self.project_root / path_str
            if path.exists():
                result['tools'].append(path)
            else:
                logger.debug(f"Tool path does not exist: {path}")

        return result

    def get_google_adk_env_vars(self) -> dict[str, str]:
        """
        Get environment variables needed for Google ADK.

        Returns:
            Dictionary of environment variables for ADK configuration
        """
        env_vars = {}

        if self.model.use_vertex_ai:
            env_vars["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
            if self.model.google_cloud_project:
                env_vars["GOOGLE_CLOUD_PROJECT"] = self.model.google_cloud_project
            if self.model.google_cloud_location:
                env_vars["GOOGLE_CLOUD_LOCATION"] = self.model.google_cloud_location
        else:
            env_vars["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
            if self.model.google_api_key:
                env_vars["GOOGLE_API_KEY"] = self.model.google_api_key

        return env_vars

    def validate(self) -> list[str]:
        """
        Validate the configuration and return any errors.

        Returns:
            List of validation error messages
        """
        errors = []

        # Validate model configuration
        if not self.model.primary_model:
            errors.append("Primary model must be specified")
        if not 0 <= self.model.temperature <= 2:
            errors.append("Temperature must be between 0 and 2")
        if self.model.max_tokens <= 0:
            errors.append("Max tokens must be positive")

        # Validate Google ADK configuration
        if self.model.use_vertex_ai:
            if not self.model.google_cloud_project:
                errors.append("Google Cloud Project must be specified when using Vertex AI")
        else:
            if not self.model.google_api_key:
                errors.append("Google API Key must be specified when not using Vertex AI")

        # Validate paths
        if not self.project_root.exists():
            errors.append(f"Project root does not exist: {self.project_root}")

        # Validate Splunk configuration
        if not self.splunk.host:
            errors.append("Splunk host must be specified")
        if not 1 <= self.splunk.port <= 65535:
            errors.append("Splunk port must be between 1 and 65535")

        return errors

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to dictionary format.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            'model': {
                'primary_model': self.model.primary_model,
                'fallback_model': self.model.fallback_model,
                'temperature': self.model.temperature,
                'max_tokens': self.model.max_tokens,
                'timeout': self.model.timeout,
                'use_vertex_ai': self.model.use_vertex_ai,
                'google_cloud_project': self.model.google_cloud_project,
                'google_cloud_location': self.model.google_cloud_location,
                # Note: API key is excluded for security
            },
            'discovery': {
                'contrib_agents_paths': self.discovery.contrib_agents_paths,
                'contrib_tools_paths': self.discovery.contrib_tools_paths,
                'auto_discover': self.discovery.auto_discover,
                'discovery_patterns': self.discovery.discovery_patterns,
            },
            'splunk': {
                'host': self.splunk.host,
                'port': self.splunk.port,
                'username': self.splunk.username,
                'app_context': self.splunk.app_context,
                'enable_ssl': self.splunk.enable_ssl,
                'verify_ssl': self.splunk.verify_ssl,
                'mcp_server_url': self.splunk.mcp_server_url,
                # Note: password is excluded for security
            },
            'framework': {
                'project_root': str(self.project_root),
                'debug_mode': self.debug_mode,
                'log_level': self.log_level,
                'max_concurrent_agents': self.max_concurrent_agents,
                'session_timeout': self.session_timeout,
            },
            'custom': self.custom_settings
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Config':
        """
        Create configuration from dictionary.

        Args:
            data: Dictionary containing configuration data

        Returns:
            Config instance
        """
        config = cls()

        # Update model config
        if model_data := data.get('model'):
            for key, value in model_data.items():
                if hasattr(config.model, key):
                    setattr(config.model, key, value)

        # Update discovery config
        if discovery_data := data.get('discovery'):
            for key, value in discovery_data.items():
                if hasattr(config.discovery, key):
                    setattr(config.discovery, key, value)

        # Update splunk config
        if splunk_data := data.get('splunk'):
            for key, value in splunk_data.items():
                if hasattr(config.splunk, key):
                    setattr(config.splunk, key, value)

        # Update framework settings
        if framework_data := data.get('framework'):
            for key, value in framework_data.items():
                if hasattr(config, key):
                    if key == 'project_root':
                        setattr(config, key, Path(value))
                    else:
                        setattr(config, key, value)

        # Update custom settings
        if custom_data := data.get('custom'):
            config.custom_settings.update(custom_data)

        return config

    def __repr__(self) -> str:
        """String representation of the configuration."""
        auth_method = "Vertex AI" if self.model.use_vertex_ai else "API Key"
        return (
            f"Config("
            f"model='{self.model.primary_model}', "
            f"auth='{auth_method}', "
            f"splunk='{self.splunk.host}:{self.splunk.port}', "
            f"debug={self.debug_mode})"
        )
