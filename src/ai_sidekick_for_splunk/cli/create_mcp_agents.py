import argparse
import asyncio
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    StdioServerParameters,
    StreamableHTTPConnectionParams,
)
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

logger = logging.getLogger(__name__)

# Default MCP prompt template for generated agents
DEFAULT_MCP_PROMPT = """
# Generic MCP Agent

You are an MCP tool executor and data analyst. Execute MCP tools and provide structured factual analysis of the returned data.

<success_criteria>
Execute the correct MCP tool and present results with basic factual analysis derived only from the actual tool output. Never fabricate data or add interpretations beyond what is directly calculable.
</success_criteria>

<constraints>
- Only execute provided commands/queries exactly - never modify or create new ones
- If a tool call fails, report the exact error message
- Only analyze data actually returned by tools
- Zero results → show "No results found" and stop
- Errors → report exact error message
- No business interpretation or recommendations
- If operation fails, report error and suggest alternatives if appropriate
</constraints>

## Tool Usage
Use available MCP tools as needed. If unsure, list tools first.

## Output Format
Present results in a structured format with execution details, results, and key findings.

Present tool results with factual analysis derived only from the actual data returned.
"""


async def test_mcp_connection(toolset: McpToolset) -> list | None:
    """Test MCP connection with proper timeout and error handling."""
    try:
        logger.debug(f"Discovered attributes: {dir(toolset)}")

        # Add timeout to prevent hanging connections
        try:
            # Use asyncio.wait_for with a reasonable timeout
            tools = await asyncio.wait_for(toolset.get_tools(), timeout=30.0)
            logger.debug(f"Retrieved tools (async): {tools}")
            logger.debug(f"Tool types: {[type(t) for t in tools] if tools else 'None'}")

            if tools and isinstance(tools, list):
                logger.info(f"Connection test successful - found {len(tools)} tools")
                return tools
            else:
                logger.info("Connection successful but no tools returned")
                return []

        except TimeoutError:
            logger.warning("Connection test timed out after 30 seconds")
            return []
        except asyncio.CancelledError:
            logger.warning("Connection test was cancelled")
            return []
        except Exception as async_e:
            logger.debug(f"Async get_tools() failed: {async_e}")

        # If async fails, tools might be available as attributes
        # Look for dynamically added tool attributes
        tool_attrs = []
        for attr_name in dir(toolset):
            if not attr_name.startswith("_") and attr_name not in [
                "get_tools",
                "close",
                "from_config",
                "get_tools_with_prefix",
                "process_llm_request",
                "tool_filter",
                "tool_name_prefix",
            ]:
                attr = getattr(toolset, attr_name)
                if hasattr(attr, "run") or hasattr(attr, "__call__"):  # Looks like a tool
                    tool_attrs.append(attr)

        if tool_attrs:
            logger.info(f"Found {len(tool_attrs)} tool attributes on toolset")
            return tool_attrs

        logger.warning("No tools found via any method")
        return []

    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return None
    finally:
        # Ensure proper cleanup
        try:
            if hasattr(toolset, "close"):
                await toolset.close()
        except Exception as cleanup_e:
            logger.debug(f"Cleanup error (ignored): {cleanup_e}")


def extract_tool_info(mcp_tool) -> dict:
    """Extract name, description, and schema from MCPTool object."""
    info = {
        "name": "Unknown",
        "description": "No description available",
        "schema": "No input schema available",
    }

    try:
        # Try to get tool metadata via _mcp_tool attribute (common in ADK MCPTool)
        if hasattr(mcp_tool, "_mcp_tool"):
            mcp_spec = mcp_tool._mcp_tool
            info["name"] = getattr(mcp_spec, "name", "Unknown")
            info["description"] = getattr(mcp_spec, "description", "No description")
            if hasattr(mcp_spec, "inputSchema"):
                schema = getattr(mcp_spec, "inputSchema", {})
                info["schema"] = json.dumps(schema, indent=2) if schema else "No schema"

        # Fallback: try direct attributes
        elif hasattr(mcp_tool, "name"):
            info["name"] = mcp_tool.name
            info["description"] = getattr(mcp_tool, "description", "No description")

        # Last resort: use string representation
        else:
            info["name"] = str(mcp_tool)

    except Exception as e:
        logger.debug(f"Failed to extract tool info: {e}")
        info["name"] = str(mcp_tool)

    return info


