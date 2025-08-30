"""
Enhanced Discovery system for AI Sidekick for Splunk components.

This module provides functionality to automatically discover and register
agents and tools from various directories, supporting both core and contrib
components with proper ADK-style tool-to-sub-agent mapping.
"""

import importlib
import logging
import pkgutil
from typing import Any

from .base_agent import AgentMetadata, BaseAgent
from .base_tool import BaseTool, ToolMetadata
from .config import Config
from .registry import RegistryManager

logger = logging.getLogger(__name__)


class AgentToolMapping:
    """Tracks the association between agents and their tools."""

    def __init__(self):
        self.agent_tools: dict[str, list[str]] = {}  # agent_name -> list of tool names
        self.tool_agents: dict[str, str] = {}  # tool_name -> agent_name

    def associate_tool_with_agent(self, agent_name: str, tool_name: str) -> None:
        """Associate a tool with an agent."""
        if agent_name not in self.agent_tools:
            self.agent_tools[agent_name] = []

        if tool_name not in self.agent_tools[agent_name]:
            self.agent_tools[agent_name].append(tool_name)

        self.tool_agents[tool_name] = agent_name

    def get_agent_tools(self, agent_name: str) -> list[str]:
        """Get all tools associated with an agent."""
        return self.agent_tools.get(agent_name, [])

    def get_tool_agent(self, tool_name: str) -> str | None:
        """Get the agent associated with a tool."""
        return self.tool_agents.get(tool_name)

    def get_all_agent_tool_mappings(self) -> dict[str, list[str]]:
        """Get all agent-to-tools mappings."""
        return self.agent_tools.copy()


class ADKAgentWrapper(BaseAgent):
    """Enhanced wrapper for ADK Agent instances with tool association support."""

    def __init__(self, config: Config, metadata: AgentMetadata, adk_agent: Any = None,
                 tools: list[Any] | None = None, session_state: dict[str, Any] | None = None):
        self.config = config
        self._metadata = metadata
        self.adk_agent = adk_agent
        self.associated_tools = tools or []
        self.session_state = session_state or {}

    @property
    def metadata(self) -> AgentMetadata:
        return self._metadata

    @property
    def instructions(self) -> str:
        return getattr(self.adk_agent, 'instruction', "ADK agent wrapper")

    def get_adk_agent(self, tools: list[Any] | None = None) -> Any:
        """Get the wrapped ADK agent instance.

        Args:
            tools: Optional list of tools (ignored for wrapped agents)

        Returns:
            The wrapped ADK agent instance
        """
        return self.adk_agent

    def get_associated_tools(self) -> list[Any]:
        """Get tools associated with this agent."""
        return self.associated_tools


