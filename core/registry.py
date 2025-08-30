"""
Registry system for AI Sidekick for Splunk agents and tools.

This module provides centralized registration and management of agents and tools
in the framework, supporting dynamic discovery and dependency resolution.
"""

import inspect
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .base_agent import AgentMetadata, BaseAgent
from .base_tool import BaseTool, ToolMetadata
from .config import Config

logger = logging.getLogger(__name__)


@dataclass
class RegistryEntry:
    """Base class for registry entries."""
    name: str
    cls: type
    metadata: AgentMetadata | ToolMetadata
    source_path: Path | None = None
    is_loaded: bool = False
    instance: Any | None = None


class BaseRegistry:
    """
    Base registry class for managing components.

    Provides common functionality for registering, discovering, and managing
    framework components (agents or tools).
    """

    def __init__(self, config: Config):
        """
        Initialize the registry.

        Args:
            config: Configuration instance
        """
        self.config = config
        self._entries: dict[str, RegistryEntry] = {}
        self._tags: dict[str, set[str]] = {}
        self._dependencies: dict[str, set[str]] = {}

    def register(
        self,
        name: str,
        cls: type,
        metadata: AgentMetadata | ToolMetadata,
        source_path: Path | None = None,
        overwrite: bool = False
    ) -> None:
        """
        Register a component in the registry.

        Args:
            name: Component name
            cls: Component class
            metadata: Component metadata
            source_path: Path to the source file
            overwrite: Whether to overwrite existing entries

        Raises:
            ValueError: If component already exists and overwrite is False
        """
        if name in self._entries and not overwrite:
            raise ValueError(f"Component '{name}' already registered. Use overwrite=True to replace.")

        entry = RegistryEntry(
            name=name,
            cls=cls,
            metadata=metadata,
            source_path=source_path
        )

        self._entries[name] = entry

        # Index by tags
        for tag in metadata.tags:
            if tag not in self._tags:
                self._tags[tag] = set()
            self._tags[tag].add(name)

        # Index dependencies
        if metadata.dependencies:
            self._dependencies[name] = set(metadata.dependencies)

        logger.info(f"Registered component: {name}")

    def unregister(self, name: str) -> bool:
        """
        Unregister a component from the registry.

        Args:
            name: Component name

        Returns:
            True if component was removed, False if not found
        """
        if name not in self._entries:
            return False

        entry = self._entries.pop(name)

        # Clean up tags
        for tag in entry.metadata.tags:
            if tag in self._tags:
                self._tags[tag].discard(name)
                if not self._tags[tag]:
                    del self._tags[tag]

        # Clean up dependencies
        if name in self._dependencies:
            del self._dependencies[name]

        # Clean up instance if loaded
        if entry.instance:
            try:
                if hasattr(entry.instance, 'cleanup'):
                    if inspect.iscoroutinefunction(entry.instance.cleanup):
                        import asyncio
                        asyncio.create_task(entry.instance.cleanup())
                    else:
                        entry.instance.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up component {name}: {e}")

        logger.info(f"Unregistered component: {name}")
        return True

    def get(self, name: str) -> RegistryEntry | None:
        """
        Get a registry entry by name.

        Args:
            name: Component name

        Returns:
            Registry entry or None if not found
        """
        return self._entries.get(name)

    def list_all(self) -> dict[str, RegistryEntry]:
        """
        Get all registered components.

        Returns:
            Dictionary of all registry entries
        """
        return self._entries.copy()

    def list_by_tag(self, tag: str) -> dict[str, RegistryEntry]:
        """
        Get components by tag.

        Args:
            tag: Tag to filter by

        Returns:
            Dictionary of matching registry entries
        """
        component_names = self._tags.get(tag, set())
        return {name: self._entries[name] for name in component_names if name in self._entries}

    def get_dependencies(self, name: str) -> set[str]:
        """
        Get dependencies for a component.

        Args:
            name: Component name

        Returns:
            Set of dependency names
        """
        return self._dependencies.get(name, set()).copy()

    def resolve_dependencies(self, name: str) -> list[str]:
        """
        Resolve dependencies in proper loading order.

        Args:
            name: Component name

        Returns:
            List of component names in dependency order

        Raises:
            ValueError: If circular dependencies are detected
        """
        resolved = []
        visited = set()
        visiting = set()

        def visit(component_name: str):
            if component_name in visiting:
                raise ValueError(f"Circular dependency detected involving: {component_name}")

            if component_name in visited:
                return

            visiting.add(component_name)

            # Visit dependencies first
            for dep in self.get_dependencies(component_name):
                if dep in self._entries:
                    visit(dep)

            visiting.remove(component_name)
            visited.add(component_name)
            resolved.append(component_name)

        visit(name)
        return resolved

    def get_info(self) -> dict[str, Any]:
        """
        Get registry information.

        Returns:
            Dictionary containing registry statistics
        """
        return {
            'total_components': len(self._entries),
            'tags': {tag: len(components) for tag, components in self._tags.items()},
            'components_with_dependencies': len(self._dependencies),
            'loaded_components': len([e for e in self._entries.values() if e.is_loaded])
        }