def enhance_prompt(tool_list: list) -> str:
    """Enhance the default prompt with the actual tool catalog."""
    if not tool_list:
        return DEFAULT_MCP_PROMPT

    tool_catalog = f"## Available Tools (Discovered {len(tool_list)} tools from MCP Server)\n"
    for tool in tool_list:
        info = extract_tool_info(tool)
        tool_catalog += f"- **{info['name']}**: {info['description']}\n"
        if info["schema"] != "No input schema available":
            tool_catalog += f"  **Input Schema**:\n```json\n{info['schema']}\n```\n\n"
        else:
            tool_catalog += "\n"

    enhanced = DEFAULT_MCP_PROMPT + "\n" + tool_catalog
    return enhanced


def update_orchestrator_prompt(agent_descriptions: list[str]) -> None:
    """Update orchestrator_prompt.py with new MCP agent descriptions."""
    orchestrator_prompt_path = Path("src/ai_sidekick_for_splunk/core/orchestrator_prompt.py")

    if not orchestrator_prompt_path.exists():
        logger.error(f"Orchestrator prompt file not found: {orchestrator_prompt_path}")
        return

    try:
        # Read current content
        content = orchestrator_prompt_path.read_text()

        # Find the </tools> closing tag
        tools_end = content.find("</tools>")
        if tools_end == -1:
            logger.error("Could not find </tools> closing tag in orchestrator prompt")
            return

        # Check if we already have MCP agent descriptions
        mcp_section_start = content.find("## Generated MCP Agents")

        if mcp_section_start != -1 and mcp_section_start < tools_end:
            # Remove existing MCP section
            mcp_section_end = content.find("\n</tools>", mcp_section_start)
            if mcp_section_end != -1:
                content = content[:mcp_section_start] + content[mcp_section_end:]
                tools_end = content.find("</tools>")

        # Generate new MCP section
        mcp_section = "\n## Generated MCP Agents\n"
        for description in agent_descriptions:
            mcp_section += description + "\n"

        # Insert before </tools>
        new_content = content[:tools_end] + mcp_section + "\n" + content[tools_end:]

        # Write back to file
        orchestrator_prompt_path.write_text(new_content)
        logger.info(
            f"✅ Updated orchestrator prompt with {len(agent_descriptions)} MCP agent descriptions"
        )

    except Exception as e:
        logger.error(f"Failed to update orchestrator prompt: {e}")


def generate_agent_description_for_orchestrator(
    agent_name: str, server_key: str, tool_list: list
) -> str:
    """Generate agent description for orchestrator prompt in the correct format."""

    # Extract tool names and descriptions
    tool_info = []
    for tool in tool_list:
        info = extract_tool_info(tool)
        tool_info.append(f"- {info['name']}: {info['description']}")

    # Limit to first 10 tools for readability
    if len(tool_info) > 10:
        tool_display = tool_info[:10] + [f"- ... and {len(tool_info) - 10} more tools"]
    else:
        tool_display = tool_info

    tool_capabilities = "\n".join(tool_display) if tool_display else "- No tools discovered"

    # Generate description based on server type
    server_description = f"{server_key} MCP server integration"

    # Create use cases based on server type
    use_cases = []
    if "firecrawl" in server_key.lower():
        use_cases = [
            "Web scraping and content extraction",
            "Website crawling and data collection",
            "Content analysis and documentation",
        ]
    elif "github" in server_key.lower():
        use_cases = [
            "Repository management and analysis",
            "Issue and pull request operations",
            "Code search and workflow automation",
        ]
    elif "context7" in server_key.lower():
        use_cases = [
            "Documentation library access",
            "Technical reference and examples",
            "Library and framework information",
        ]
    else:
        use_cases = [
            f"{server_key} server operations",
            "Tool execution and data processing",
            "External system integration",
        ]

    use_case_text = "\n".join([f"- {use_case}" for use_case in use_cases])

    return f"""
### **{agent_name}**: {server_description.title()}
**When to Use**:
{use_case_text}

**How to Use**:
- Pass complete user context and requirements
- Specify the operation or data needed from {server_key}
- Expect structured responses with tool execution results

**Available Tools ({len(tool_list)} total)**:
{tool_capabilities}

**Capabilities**:
- Direct integration with {server_key} MCP server
- Automatic tool discovery and execution
- Enhanced error handling with timeout management
- Full callback support for observability and validation
"""


