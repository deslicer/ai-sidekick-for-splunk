"""
Base tool class for Splunk AI Sidekick.

This module provides the foundational BaseTool class that all Splunk AI tools
should inherit from. It implements common functionality and enforces the
contract for tool implementations.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from .config import Config

logger = logging.getLogger(__name__)


@dataclass
class ToolMetadata:
    """Metadata for tool registration and discovery."""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "Unknown"
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    """
    Base class for all Splunk AI tools.

    This class provides the foundational structure and common functionality
    that all tools in the Splunk AI Sidekick framework should implement.
    It integrates with Google ADK's tool patterns while providing
    Splunk-specific abstractions.

    Attributes:
        config: Configuration instance for the tool
        metadata: Tool metadata for registration and discovery
        _is_initialized: Whether the tool has been initialized
    """

    def __init__(
        self,
        config: Config,
        metadata: ToolMetadata
    ):
        """
        Initialize the base tool.

        Args:
            config: Configuration instance
            metadata: Tool metadata
        """
        self.config = config
        self.metadata = metadata
        self._is_initialized = False

        logger.info(f"Initializing tool: {self.metadata.name}")

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool with the given parameters.

        This method must be implemented by all tool subclasses to define
        the tool's core functionality.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Tool execution result

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Tool subclasses must implement execute method")

    @property
    @abstractmethod
    def schema(self) -> dict[str, Any]:
        """
        Get the tool's parameter schema.

        This property must be implemented by all tool subclasses to define
        the expected parameters and their types for proper validation.

        Returns:
            Dictionary containing the parameter schema
        """
        raise NotImplementedError("Tool subclasses must implement schema property")

    def validate_parameters(self, parameters: dict[str, Any]) -> list[str]:
        """
        Validate parameters against the tool's schema.

        Args:
            parameters: Parameters to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        schema = self.schema

        # Check required parameters
        required_params = schema.get('required', [])
        for param in required_params:
            if param not in parameters:
                errors.append(f"Missing required parameter: {param}")

        # Check parameter types
        properties = schema.get('properties', {})
        for param_name, param_value in parameters.items():
            if param_name in properties:
                expected_type = properties[param_name].get('type')
                if expected_type and not self._validate_type(param_value, expected_type):
                    errors.append(f"Invalid type for parameter '{param_name}': expected {expected_type}")

        return errors

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """
        Validate a parameter value against its expected type.

        Args:
            value: Value to validate
            expected_type: Expected type string

        Returns:
            True if valid, False otherwise
        """
        type_mapping = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict
        }

        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is None:
            return True  # Unknown type, allow it

        return isinstance(value, expected_python_type)

    async def safe_execute(self, **kwargs) -> dict[str, Any]:
        """
        Safely execute the tool with parameter validation and error handling.

        Args:
            **kwargs: Tool parameters

        Returns:
            Dictionary with 'success', 'result', and optionally 'error' keys
        """
        try:
            # Validate parameters
            validation_errors = self.validate_parameters(kwargs)
            if validation_errors:
                return {
                    'success': False,
                    'error': f"Parameter validation failed: {'; '.join(validation_errors)}"
                }

            # Initialize if needed
            if not self._is_initialized:
                await self.initialize()

            # Execute the tool
            result = await self.execute(**kwargs)

            return {
                'success': True,
                'result': result
            }

        except Exception as e:
            logger.error(f"Error executing tool {self.metadata.name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def initialize(self) -> None:
        """
        Initialize the tool.

        This method can be overridden by subclasses for custom initialization logic.
        """
        if self._is_initialized:
            return

        logger.debug(f"Initializing tool: {self.metadata.name}")
        self._is_initialized = True

    async def cleanup(self) -> None:
        """
        Clean up tool resources.

        This method can be overridden by subclasses for custom cleanup logic.
        """
        logger.debug(f"Cleaning up tool: {self.metadata.name}")
        self._is_initialized = False

    def get_info(self) -> dict[str, Any]:
        """
        Get comprehensive tool information.

        Returns:
            Dictionary containing tool metadata and schema
        """
        return {
            'name': self.metadata.name,
            'description': self.metadata.description,
            'version': self.metadata.version,
            'author': self.metadata.author,
            'tags': self.metadata.tags,
            'dependencies': self.metadata.dependencies,
            'parameters': self.metadata.parameters,
            'schema': self.schema,
            'initialized': self._is_initialized
        }

    def __repr__(self) -> str:
        """String representation of the tool."""
        return (
            f"BaseTool(name='{self.metadata.name}', "
            f"version='{self.metadata.version}', "
            f"initialized={self._is_initialized})"
        )


class SplunkTool(BaseTool):
    """
    Specialized base class for Splunk-specific tools.

    This class extends BaseTool with Splunk connection and query capabilities.
    """

    def __init__(
        self,
        config: Config,
        metadata: ToolMetadata
    ):
        """
        Initialize the Splunk tool.

        Args:
            config: Configuration instance
            metadata: Tool metadata
        """
        super().__init__(config, metadata)
        self._splunk_client: Any | None = None

    async def get_splunk_client(self) -> Any | None:
        """
        Get or create a Splunk client instance.

        Returns:
            Splunk client instance
        """
        if self._splunk_client is None:
            await self._initialize_splunk_client()
        return self._splunk_client

    async def _initialize_splunk_client(self) -> None:
        """Initialize the Splunk client."""
        try:
            # This would import the actual Splunk SDK or client
            # For now, we'll use a placeholder
            logger.debug(f"Initializing Splunk client for tool: {self.metadata.name}")
            # self._splunk_client = SplunkClient(self.config.splunk)

        except Exception as e:
            logger.error(f"Failed to initialize Splunk client: {e}")
            raise

    async def execute_search(self, search_query: str, **kwargs) -> dict[str, Any]:
        """
        Execute a Splunk search query.

        Args:
            search_query: SPL search query
            **kwargs: Additional search parameters

        Returns:
            Search results
        """
        client = await self.get_splunk_client()
        if client is None:
            raise RuntimeError("Splunk client not available")

        logger.info(f"Executing Splunk search: {search_query}")
        # Implementation would depend on the Splunk client library
        # return await client.search(search_query, **kwargs)

        # Placeholder implementation
        return {
            'query': search_query,
            'results': [],
            'message': 'Placeholder implementation'
        }

    async def cleanup(self) -> None:
        """Clean up Splunk tool resources."""
        if self._splunk_client:
            try:
                # Close Splunk client connection
                # await self._splunk_client.close()
                self._splunk_client = None
            except Exception as e:
                logger.error(f"Error closing Splunk client: {e}")

        await super().cleanup()
