"""
Splunk Information Tool - A simple contrib tool example.

This tool provides basic Splunk environment information.
"""

import logging
from typing import Any

from splunk_ai_sidekick.core.base_tool import BaseTool, ToolMetadata

logger = logging.getLogger(__name__)


class SplunkInfoTool(BaseTool):
    """
    A simple tool that provides Splunk environment information.

    This is an example of a community-contributed tool.
    """

    # Class metadata for discovery system
    METADATA = ToolMetadata(
        name="splunk-info",
        description="Provides basic Splunk environment information",
        version="1.0.0",
        author="Community",
        tags=["info", "environment", "splunk"],
        parameters={
            "info_type": {
                "type": "string",
                "description": "Type of information to retrieve",
                "required": False,
                "default": "general"
            }
        }
    )

    def __init__(self, config: Any = None, metadata: ToolMetadata | None = None):
        """Initialize the Splunk Info Tool."""
        from splunk_ai_sidekick.core.config import Config

        if config is None:
            config = Config()

        if metadata is None:
            metadata = ToolMetadata(
                name="splunk-info",
                description="Provides basic Splunk environment information",
                version="1.0.0",
                author="Community",
                tags=["info", "environment", "splunk"],
                parameters={
                    "info_type": {
                        "type": "string",
                        "description": "Type of information to retrieve",
                        "required": False,
                        "default": "general"
                    }
                }
            )

        super().__init__(config, metadata)

    async def execute(self, info_type: str = "general", **kwargs) -> dict[str, Any]:
        """
        Execute the tool to get Splunk information.

        Args:
            info_type: Type of information to retrieve
            **kwargs: Additional parameters

        Returns:
            Dictionary containing the requested information
        """
        try:
            logger.info(f"SplunkInfoTool executing with info_type: {info_type}")

            if info_type == "general":
                return {
                    "success": True,
                    "data": {
                        "splunk_host": self.config.splunk.host,
                        "splunk_port": self.config.splunk.port,
                        "app_context": self.config.splunk.app_context,
                        "ssl_enabled": self.config.splunk.enable_ssl,
                        "framework_version": "1.0.0"
                    },
                    "message": "General Splunk environment information retrieved"
                }
            elif info_type == "config":
                return {
                    "success": True,
                    "data": {
                        "primary_model": self.config.model.primary_model,
                        "fallback_model": self.config.model.fallback_model,
                        "temperature": self.config.model.temperature,
                        "max_tokens": self.config.model.max_tokens,
                        "debug_mode": self.config.debug_mode
                    },
                    "message": "Framework configuration information retrieved"
                }
            elif info_type == "discovery":
                return {
                    "success": True,
                    "data": {
                        "agent_paths": self.config.discovery.contrib_agents_paths,
                        "tool_paths": self.config.discovery.contrib_tools_paths,
                        "patterns": self.config.discovery.discovery_patterns,
                        "auto_discover": self.config.discovery.auto_discover
                    },
                    "message": "Discovery configuration information retrieved"
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown info_type: {info_type}",
                    "message": "Valid info_types are: general, config, discovery"
                }

        except Exception as e:
            logger.error(f"SplunkInfoTool execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve Splunk information"
            }

    def validate_parameters(self, **kwargs) -> bool:
        """Validate tool parameters."""
        info_type = kwargs.get("info_type", "general")
        return isinstance(info_type, str) and info_type in ["general", "config", "discovery"]

    @property
    def schema(self) -> dict[str, Any]:
        """Get tool schema for validation."""
        return {
            "type": "object",
            "properties": {
                "info_type": {
                    "type": "string",
                    "enum": ["general", "config", "discovery"],
                    "default": "general",
                    "description": "Type of information to retrieve"
                }
            },
            "required": []
        }

    async def cleanup(self) -> None:
        """Cleanup tool resources."""
        logger.info("SplunkInfoTool cleanup completed")
        pass