class AgentRegistry(BaseRegistry):
    """
    Registry for managing Splunk AI agents.

    Provides specialized functionality for agent registration, discovery,
    and instantiation within the framework.
    """

    def register(
        self,
        name: str,
        cls: type,
        metadata: AgentMetadata,
        source_path: Path | None = None,
        overwrite: bool = False
    ) -> None:
        """Override to ensure only AgentMetadata is accepted."""
        super().register(name, cls, metadata, source_path, overwrite)

    async def create_instance(
        self,
        name: str,
        session_state: dict[str, Any] | None = None,
        tools: list[Any] | None = None
    ) -> BaseAgent | None:
        """
        Create an instance of an agent.

        Args:
            name: Agent name
            session_state: Shared session state
            tools: Tools to provide to the agent

        Returns:
            Agent instance or None if not found

        Raises:
            RuntimeError: If agent creation fails
        """
        entry = self.get(name)
        if not entry:
            logger.error(f"Agent not found: {name}")
            return None

        try:
            # Create instance
            instance = entry.cls(
                config=self.config,
                metadata=entry.metadata,
                tools=tools,
                session_state=session_state
            )

            # Cache the instance
            entry.instance = instance
            entry.is_loaded = True

            logger.info(f"Created agent instance: {name}")
            return instance

        except Exception as e:
            logger.error(f"Failed to create agent instance {name}: {e}")
            raise RuntimeError(f"Agent creation failed: {e}")

    async def get_instance(
        self,
        name: str,
        session_state: dict[str, Any] | None = None,
        tools: list[Any] | None = None
    ) -> BaseAgent | None:
        """
        Get or create an agent instance.

        Args:
            name: Agent name
            session_state: Shared session state
            tools: Tools to provide to the agent

        Returns:
            Agent instance or None if not found
        """
        entry = self.get(name)
        if not entry:
            return None

        if entry.instance:
            return entry.instance

        return await self.create_instance(name, session_state, tools)

    def list_available_agents(self) -> dict[str, dict[str, Any]]:
        """
        List all available agents with their metadata.

        Returns:
            Dictionary of agent information
        """
        result = {}
        for name, entry in self._entries.items():
            result[name] = {
                'name': entry.metadata.name,
                'description': entry.metadata.description,
                'version': entry.metadata.version,
                'author': entry.metadata.author,
                'tags': entry.metadata.tags,
                'dependencies': entry.metadata.dependencies,
                'loaded': entry.is_loaded,
                'source_path': str(entry.source_path) if entry.source_path else None
            }
        return result