class ADKToolWrapper(BaseTool):
    """Wrapper for ADK Tool instances to integrate with our registry system."""

    def __init__(self, config: Config, metadata: ToolMetadata, adk_tool: Any = None):
        self.config = config
        self._metadata = metadata
        self.adk_tool = adk_tool

    @property
    def metadata(self) -> ToolMetadata:
        return self._metadata

    @property
    def schema(self) -> dict[str, Any]:
        # ADK tools have their own schema handling
        return {
            "type": "function",
            "function": {
                "name": self.metadata.name,
                "description": self.metadata.description
            }
        }

    async def execute(self, **kwargs) -> dict[str, Any]:
        """Execute the wrapped ADK tool."""
        try:
            # ADK tools are callable
            if hasattr(self.adk_tool, '__call__'):
                result = self.adk_tool(**kwargs)
                return {"result": result, "success": True}
            else:
                return {"error": "ADK tool is not callable", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    def get_adk_tool(self) -> Any:
        """Get the wrapped ADK tool instance."""
        return self.adk_tool


class ComponentDiscovery:
    """Enhanced discovery system for agents and tools with ADK-style tool-to-sub-agent mapping."""

    def __init__(self, registry_manager: RegistryManager, config: Config):
        """Initialize the enhanced discovery system.

        Args:
            registry_manager: The registry manager for registering components
            config: Configuration object for the system
        """
        self.registry_manager = registry_manager
        self.config = config
        self.agent_tool_mapping = AgentToolMapping()

    def discover_all(self, agent_paths: list[str], tool_paths: list[str]) -> dict[str, int]:
        """Discover and register all components with tool-to-agent mapping.

        Args:
            agent_paths: List of paths to search for agents
            tool_paths: List of paths to search for tools (legacy - tools should be with agents)

        Returns:
            Dictionary with discovery counts
        """
        logger.info("Starting enhanced component discovery...")

        # First pass: Discover agents and their associated tools
        agent_count = 0
        tool_count = 0

        for path in agent_paths:
            try:
                counts = self.discover_agents_with_tools_in_path(path)
                agent_count += counts['agents']
                tool_count += counts['tools']
                logger.info(f"Discovered {counts['agents']} agents and {counts['tools']} tools in {path}")
            except Exception as e:
                logger.error(f"Error discovering agents with tools in {path}: {e}")

        # Second pass: Discover standalone tools (legacy support)
        for path in tool_paths:
            try:
                count = self.discover_standalone_tools_in_path(path)
                tool_count += count
                logger.info(f"Discovered {count} standalone tools in {path}")
            except Exception as e:
                logger.error(f"Error discovering standalone tools in {path}: {e}")

        logger.info(f"Enhanced discovery complete: {agent_count} agents, {tool_count} tools")
        logger.info(f"Agent-tool mappings: {self.agent_tool_mapping.get_all_agent_tool_mappings()}")

        return {'agents': agent_count, 'tools': tool_count}

    def discover_agents_with_tools_in_path(self, path: str) -> dict[str, int]:
        """Discover agents and their associated tools in a specific path.

        Args:
            path: Module path to search for agents (e.g., 'my.module.agents')

        Returns:
            Dictionary with counts of agents and tools discovered
        """
        agent_count = 0
        tool_count = 0

        try:
            # Convert path to module notation if needed
            if path.startswith('src/'):
                module_path = path.replace('src/', '').replace('/', '.')
            else:
                module_path = path.replace('/', '.')

            # Try to import the base module
            try:
                base_module = importlib.import_module(module_path)
            except ImportError as e:
                logger.warning(f"Could not import agent module {module_path}: {e}")
                return {'agents': 0, 'tools': 0}

            # First, check the base module itself for agents
            registered_agents = self._register_agents_from_module(base_module, module_path)
            agent_count += len(registered_agents)

            # Then look for agent subdirectories following ADK patterns
            if hasattr(base_module, '__path__'):
                for finder, name, ispkg in pkgutil.iter_modules(base_module.__path__, f"{module_path}."):
                    if ispkg:
                        counts = self._discover_agent_package_with_tools(name)
                        agent_count += counts['agents']
                        tool_count += counts['tools']

        except Exception as e:
            logger.error(f"Error discovering agents with tools in {path}: {e}")

        return {'agents': agent_count, 'tools': tool_count}

    def _discover_agent_package_with_tools(self, package_name: str) -> dict[str, int]:
        """Discover an agent and its tools in a specific package following ADK patterns.

        Args:
            package_name: Full package name to inspect

        Returns:
            Dictionary with counts of agents and tools discovered
        """
        agent_count = 0
        tool_count = 0

        try:
            # Try to import the package
            package = importlib.import_module(package_name)

            # Look for standard agent module
            agent_module = None
            try:
                agent_module = importlib.import_module(f"{package_name}.agent")
            except ImportError:
                # Try looking for __init__ with agent exports
                agent_module = package

            if agent_module:
                # Discover agent(s) in the module
                agent_names = self._register_agents_from_module(agent_module, package_name)
                agent_count += len(agent_names)

                # For each discovered agent, look for associated tools
                for agent_name in agent_names:
                    # Look for tools in the same package
                    agent_tools = self._discover_tools_for_agent(package_name, agent_name)
                    tool_count += len(agent_tools)

        except Exception as e:
            logger.debug(f"Could not discover agent package {package_name}: {e}")

        return {'agents': agent_count, 'tools': tool_count}

    def _discover_tools_for_agent(self, package_name: str, agent_name: str) -> list[str]:
        """Discover tools associated with a specific agent.

        Args:
            package_name: Package name containing the agent
            agent_name: Name of the agent

        Returns:
            List of tool names discovered for the agent
        """
        discovered_tools = []

        try:
            # Look for tools directory within the agent package
            tools_module_path = f"{package_name}.tools"
            try:
                tools_module = importlib.import_module(tools_module_path)

                # Register tools from the tools module
                tool_names = self._register_tools_from_module_for_agent(
                    tools_module, tools_module_path, agent_name
                )
                discovered_tools.extend(tool_names)

                # Look for individual tool files
                if hasattr(tools_module, '__path__'):
                    for finder, name, ispkg in pkgutil.iter_modules(tools_module.__path__, f"{tools_module_path}."):
                        if not ispkg and not name.endswith('__init__'):
                            try:
                                tool_module = importlib.import_module(name)
                                tool_names = self._register_tools_from_module_for_agent(
                                    tool_module, name, agent_name
                                )
                                discovered_tools.extend(tool_names)
                            except Exception as e:
                                logger.debug(f"Could not import tool module {name}: {e}")

            except ImportError:
                logger.debug(f"No tools directory found for agent {agent_name} in {package_name}")

        except Exception as e:
            logger.error(f"Error discovering tools for agent {agent_name}: {e}")

        return discovered_tools

    def _register_agents_from_module(self, module: Any, package_name: str) -> list[str]:
        """Register agents found in a module.

        Args:
            module: The module to inspect
            package_name: Name of the package for logging

        Returns:
            List of agent names registered
        """
        registered_agents = []

        # Look for agent instances or classes
        for attr_name in dir(module):
            if attr_name.startswith('_'):
                continue

            attr = getattr(module, attr_name)

            # Check if it's an ADK Agent instance
            if self._is_adk_agent(attr):
                try:
                    # Create metadata for ADK agent
                    metadata = AgentMetadata(
                        name=getattr(attr, 'name', attr_name),
                        description=getattr(attr, 'description', f"Agent from {package_name}"),
                        version="1.0.0",
                        author="Auto-discovered",
                        tags=[package_name.split('.')[-1]],
                        dependencies=[]
                    )

                    # Create wrapper class for ADK agent
                    def create_agent_wrapper(agent_instance, agent_metadata):
                        class SpecificADKAgentWrapper(ADKAgentWrapper):
                            def __init__(self, config: Config, metadata: AgentMetadata, tools: list[Any] | None = None, session_state: dict[str, Any] | None = None):
                                super().__init__(config, metadata, agent_instance, tools, session_state)
                        return SpecificADKAgentWrapper

                    wrapper_class = create_agent_wrapper(attr, metadata)

                    # Register the wrapper class
                    self.registry_manager.agent_registry.register(
                        name=metadata.name,
                        cls=wrapper_class,
                        metadata=metadata
                    )
                    logger.info(f"Registered ADK agent: {metadata.name}")
                    registered_agents.append(metadata.name)

                except Exception as e:
                    logger.error(f"Error registering ADK agent {attr_name}: {e}")

            # Check if it's a BaseAgent subclass
            elif isinstance(attr, type) and issubclass(attr, BaseAgent) and attr != BaseAgent:
                try:
                    # Get metadata from the class attributes instead of instantiating
                    metadata_attr = getattr(attr, 'METADATA', None)
                    if metadata_attr and isinstance(metadata_attr, AgentMetadata):
                        self.registry_manager.agent_registry.register(
                            name=metadata_attr.name,
                            cls=attr,
                            metadata=metadata_attr
                        )
                        logger.info(f"Registered BaseAgent: {metadata_attr.name}")
                        registered_agents.append(metadata_attr.name)

                        # Associate any built-in tools with this agent
                        if hasattr(attr, 'get_adk_agent'):
                            try:
                                # Create instance to check for tools
                                instance = attr(self.config, metadata_attr)
                                get_adk_agent_method = getattr(instance, 'get_adk_agent', None)
                                if get_adk_agent_method and callable(get_adk_agent_method):
                                    adk_agent = get_adk_agent_method()
                                    if adk_agent and hasattr(adk_agent, 'tools') and adk_agent.tools:
                                        for tool in adk_agent.tools:
                                            tool_name = getattr(tool, 'name', 'unknown_tool')
                                            self.agent_tool_mapping.associate_tool_with_agent(
                                                metadata_attr.name, tool_name
                                            )
                                            logger.debug(f"Associated tool {tool_name} with agent {metadata_attr.name}")
                            except Exception as e:
                                logger.debug(f"Could not check tools for agent {metadata_attr.name}: {e}")
                    else:
                        logger.debug(f"Skipping BaseAgent class {attr_name} - no valid METADATA attribute")
                except Exception as e:
                    logger.error(f"Error registering agent class {attr_name}: {e}")

            # Check if it's a BaseAgent instance
            elif isinstance(attr, BaseAgent):
                try:
                    # Use the instance's metadata
                    if hasattr(attr, 'metadata') and isinstance(attr.metadata, AgentMetadata):
                        self.registry_manager.agent_registry.register(
                            name=attr.metadata.name,
                            cls=type(attr),
                            metadata=attr.metadata,
                            overwrite=True  # Allow instances to override class registrations
                        )

                        # Set the instance in the registry entry to avoid re-creation
                        entry = self.registry_manager.agent_registry.get(attr.metadata.name)
                        if entry:
                            entry.instance = attr
                            logger.debug(f"Set instance for {attr.metadata.name} in registry")

                        logger.info(f"Registered BaseAgent instance: {attr.metadata.name}")
                        registered_agents.append(attr.metadata.name)

                        # Associate any built-in tools with this agent
                        try:
                            # Check if the instance has ADK agent capabilities with tools
                            get_adk_agent_method = getattr(attr, 'get_adk_agent', None)
                            if get_adk_agent_method and callable(get_adk_agent_method):
                                adk_agent = get_adk_agent_method()
                                if adk_agent and hasattr(adk_agent, 'tools') and adk_agent.tools:
                                    for tool in adk_agent.tools:
                                        tool_name = getattr(tool, 'name', 'unknown_tool')
                                        self.agent_tool_mapping.associate_tool_with_agent(
                                            attr.metadata.name, tool_name
                                        )
                                        logger.debug(f"Associated tool {tool_name} with agent {attr.metadata.name}")
                        except Exception as e:
                            logger.debug(f"Could not check tools for agent instance {attr.metadata.name}: {e}")
                    else:
                        logger.debug(f"Skipping BaseAgent instance {attr_name} - no valid metadata attribute")
                except Exception as e:
                    logger.error(f"Error registering agent instance {attr_name}: {e}")

        return registered_agents

    def _is_adk_agent(self, obj: Any) -> bool:
        """Check if an object is an ADK Agent instance.

        Args:
            obj: Object to check

        Returns:
            True if it's an ADK Agent instance
        """
        try:
            # Import all ADK Agent classes to check isinstance
            from google.adk.agents import Agent, LlmAgent, LoopAgent
            from google.adk.agents.base_agent import BaseAgent as ADKBaseAgent

            # Check if it's any type of ADK agent
            return isinstance(obj, Agent | LlmAgent | LoopAgent | ADKBaseAgent)
        except ImportError:
            # ADK not available, check by duck typing
            return (hasattr(obj, 'name') and
                   hasattr(obj, 'description') and
                   hasattr(obj, 'instruction'))

    def _register_tools_from_module(self, module: Any, module_name: str) -> int:
        """Register tools found in a module.

        Args:
            module: The module to inspect
            module_name: Name of the module for logging

        Returns:
            Number of tools registered
        """
        count = 0

        # Look for tool instances or classes
        for attr_name in dir(module):
            if attr_name.startswith('_'):
                continue

            attr = getattr(module, attr_name)

            # Check if it's an ADK tool instance
            if self._is_adk_tool(attr):
                try:
                    # Create metadata for ADK tool
                    metadata = ToolMetadata(
                        name=getattr(attr, 'name', attr_name),
                        description=getattr(attr, 'description', f"Tool from {module_name}"),
                        version="1.0.0",
                        author="Auto-discovered",
                        tags=[module_name.split('.')[-1]],
                        parameters={}  # ADK tools handle their own schemas
                    )

                    # Create wrapper class for ADK tool
                    def create_tool_wrapper(tool_instance, tool_metadata):
                        class SpecificADKToolWrapper(ADKToolWrapper):
                            def __init__(self, config: Config, metadata: ToolMetadata):
                                super().__init__(config, metadata, tool_instance)
                        return SpecificADKToolWrapper

                    wrapper_class = create_tool_wrapper(attr, metadata)

                    # Register the wrapper class
                    self.registry_manager.tool_registry.register(
                        name=metadata.name,
                        cls=wrapper_class,
                        metadata=metadata
                    )
                    logger.info(f"Registered ADK tool: {metadata.name}")
                    count += 1

                except Exception as e:
                    logger.error(f"Error registering ADK tool {attr_name}: {e}")

            # Check if it's a BaseTool subclass
            elif isinstance(attr, type) and issubclass(attr, BaseTool) and attr != BaseTool:
                try:
                    # Get metadata from the class attributes instead of instantiating
                    metadata_attr = getattr(attr, 'METADATA', None)
                    if metadata_attr and isinstance(metadata_attr, ToolMetadata):
                        self.registry_manager.tool_registry.register(
                            name=metadata_attr.name,
                            cls=attr,
                            metadata=metadata_attr
                        )
                        logger.info(f"Registered BaseTool: {metadata_attr.name}")
                        count += 1
                    else:
                        logger.debug(f"Skipping BaseTool class {attr_name} - no valid METADATA attribute")
                except Exception as e:
                    logger.error(f"Error registering tool class {attr_name}: {e}")

        return count

    def _is_adk_tool(self, obj: Any) -> bool:
        """Check if an object is an ADK tool instance.

        Args:
            obj: Object to check

        Returns:
            True if it's an ADK tool instance
        """
        try:
            # Import ADK tool classes to check isinstance
            from google.adk.tools.agent_tool import AgentTool
            from google.adk.tools.google_search_tool import google_search

            return (isinstance(obj, AgentTool) or
                   obj is google_search or
                   (hasattr(obj, '__class__') and
                    obj.__class__.__module__.startswith('google.adk.tools')))
        except ImportError:
            # ADK not available, check by duck typing
            return (hasattr(obj, '__call__') and
                   hasattr(obj, 'name') if hasattr(obj, 'name') else False)

    def _register_tools_from_module_for_agent(self, module: Any, module_name: str, agent_name: str) -> list[str]:
        """Register tools found in a module for a specific agent.

        Args:
            module: The module to inspect
            module_name: Name of the module for logging
            agent_name: Name of the agent

        Returns:
            List of tool names registered for the agent
        """
        discovered_tools = []

        # Look for tool instances or classes
        for attr_name in dir(module):
            if attr_name.startswith('_'):
                continue

            attr = getattr(module, attr_name)

            # Check if it's an ADK tool instance
            if self._is_adk_tool(attr):
                try:
                    # Create metadata for ADK tool
                    metadata = ToolMetadata(
                        name=getattr(attr, 'name', attr_name),
                        description=getattr(attr, 'description', f"Tool from {module_name}"),
                        version="1.0.0",
                        author="Auto-discovered",
                        tags=[module_name.split('.')[-1]],
                        parameters={}  # ADK tools handle their own schemas
                    )

                    # Create wrapper class for ADK tool
                    def create_tool_wrapper(tool_instance, tool_metadata):
                        class SpecificADKToolWrapper(ADKToolWrapper):
                            def __init__(self, config: Config, metadata: ToolMetadata):
                                super().__init__(config, metadata, tool_instance)
                        return SpecificADKToolWrapper

                    wrapper_class = create_tool_wrapper(attr, metadata)

                    # Register the wrapper class
                    self.registry_manager.tool_registry.register(
                        name=metadata.name,
                        cls=wrapper_class,
                        metadata=metadata
                    )
                    logger.info(f"Registered ADK tool: {metadata.name}")
                    discovered_tools.append(metadata.name)

                    # Associate the tool with the agent
                    self.agent_tool_mapping.associate_tool_with_agent(agent_name, metadata.name)
                    logger.debug(f"Associated tool {metadata.name} with agent {agent_name}")

                except Exception as e:
                    logger.error(f"Error registering ADK tool {attr_name}: {e}")

            # Check if it's a BaseTool subclass
            elif isinstance(attr, type) and issubclass(attr, BaseTool) and attr != BaseTool:
                try:
                    # Get metadata from the class attributes instead of instantiating
                    metadata_attr = getattr(attr, 'METADATA', None)
                    if metadata_attr and isinstance(metadata_attr, ToolMetadata):
                        self.registry_manager.tool_registry.register(
                            name=metadata_attr.name,
                            cls=attr,
                            metadata=metadata_attr
                        )
                        logger.info(f"Registered BaseTool: {metadata_attr.name}")
                        discovered_tools.append(metadata_attr.name)

                        # Associate the tool with the agent
                        self.agent_tool_mapping.associate_tool_with_agent(agent_name, metadata_attr.name)
                        logger.debug(f"Associated tool {metadata_attr.name} with agent {agent_name}")
                    else:
                        logger.debug(f"Skipping BaseTool class {attr_name} - no valid METADATA attribute")
                except Exception as e:
                    logger.error(f"Error registering tool class {attr_name}: {e}")

        return discovered_tools

    def discover_standalone_tools_in_path(self, path: str) -> int:
        """Discover standalone tools in a specific path.

        Args:
            path: Module path to search for tools (e.g., 'my.module.tools')

        Returns:
            Number of standalone tools discovered
        """
        count = 0

        try:
            # Convert path to module notation if needed
            if path.startswith('src/'):
                module_path = path.replace('src/', '').replace('/', '.')
            else:
                module_path = path.replace('/', '.')

            # Try to import the base module
            try:
                base_module = importlib.import_module(module_path)
            except ImportError as e:
                logger.warning(f"Could not import tool module {module_path}: {e}")
                return 0

            # Check for direct tool definitions in the module
            count += self._register_tools_from_module(base_module, module_path)

            # Look for tool files in subdirectories
            if hasattr(base_module, '__path__'):
                for finder, name, ispkg in pkgutil.iter_modules(base_module.__path__, f"{module_path}."):
                    if not ispkg and not name.endswith('__init__'):
                        try:
                            tool_module = importlib.import_module(name)
                            count += self._register_tools_from_module(tool_module, name)
                        except Exception as e:
                            logger.debug(f"Could not import tool module {name}: {e}")

        except Exception as e:
            logger.error(f"Error discovering standalone tools in {path}: {e}")

        return count

    def get_agent_tool_mapping(self) -> AgentToolMapping:
        """Get the agent-tool mapping for use by orchestrator."""
        return self.agent_tool_mapping

    def get_tools_for_agent(self, agent_name: str) -> list[str]:
        """Get all tools associated with a specific agent."""
        return self.agent_tool_mapping.get_agent_tools(agent_name)