def create_agent_files(
    agent_name: str,
    server_key: str,
    connection_params,
    custom_prompt: str,
    agents_dir: Path,
    server_data: dict,
) -> None:
    """Create agent files in the contrib/agents directory structure."""
    # Create agent directory
    agent_dir = agents_dir / agent_name
    agent_dir.mkdir(parents=True, exist_ok=True)

    # Generate agent.py file with full template
    class_name = f"{agent_name.title().replace('_', '')}Agent"
    agent_py_content = f'''"""
{agent_name.title()} Agent - Generated from MCP server configuration.

Auto-generated agent for {server_key} MCP server integration.
Based on GenericMCPAgent template with pre-configured connection parameters.
"""

import logging
import uuid
from typing import Any, Optional

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams, StdioConnectionParams, StdioServerParameters
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

from ai_sidekick_for_splunk.core.base_agent import AgentMetadata, BaseAgent

from .prompt import {agent_name.upper()}_PROMPT

# Add imports for callbacks
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.genai.types import Content, Part
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any

logger = logging.getLogger(__name__)


class {class_name}(BaseAgent):
    """
    {agent_name.title()} agent for {server_key} MCP server integration.

    Auto-generated agent with pre-configured connection parameters and full callback support.
    """

    # Class metadata for discovery system
    METADATA = AgentMetadata(
        name="{agent_name}",
        description="Agent for {server_key} MCP server integration",
        version="1.0.0",
        author="Generated",
        tags=["mcp", "integration", "{server_key.lower()}"],
        dependencies=[],
    )

    name = "{agent_name}"
    description = "Agent for {server_key} MCP server integration"

    def __init__(
        self,
        config: Any | None = None,
        metadata: AgentMetadata | None = None,
        tools: list[Any] | None = None,
        session_state: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the {agent_name.title()} Agent with pre-configured connection."""
        from ai_sidekick_for_splunk.core.config import Config

        # Use default config if none provided
        if config is None:
            config = Config()

        # Create metadata if not provided
        if metadata is None:
            metadata = self.METADATA

        super().__init__(config, metadata, tools, session_state)

        # Pre-configured connection parameters for {server_key}
        # Note: You can modify the timeout value below if operations are slow
        self.connection_params = {_generate_connection_params_code(connection_params, server_data)}
        self.custom_prompt = {agent_name.upper()}_PROMPT

        # Create and store MCP toolset for direct execution
        self.mcp_toolset = self._create_mcp_toolset()
        if self.mcp_toolset:
            logger.info("✅ MCP toolset created and stored for direct execution")
        else:
            logger.warning("⚠️ MCP toolset creation failed - direct execution not available")

    @property
    def instructions(self) -> str:
        """Get the agent instructions/prompt."""
        return self.custom_prompt

    def before_model_callback(self, callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
        """Log context sent to the model."""
        logger.info(f"Before model call for agent {{callback_context.agent_name}}")
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"LLM Request Context: {{llm_request}}")
        return None  # Proceed with model call

    def after_model_callback(self, callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
        """Log response from model and validate tool calls if expected."""
        logger.info(f"After model call for agent {{callback_context.agent_name}}")
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"LLM Response: {{llm_response}}")

        # Validation: Check if tool calls are present if expected
        if hasattr(self, '_expect_tool_call') and self._expect_tool_call:
            if not llm_response.candidates or not llm_response.candidates[0].content.parts[0].function_call:
                logger.error("Validation failed: Expected tool call but none was made.")
                return LlmResponse(
                    content=Content(
                        role="model",
                        parts=[Part(text="Error: Expected tool call not made. Invalidating response.")]
                    )
                )
        return None  # Proceed with original response

    def before_tool_callback(self, tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[Dict]:
        """Log and optionally modify tool arguments before execution."""
        agent_name = tool_context.agent_name
        tool_name = tool.name
        logger.info(f"Before tool call for tool '{{tool_name}}' in agent '{{agent_name}}'")
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Tool args: {{args}}")

        # Example validation: Could block certain operations or modify args
        # Return None to proceed with original args, or return dict to override tool response
        return None

    def after_tool_callback(self, tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Any) -> Optional[Any]:
        """Log and optionally modify tool response after execution."""
        agent_name = tool_context.agent_name
        tool_name = tool.name
        logger.info(f"After tool call for tool '{{tool_name}}' in agent '{{agent_name}}'")
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Tool args: {{args}}, Response: {{tool_response}}")

        # Enhanced validation with timeout detection
        if not tool_response:
            logger.error("Validation failed: Tool response is empty.")
            return "Error: Invalid tool response"

        # Check for timeout errors in the response
        if isinstance(tool_response, dict) and 'error' in tool_response:
            error_msg = str(tool_response.get('error', ''))
            if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
                logger.warning(f"Tool {{tool_name}} timed out - consider increasing timeout in agent configuration or mcp.json")

        return None  # Proceed with original response

    def _initialize_llm_agent(self) -> None:
        """Initialize the ADK LlmAgent instance with MCP toolset."""
        try:
            from google.adk.agents import LlmAgent

            mcp_toolset = self._create_mcp_toolset()
            if not mcp_toolset:
                logger.error("Cannot create ADK agent without MCP toolset")
                raise RuntimeError("MCP toolset creation failed")

            self._llm_agent = LlmAgent(
                model=self.config.model.primary_model,
                name=self.display_name,
                description=self.metadata.description,
                instruction=self.instructions,
                tools=[mcp_toolset],
                before_model_callback=self.before_model_callback,
                after_model_callback=self.after_model_callback,
                before_tool_callback=self.before_tool_callback,
                after_tool_callback=self.after_tool_callback,
            )
            self._is_initialized = True
            logger.debug("Created {agent_name} ADK agent with MCP toolset")
        except ImportError as e:
            logger.error(f"ADK LlmAgent not available for {{self.metadata.name}}: {{e}}")
            raise RuntimeError(
                f"ADK LlmAgent is required for agent {{self.metadata.name}} but not available"
            ) from e
        except Exception as e:
            logger.error(f"Failed to initialize LlmAgent for {{self.metadata.name}}: {{e}}")
            raise

    def _create_mcp_toolset(self) -> MCPToolset | None:
        """Create MCP toolset with pre-configured connection parameters."""
        try:
            # Temporarily suppress ADK authentication warnings
            adk_auth_logger = logging.getLogger("google_adk.google.adk.tools.base_authenticated_tool")
            original_level = adk_auth_logger.level
            adk_auth_logger.setLevel(logging.ERROR)

            try:
                # Create MCPToolset with extended timeout for slow operations
                mcp_toolset = MCPToolset(
                    connection_params=self.connection_params,
                    # Add any additional timeout or retry configurations here
                )
            finally:
                adk_auth_logger.setLevel(original_level)

            logger.info("✅ Created MCP toolset with pre-configured connection parameters and extended timeout")
            return mcp_toolset

        except Exception as e:
            logger.error(f"Failed to create MCP toolset: {{e}}")
            return None

    def get_adk_agent(self, tools: list[Any] | None = None) -> LlmAgent | None:
        """Create ADK LlmAgent for MCP operations."""
        try:
            mcp_toolset = self._create_mcp_toolset()
            if not mcp_toolset:
                logger.error("Cannot create ADK agent without MCP toolset")
                return None

            agent = LlmAgent(
                model=self.config.model.primary_model,
                name=self.name,
                description=self.description,
                instruction=self.instructions,
                tools=[mcp_toolset],
                before_model_callback=self.before_model_callback,
                after_model_callback=self.after_model_callback,
                before_tool_callback=self.before_tool_callback,
                after_tool_callback=self.after_tool_callback,
            )

            logger.debug("Created {agent_name} ADK agent with MCP toolset")
            return agent

        except Exception as e:
            logger.error(f"Failed to create {agent_name} ADK agent: {{e}}")
            return None

    async def execute(self, task: str, context: Optional[dict[str, Any]] = None, expect_tool_call: bool = False) -> dict[str, Any]:
        """Execute a task using the ADK LlmAgent with MCP toolset."""
        self._expect_tool_call = expect_tool_call
        try:
            logger.info(f"{class_name} executing task: {{task}}")

            if context:
                task = f"{{task}}\\nParameters: {{dict(context)}}"

            result = await self.process_request(task, context)

            logger.info("✅ {agent_name} task executed successfully")
            return {{
                "success": True,
                "task_type": "mcp",
                "response": result,
                "execution_method": "adk_agent_with_mcp_tools",
            }}

        except Exception as e:
            logger.error(f"{class_name} execution failed: {{e}}", exc_info=True)
            return {{
                "success": False,
                "error": str(e),
                "message": "Failed to execute MCP task",
            }}

    def get_capabilities(self) -> list[str]:
        """Get agent capabilities."""
        return [
            "mcp_integration",
            "real_time_access",
            "tool_execution",
            "{server_key.lower()}_integration",
        ]

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data for the agent."""
        return "task" in input_data or "query" in input_data

    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        logger.info("{class_name} cleanup completed")
        pass
'''

    # Sanitize custom_prompt to escape ALL ADK injection patterns like {var} and {+var+}
    # ADK tries to inject session variables for any {var} pattern, so we need to escape them all
    def escape_braces(text):
        # Strategy: Replace problematic patterns with safe XML-style tags
        # This avoids complex regex and double-escaping issues

        # First, protect already-safe XML tags by temporarily replacing them
        xml_tags = {}
        xml_counter = 0

        # Find and temporarily replace XML-style tags like <success_criteria>
        xml_pattern = r"<([^>]+)>"
        for match in re.finditer(xml_pattern, text):
            placeholder = f"__XML_TAG_{xml_counter}__"
            xml_tags[placeholder] = match.group(0)
            text = text.replace(match.group(0), placeholder, 1)
            xml_counter += 1

        # Handle malformed patterns first
        text = re.sub(r"\{([^}>]+)>", r"<\1>", text)  # {var> -> <var>
        text = re.sub(r"<([^}>]+)\}", r"<\1>", text)  # <var} -> <var>
        text = re.sub(r"\{([^}]+)\}\}", r"<\1>", text)  # {var}} -> <var>

        # Then handle normal {var} patterns -> convert to <var>
        text = re.sub(r"\{([^}]+)\}", r"<\1>", text)

        # Restore protected XML tags
        for placeholder, original in xml_tags.items():
            text = text.replace(placeholder, original)

        return text

    sanitized_prompt = escape_braces(custom_prompt)
    logger.debug(
        f"Sanitized prompt for {agent_name} (first 200 chars): {sanitized_prompt[:200]}..."
    )

    # Generate prompt.py file - use regular string, not f-string to avoid syntax errors with JSON schemas
    prompt_py_content = f'''"""
Prompt for {agent_name.title()} Agent.

Enhanced prompt with tools discovered from {server_key} MCP server.
"""

{agent_name.upper()}_PROMPT = """{sanitized_prompt}"""
'''

    # Generate __init__.py file with proper exposure like splunk_mcp
    class_name = f"{agent_name.title().replace('_', '')}Agent"
    init_py_content = f'''"""
{agent_name.title()} Agent - Generated MCP agent for {server_key} integration.

Auto-generated agent for {server_key} MCP server integration with full
callback support and observability features.
"""

from .agent import {class_name}

__version__ = "1.0.0"
__all__ = ["{class_name}"]
'''

    # Generate README.md file
    readme_content = f"""# {agent_name.title()} Agent

Auto-generated agent for {server_key} MCP server integration.

## Usage

```python
from ai_sidekick_for_splunk.contrib.agents.{agent_name} import {agent_name.title().replace("_", "")}Agent

# Create and use the agent
agent = {agent_name.title().replace("_", "")}Agent()
result = await agent.execute("Your task here")
```

## Configuration

This agent is pre-configured to connect to the {server_key} MCP server with the following setup:
- Connection type: {"HTTP" if isinstance(connection_params, StreamableHTTPConnectionParams) else "Stdio"}
- Enhanced prompt with discovered tools
- Automatic connection management

Generated on: {__import__("datetime").datetime.now().isoformat()}
"""

    # Write files
    (agent_dir / "agent.py").write_text(agent_py_content)
    (agent_dir / "prompt.py").write_text(prompt_py_content)
    (agent_dir / "__init__.py").write_text(init_py_content)
    (agent_dir / "README.md").write_text(readme_content)

    logger.info(f"Created agent files in {agent_dir}")