class ToolRegistry(BaseRegistry):
    """
    Registry for managing Splunk AI tools.

    Provides specialized functionality for tool registration, discovery,
    and instantiation within the framework.
    """

    def register(
        self,
        name: str,
        cls: type,
        metadata: 'ToolMetadata',
        source_path: Path | None = None,
        overwrite: bool = False
    ) -> None:
        """Override to ensure only ToolMetadata is accepted."""
        super().register(name, cls, metadata, source_path, overwrite)

    async def create_instance(self, name: str) -> BaseTool | None:
        """
        Create an instance of a tool.

        Args:
            name: Tool name

        Returns:
            Tool instance or None if not found

        Raises:
            RuntimeError: If tool creation fails
        """
        entry = self.get(name)
        if not entry:
            logger.error(f"Tool not found: {name}")
            return None

        try:
            # Create instance
            instance = entry.cls(
                config=self.config,
                metadata=entry.metadata
            )

            # Cache the instance
            entry.instance = instance
            entry.is_loaded = True

            logger.info(f"Created tool instance: {name}")
            return instance

        except Exception as e:
            logger.error(f"Failed to create tool instance {name}: {e}")
            raise RuntimeError(f"Tool creation failed: {e}")

    async def get_instance(self, name: str) -> BaseTool | None:
        """
        Get or create a tool instance.

        Args:
            name: Tool name

        Returns:
            Tool instance or None if not found
        """
        entry = self.get(name)
        if not entry:
            return None

        if entry.instance:
            return entry.instance

        return await self.create_instance(name)

    def list_available_tools(self) -> dict[str, dict[str, Any]]:
        """
        List all available tools with their metadata.

        Returns:
            Dictionary of tool information
        """
        result = {}
        for name, entry in self._entries.items():
            # Since this is ToolRegistry, metadata should be ToolMetadata
            metadata = entry.metadata
            if isinstance(metadata, ToolMetadata):
                result[name] = {
                    'name': metadata.name,
                    'description': metadata.description,
                    'version': metadata.version,
                    'author': metadata.author,
                    'tags': metadata.tags,
                    'dependencies': metadata.dependencies,
                    'parameters': metadata.parameters,
                    'loaded': entry.is_loaded,
                    'source_path': str(entry.source_path) if entry.source_path else None,
                    'schema': entry.cls.schema if hasattr(entry.cls, 'schema') else None
                }
            else:
                logger.warning(f"Non-tool metadata found in ToolRegistry for {name}")
        return result

    async def execute_tool(
        self,
        name: str,
        **kwargs
    ) -> dict[str, Any]:
        """
        Execute a tool by name.

        Args:
            name: Tool name
            **kwargs: Tool parameters

        Returns:
            Tool execution result
        """
        tool = await self.get_instance(name)
        if not tool:
            return {
                'success': False,
                'error': f"Tool not found: {name}"
            }

        return await tool.safe_execute(**kwargs)


class RegistryManager:
    """
    Manager for coordinating agent and tool registries.

    Provides a unified interface for managing both agents and tools
    within the AI Sidekick for Splunk framework.
    """

    def __init__(self, config: Config):
        """
        Initialize the registry manager.

        Args:
            config: Configuration instance
        """
        self.config = config
        self.agent_registry = AgentRegistry(config)
        self.tool_registry = ToolRegistry(config)

    def get_summary(self) -> dict[str, Any]:
        """
        Get a summary of all registries.

        Returns:
            Dictionary containing registry summaries
        """
        return {
            'agents': self.agent_registry.get_info(),
            'tools': self.tool_registry.get_info(),
            'total_components': (
                self.agent_registry.get_info()['total_components'] +
                self.tool_registry.get_info()['total_components']
            )
        }

    async def cleanup_all(self) -> None:
        """Clean up all registry instances."""
        # Get all entries from both registries
        agent_entries = self.agent_registry.list_all()
        tool_entries = self.tool_registry.list_all()

        # Clean up agent instances
        for entry in agent_entries.values():
            if entry.instance and hasattr(entry.instance, 'cleanup'):
                try:
                    await entry.instance.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up agent {entry.name}: {e}")

        # Clean up tool instances
        for entry in tool_entries.values():
            if entry.instance and hasattr(entry.instance, 'cleanup'):
                try:
                    await entry.instance.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up tool {entry.name}: {e}")

        logger.info("Registry cleanup completed")