def _generate_connection_params_code(connection_params, server_data: dict) -> str:
    """Generate Python code for connection parameters."""
    if isinstance(connection_params, StreamableHTTPConnectionParams):
        return f'''StreamableHTTPConnectionParams(
            url="{server_data.get("url")}",
            headers={server_data.get("headers", {})},
            timeout=15.0,
            sse_read_timeout=300.0,
            terminate_on_close=True,
            max_retries=2,
            retry_delay=1.0,
        )'''
    elif isinstance(connection_params, StdioConnectionParams):
        # Get timeout from server config or use default
        timeout = server_data.get("timeout", 60.0)  # Default 60s, user-configurable

        return f'''StdioConnectionParams(
            server_params=StdioServerParameters(
                command="{server_data.get("command")}",
                args={server_data.get("args", [])},
                env={{**{server_data.get("env", {})}, 'DEBUG': '1'}}
            ),
            terminate_on_close=True,
            timeout={timeout},  # User-configurable timeout (default 60s)
        )'''
    else:
        return "None  # Unknown connection type"


async def create_mcp_agents(
    json_path: str,
    save_to_disk: bool = False,
    override: bool = False,
    update_orchestrator: bool = False,
) -> dict[str, Any]:
    """Create MCP agent instances from mcp.json configurations."""
    try:
        with open(json_path) as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load mcp.json: {e}")
        sys.exit(1)

    agents = {}
    mcp_servers = data.get("mcpServers", {})
    agent_descriptions = []  # For orchestrator prompt update

    # Set up agents directory if saving to disk
    if save_to_disk:
        # Get current working directory (should be project root when run with uv run)
        project_root = Path.cwd()
        agents_dir = project_root / "src" / "ai_sidekick_for_splunk" / "contrib" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Will save agents to: {agents_dir}")

    for server_key, server_data in mcp_servers.items():
        if server_data.get("enabled", True) is False:
            logger.debug(f"Skipping disabled server: {server_key}")
            continue

        logger.info(f"Processing server: {server_key}")
        connection_params = None

        # Check for StreamableHTTP pattern
        url = server_data.get("url")
        if url and "mcp" in url.lower():
            headers = server_data.get("headers", {})
            connection_params = StreamableHTTPConnectionParams(
                url=url,
                headers=headers,
                timeout=15.0,
                sse_read_timeout=300.0,
                terminate_on_close=True,  # Docs recommend for proper cleanup
                max_retries=2,
                retry_delay=1.0,
            )
            logger.info(f"Configured StreamableHTTP for {server_key}")

        # Default to stdio pattern
        elif "command" in server_data:
            server_params = StdioServerParameters(
                command=server_data["command"],
                args=server_data.get("args", []),
                env={**server_data.get("env", {}), "DEBUG": "1"},  # Enable server debug
            )
            # Get timeout from server config or use default
            timeout = server_data.get("timeout", 60.0)  # Default 60s for all stdio connections

            connection_params = StdioConnectionParams(
                server_params=server_params,
                terminate_on_close=True,  # Docs recommend for process termination
                timeout=timeout,  # User-configurable timeout (default 60s)
                # Add other params like timeouts if needed
            )
            logger.info(f"Configured stdio process for {server_key} with {timeout}s timeout")

        else:
            logger.warning(f"Skipping {server_key}: No valid url or command found")
            continue

        logger.debug(f"Configuring params for {server_key}")
        # Create toolset
        try:
            toolset = McpToolset(connection_params=connection_params)
        except Exception as e:
            logger.error(f"Failed to create MCPToolset for {server_key}: {e}")
            continue

        logger.debug(f"Testing connection for {server_key}")
        # Always define custom_prompt
        tool_response = await test_mcp_connection(toolset)  # Await async test
        custom_prompt = enhance_prompt(tool_response or [])  # Use empty if None
        logger.debug(
            f"Enhanced prompt for {server_key}: {custom_prompt[:200]}..."
        )  # Truncate for log

        # Create the agent with enhanced prompt
        agent_name = f"{server_key}_agent".lower()
        logger.debug(f"Creating agent: {agent_name}")

        # Save agent files to disk if requested
        if save_to_disk:
            agent_dir = agents_dir / agent_name

            # Check if agent already exists and handle override logic
            if agent_dir.exists() and not override:
                logger.warning(f"Skipping existing agent: {agent_name} (use --override to replace)")
                logger.info(f"Agent directory already exists at: {agent_dir}")
                continue
            elif agent_dir.exists() and override:
                logger.info(f"Overriding existing agent: {agent_name}")
                # Remove existing directory to ensure clean override
                import shutil

                try:
                    shutil.rmtree(agent_dir)
                    logger.debug(f"Removed existing agent directory: {agent_dir}")
                except Exception as e:
                    logger.error(f"Failed to remove existing agent directory {agent_dir}: {e}")
                    continue

            try:
                # Create a copy of server_data with server_key for the template
                server_data_with_key = {**server_data, "server_key": server_key}
                create_agent_files(
                    agent_name,
                    server_key,
                    connection_params,
                    custom_prompt,
                    agents_dir,
                    server_data_with_key,
                )
                logger.info(f"✅ Successfully created agent files for: {agent_name}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent files for {agent_name}: {e}")
                import traceback

                logger.debug(traceback.format_exc())
                continue

        # Store agent configuration (agents are generated as files, not instances)
        try:
            agent_config = {
                "name": agent_name,
                "server_key": server_key,
                "connection_params": connection_params,
                "custom_prompt": custom_prompt,
                "tools_discovered": len(tool_response or []),
            }
            agents[agent_name] = agent_config
            logger.info(f"✅ Created agent configuration: {agent_name} with enhanced prompt")

            # Generate description for orchestrator prompt if requested
            if update_orchestrator:
                description = generate_agent_description_for_orchestrator(
                    agent_name, server_key, tool_response or []
                )
                agent_descriptions.append(description)
                logger.debug(f"Generated orchestrator description for {agent_name}")

        except Exception as e:
            logger.error(f"❌ Failed to create agent configuration for {agent_name}: {e}")
            continue

    # Log summary
    total_servers = len(mcp_servers)
    successful_agents = len(agents)
    logger.info(f"📊 Summary: {successful_agents}/{total_servers} agents created successfully")

    if successful_agents < total_servers:
        skipped = total_servers - successful_agents
        logger.warning(f"⚠️  {skipped} servers were skipped due to errors or existing agents")

    # Update orchestrator prompt if requested and we have descriptions
    if update_orchestrator and agent_descriptions:
        try:
            update_orchestrator_prompt(agent_descriptions)
            logger.info(
                f"🔄 Updated orchestrator prompt with {len(agent_descriptions)} MCP agent descriptions"
            )
        except Exception as e:
            logger.error(f"❌ Failed to update orchestrator prompt: {e}")
    elif update_orchestrator and not agent_descriptions:
        logger.warning("⚠️  No agent descriptions to add to orchestrator prompt")

    return agents


def main():
    load_dotenv()  # Load .env from current dir

    # Parse args early to determine logging level
    parser = argparse.ArgumentParser(
        description="Create MCP agents from config",
        epilog="""
Environment variables:
  LOG_LEVEL (DEBUG/INFO/WARNING/ERROR/CRITICAL) sets default logging level

Timeout configuration:
  Add 'timeout': 120.0 to any server in mcp.json to set custom timeout (default: 60s)
  Example: {"Firecrawl": {"command": "...", "timeout": 120.0}}

Generated agents can be further customized by editing the timeout value in agent.py
        """,
    )
    parser.add_argument("-c", "--config", default="~/.cursor/mcp.json", help="Path to mcp.json")
    parser.add_argument(
        "--test-only",
        default=False,
        action="store_true",
        help="Test connections without creating agents",
    )
    parser.add_argument(
        "--save",
        default=False,
        action="store_true",
        help="Save agents to disk in contrib/agents directory",
    )
    parser.add_argument(
        "--override",
        default=False,
        action="store_true",
        help="Override existing agent files if they exist",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Reduce output verbosity (INFO level, overrides LOG_LEVEL)",
    )
    parser.add_argument(
        "--update-orchestrator",
        action="store_true",
        help="Update orchestrator_prompt.py with generated agent descriptions",
    )
    args = parser.parse_args()

    # Determine logging level from multiple sources (priority order)
    log_level = logging.DEBUG  # Default

    # 1. Check environment variable LOG_LEVEL from .env
    env_log_level = os.environ.get("LOG_LEVEL", "").upper()
    if env_log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        log_level = getattr(logging, env_log_level)

    # 2. Override with --quiet flag if provided
    if args.quiet:
        log_level = logging.INFO

    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Suppress noisy ADK authentication warnings
    logging.getLogger("google_adk.google.adk.tools.base_authenticated_tool").setLevel(logging.ERROR)
    # Suppress noisy MCP client debug messages
    logging.getLogger("mcp.client.streamable_http").setLevel(logging.WARNING)
    logging.getLogger("httpcore.connection").setLevel(logging.WARNING)
    logging.getLogger("google_adk.google.adk.tools.mcp_tool.mcp_session_manager").setLevel(
        logging.INFO
    )
    # Suppress asyncio errors from MCP cleanup issues
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)

    if not args.quiet:
        logger.debug(
            f"Log level set to: {logging.getLevelName(log_level)} (env: {env_log_level or 'not set'}, quiet: {args.quiet})"
        )
        logger.debug(f"GOOGLE_GENAI_USE_VERTEXAI: {os.environ.get('GOOGLE_GENAI_USE_VERTEXAI')}")

    # Expand user home dir
    config_path = os.path.expanduser(args.config)

    logger.info(f"📁 Using config file: {config_path}")
    logger.info(
        f"🔧 Options: test_only={args.test_only}, save={args.save}, override={args.override}"
    )

    if not os.path.exists(config_path):
        logger.error(f"❌ Config file not found: {config_path}")
        sys.exit(1)

    if args.test_only:
        logger.info("🧪 Test-only mode: Will test connections without creating agents")
        try:
            data = json.load(open(config_path))
            server_count = len(data.get("mcpServers", {}))
            logger.info(f"Found {server_count} servers in config")
            # TODO: Add actual connection testing logic here
            print("✅ Tests complete")
        except Exception as e:
            logger.error(f"❌ Failed to load config for testing: {e}")
            sys.exit(1)
    else:
        try:
            logger.info("🚀 Starting agent creation process...")
            agents = asyncio.run(
                create_mcp_agents(
                    config_path,
                    save_to_disk=args.save,
                    override=args.override,
                    update_orchestrator=args.update_orchestrator,
                )
            )

            logger.info("🎉 Agent creation complete!")
            print(f"✅ Created {len(agents)} agents: {list(agents.keys())}")

            if args.save:
                print("💾 Agents saved to disk in contrib/agents/ directory")
                if args.override:
                    print("🔄 Override mode was enabled - existing agents were replaced")
            else:
                print("💡 Use --save to write agents to disk")

            if args.update_orchestrator:
                print("🔄 Orchestrator prompt updated with MCP agent descriptions")
            else:
                print(
                    "💡 Use --update-orchestrator to add agent descriptions to orchestrator prompt"
                )

        except KeyboardInterrupt:
            logger.warning("⚠️  Process interrupted by user")
            sys.exit(130)  # Standard exit code for SIGINT
        except Exception as e:
            logger.error(f"❌ Agent creation failed: {e}")
            import traceback

            logger.debug(traceback.format_exc())
            sys.exit(1)


if __name__ == "__main__":
    main()
