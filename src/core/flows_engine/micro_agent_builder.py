"""
Micro Agent Builder for Parallel Fan-Out/Gather Pattern.

This module creates dynamic LlmAgent instances for individual tasks in Guided Agent Flows,
implementing the ADK Parallel Fan-Out/Gather pattern for concurrent task execution.
"""

import asyncio
import logging
import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.getLogger(__name__).debug("✅ Environment variables loaded from .env file")
except ImportError:
    logging.getLogger(__name__).warning("⚠️ python-dotenv not available, relying on system environment variables")

from ..config import Config
from .agent_flow import FlowTask

logger = logging.getLogger(__name__)


@dataclass
class MicroAgentResult:
    """Result from a micro agent execution."""
    task_id: str
    agent_name: str
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    execution_time: float | None = None
    timeout_occurred: bool = False


class MicroAgentBuilder:
    """
    Builder for creating dynamic LlmAgent instances for individual tasks.

    Implements the ADK pattern of creating ephemeral agents for parallel execution,
    each bounded by specific tools and instructions from the flow definition.
    """

    def __init__(self, config: Config | None = None, agent_coordinator=None):
        """
        Initialize micro agent builder.

        Args:
            config: Configuration instance
            agent_coordinator: Agent coordinator for tool access
        """
        self.config = config or Config()
        self.agent_coordinator = agent_coordinator
        self._created_agents = {}

    def create_micro_agent_for_task(self, task: FlowTask, phase_context: dict[str, Any]) -> dict[str, Any]:
        """
        Create a micro agent configuration for a specific task.

        This follows the ADK pattern of creating task-specific LlmAgents with:
        - Instructions pulled from task definition
        - Tools bounded by task.llm_loop.allowed_tools
        - Timeout and execution constraints

        Args:
            task: FlowTask to create micro agent for
            phase_context: Context from the current phase

        Returns:
            Micro agent configuration dict
        """
        agent_name = f"MicroAgent_{task.task_id}"

        # Build instructions from task metadata
        instructions = self._build_micro_agent_instructions(task, phase_context)

        # Determine allowed tools
        allowed_tools = self._get_allowed_tools(task)

        # Set timeout
        timeout = task.timeout_sec or self.config.micro_agent_timeout

        micro_agent_config = {
            "name": agent_name,
            "task_id": task.task_id,
            "instructions": instructions,
            "allowed_tools": allowed_tools,
            "timeout_sec": timeout,
            "model": self.config.model.primary_model,
            "temperature": self.config.model.temperature,
            "max_tokens": self.config.model.max_tokens,
            "bounded_execution": True,
            "task_metadata": {
                "title": self._resolve_placeholders(task.title, phase_context),
                "description": self._resolve_placeholders(task.description, phase_context),
                "goal": self._resolve_placeholders(task.goal, phase_context),
                "execution_mode": task.execution_mode,
                "search_query": self._resolve_placeholders(task.search_query, phase_context) if task.search_query else None,
                "parameters": task.parameters
            },
            "context": phase_context
        }

        logger.debug(f"🤖 Created micro agent config for task {task.task_id}: {agent_name}")
        return micro_agent_config

    def _resolve_placeholders(self, text: str, context: dict[str, Any]) -> str:
        """Resolve placeholders in text using context variables."""
        if not text:
            return text

        resolved_text = text
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in resolved_text:
                resolved_text = resolved_text.replace(placeholder, str(value))

        return resolved_text

    def _build_micro_agent_instructions(self, task: FlowTask, context: dict[str, Any]) -> str:
        """Build specific instructions for the micro agent."""

        # Resolve placeholders in task fields using context
        resolved_title = self._resolve_placeholders(task.title, context)
        resolved_description = self._resolve_placeholders(task.description, context)
        resolved_goal = self._resolve_placeholders(task.goal, context)
        resolved_instructions = self._resolve_placeholders(
            task.dynamic_instructions or 'Execute the task according to the goal and description.',
            context
        )

        # Base instruction template
        base_instructions = f"""
You are a specialized micro agent executing task: {task.task_id} - {resolved_title}

**Task Description**: {resolved_description}
**Goal**: {resolved_goal}

**Context**: INDEX_NAME = {context.get('INDEX_NAME', 'N/A')}

**Your Mission**:
{resolved_instructions}

**CRITICAL EXECUTION REQUIREMENTS**:
- You MUST call the MCP tools directly using function calling - do not just describe what you would do
- You have direct access to MCP tools like run_oneshot_search, run_splunk_search, etc.
- IMMEDIATELY make the function call as your first action
- DO NOT write explanations or markdown code blocks - use actual function calls
- Wait for the function result, then analyze the REAL data returned
- Your response must be based ONLY on actual function call results
- If a function call fails, report the actual error message

**Function Call Pattern**:
Call run_oneshot_search directly with your search query: "index=s4c_www | head 10"

**Execution Guidelines**:
- Start by calling the appropriate tool to get real data
- Validate your approach before executing searches
- Focus on the specific goal of this task
- Provide clear reasoning for your actions based on ACTUAL results
- Report any errors or issues encountered during tool execution

**Constraints**:
- Stay within your bounded execution scope
- Do not exceed the allowed tools
- Ensure all outputs are factual and grounded in REAL search results from tool calls
- If you encounter errors, report them clearly without fabricating data
- NEVER provide fake or simulated data - always use actual tool results
"""

        # Add LLM loop specific instructions if enabled
        if task.llm_loop and task.llm_loop.enabled:
            # Build tool usage instructions
            mcp_tools = []
            direct_tools = []

            mcp_tool_mapping = {
                'run_oneshot_search': 'splunk_mcp',
                'run_splunk_search': 'splunk_mcp',
                'get_spl_reference': 'splunk_mcp',
                'get_splunk_documentation': 'splunk_mcp',
                'list_spl_commands': 'splunk_mcp',
                'get_splunk_cheat_sheet': 'splunk_mcp'
            }

            for tool in task.llm_loop.allowed_tools:
                if tool in mcp_tool_mapping:
                    mcp_tools.append(tool)
                else:
                    direct_tools.append(tool)

            tool_usage_guide = ""
            if mcp_tools:
                # Create specific instructions for each MCP tool
                mcp_instructions = []
                for tool in mcp_tools:
                    if tool == 'run_oneshot_search':
                        mcp_instructions.append("- For Splunk searches: Call run_oneshot_search directly with your query")
                    elif tool == 'run_splunk_search':
                        mcp_instructions.append("- For Splunk searches: Call run_splunk_search directly with your query")
                    elif tool == 'get_spl_reference':
                        mcp_instructions.append("- For SPL help: Call get_spl_reference directly")
                    elif tool == 'get_splunk_documentation':
                        mcp_instructions.append("- For Splunk docs: Call get_splunk_documentation directly")
                    else:
                        mcp_instructions.append(f"- For {tool}: Call {tool} directly")

                tool_usage_guide += f"""
**Available MCP Tools** (call directly):
{chr(10).join(mcp_instructions)}

**CRITICAL**: You now have direct access to MCP tools. Call them directly by name.
Example: Call run_oneshot_search directly with your search query: "index=s4c_www | head 10"
"""

            if direct_tools:
                tool_usage_guide += f"""
**Direct Tools**: {', '.join(direct_tools)}
"""

            llm_instructions = f"""
**LLM Loop Configuration**:
- Maximum iterations: {task.llm_loop.max_iterations}
- Step validation: {task.llm_loop.step_validation}
{tool_usage_guide}
- Bounded execution: {task.llm_loop.bounded_execution}

**LLM Loop Instructions**:
{self._resolve_placeholders(task.llm_loop.prompt or 'Use iterative reasoning to achieve the task goal.', context)}
"""
            base_instructions += llm_instructions

        # Add search-specific instructions if this is a search task
        if task.search_query:
            resolved_search_query = self._resolve_placeholders(task.search_query, context)
            search_instructions = f"""
**Search Task Details**:
- Base query: {resolved_search_query}
- Parameters: {task.parameters or 'None'}
- Execution mode: {task.execution_mode or 'standard'}

Remember to validate SPL syntax and optimize queries for performance.
"""
            base_instructions += search_instructions

        return base_instructions.strip()

    def _get_allowed_tools(self, task: FlowTask) -> list[str]:
        """Get the list of allowed tools for this task."""

        # Start with LLM loop allowed tools if available
        if task.llm_loop and task.llm_loop.allowed_tools:
            return task.llm_loop.allowed_tools.copy()

        # Fall back to task tool and common tools
        tools = []

        if task.tool:
            tools.append(task.tool)

        # Add validation tools if required
        if task.validation and task.validation.validate_syntax:
            tools.extend(["search_guru", "get_spl_reference"])

        # Add synthesis tools if required
        if task.result_interpretation and task.result_interpretation.interpret_results:
            tools.append("result_synthesizer")

        # Default tools for search tasks
        if task.search_query:
            default_search_tools = ["splunk_mcp", "run_oneshot_search", "run_splunk_search"]
            tools.extend([tool for tool in default_search_tools if tool not in tools])

        return tools or ["splunk_mcp"]  # Ensure at least one tool

    async def execute_micro_agents_parallel(
        self,
        micro_agent_configs: list[dict[str, Any]],
        max_parallel: int,
        progress_callback: Callable | None = None
    ) -> list[MicroAgentResult]:
        """
        Execute multiple micro agents in parallel using asyncio.gather().

        This implements the core Fan-Out/Gather pattern from ADK documentation.

        Args:
            micro_agent_configs: List of micro agent configurations
            max_parallel: Maximum number of concurrent executions
            progress_callback: Optional callback for progress updates

        Returns:
            List of MicroAgentResult objects
        """
        logger.info(f"🚀 Starting parallel execution of {len(micro_agent_configs)} micro agents (max_parallel={max_parallel})")

        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_parallel)

        # Create tasks for parallel execution
        tasks = []
        for config in micro_agent_configs:
            task = self._execute_single_micro_agent(config, semaphore, progress_callback)
            tasks.append(task)

        # Fan-Out: Launch all tasks concurrently
        # Gather: Wait for all to complete and collect results
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results and handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"❌ Micro agent {micro_agent_configs[i]['name']} failed with exception: {result}")
                    processed_results.append(MicroAgentResult(
                        task_id=micro_agent_configs[i]['task_id'],
                        agent_name=micro_agent_configs[i]['name'],
                        success=False,
                        error=str(result)
                    ))
                else:
                    processed_results.append(result)

            logger.info(f"✅ Parallel execution completed. Success: {sum(1 for r in processed_results if r.success)}/{len(processed_results)}")
            return processed_results

        except Exception as e:
            logger.error(f"❌ Parallel execution failed: {e}")
            # Return error results for all agents
            return [
                MicroAgentResult(
                    task_id=config['task_id'],
                    agent_name=config['name'],
                    success=False,
                    error=f"Parallel execution failed: {e}"
                )
                for config in micro_agent_configs
            ]

    async def _execute_single_micro_agent(
        self,
        config: dict[str, Any],
        semaphore: asyncio.Semaphore,
        progress_callback: Callable | None = None
    ) -> MicroAgentResult:
        """Execute a single micro agent with concurrency control."""

        async with semaphore:  # Limit concurrency
            agent_name = config['name']
            task_id = config['task_id']
            timeout = config.get('timeout_sec', self.config.micro_agent_timeout)

            logger.debug(f"🔧 Starting micro agent {agent_name} for task {task_id}")

            # Send progress update
            if progress_callback:
                try:
                    progress_callback({
                        "phase_name": "parallel_execution",
                        "task_id": task_id,
                        "message": f"🤖 **Started Micro Agent**: {agent_name}\n*Task*: {config['task_metadata']['title']}",
                        "status": "starting",
                        "data": {"agent_name": agent_name}
                    })
                except Exception as e:
                    logger.error(f"Progress callback failed: {e}")

            start_time = asyncio.get_event_loop().time()

            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    self._run_micro_agent_logic(config),
                    timeout=timeout
                )

                execution_time = asyncio.get_event_loop().time() - start_time

                logger.debug(f"✅ Micro agent {agent_name} completed successfully in {execution_time:.2f}s")

                # Send completion progress update
                if progress_callback:
                    try:
                        progress_callback({
                            "phase_name": "parallel_execution",
                            "task_id": task_id,
                            "message": f"✅ **Completed Micro Agent**: {agent_name}\n*Duration*: {execution_time:.1f}s",
                            "status": "completed",
                            "data": {"agent_name": agent_name, "execution_time": execution_time}
                        })
                    except Exception as e:
                        logger.error(f"Progress callback failed: {e}")

                return MicroAgentResult(
                    task_id=task_id,
                    agent_name=agent_name,
                    success=True,
                    data=result,
                    execution_time=execution_time
                )

            except TimeoutError:
                execution_time = asyncio.get_event_loop().time() - start_time
                error_msg = f"Micro agent {agent_name} timed out after {timeout}s"
                logger.error(f"⏰ {error_msg}")

                # Send timeout progress update
                if progress_callback:
                    try:
                        progress_callback({
                            "phase_name": "parallel_execution",
                            "task_id": task_id,
                            "message": f"⏰ **Timeout**: {agent_name}\n*Duration*: {execution_time:.1f}s",
                            "status": "error",
                            "data": {"agent_name": agent_name, "timeout": True}
                        })
                    except Exception as e:
                        logger.error(f"Progress callback failed: {e}")

                return MicroAgentResult(
                    task_id=task_id,
                    agent_name=agent_name,
                    success=False,
                    error=error_msg,
                    execution_time=execution_time,
                    timeout_occurred=True
                )

            except Exception as e:
                execution_time = asyncio.get_event_loop().time() - start_time
                error_msg = f"Micro agent {agent_name} failed: {str(e)}"
                logger.error(f"❌ {error_msg}")

                # Send error progress update
                if progress_callback:
                    try:
                        progress_callback({
                            "phase_name": "parallel_execution",
                            "task_id": task_id,
                            "message": f"❌ **Failed**: {agent_name}\n*Error*: {str(e)[:100]}...",
                            "status": "error",
                            "data": {"agent_name": agent_name, "error": str(e)}
                        })
                    except Exception as e:
                        logger.error(f"Progress callback failed: {e}")

                return MicroAgentResult(
                    task_id=task_id,
                    agent_name=agent_name,
                    success=False,
                    error=error_msg,
                    execution_time=execution_time
                )

    async def _run_micro_agent_logic(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        Run the actual micro agent logic using real ADK LlmAgent.
        """
        task_metadata = config['task_metadata']
        task_id = config['task_id']
        allowed_tools = config['allowed_tools']
        instructions = config['instructions']

        logger.debug(f"🔍 Executing real micro agent logic for {task_id} with tools: {allowed_tools}")

        try:
            # Create real LlmAgent with the provided configuration
            from google.adk.agents import LlmAgent
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService
            from google.adk.tools.agent_tool import AgentTool
            from google.genai import types

            # Get tools for the micro agent
            agent_tools = []

            # Map MCP server tools to their corresponding agents
            mcp_tool_mapping = {
                'run_oneshot_search': 'splunk_mcp',
                'run_splunk_search': 'splunk_mcp',
                'get_spl_reference': 'splunk_mcp',
                'get_splunk_documentation': 'splunk_mcp',
                'list_spl_commands': 'splunk_mcp',
                'get_splunk_cheat_sheet': 'splunk_mcp'
            }

            # Track which agents we've already added to avoid duplicates
            added_agents = set()

            for tool_name in allowed_tools:
                # Check if this is an MCP server tool
                if tool_name in mcp_tool_mapping:
                    agent_name = mcp_tool_mapping[tool_name]
                    if agent_name not in added_agents:
                        # Get the agent that provides this MCP tool
                        tool_instance = await self.agent_coordinator.get_agent(agent_name)
                        if tool_instance and hasattr(tool_instance, 'execute'):
                            # For SplunkMCPAgent, get the MCP toolset directly instead of wrapping the agent
                            if agent_name == 'splunk_mcp' and hasattr(tool_instance, '_create_mcp_toolset'):
                                logger.debug(f"Getting MCP toolset directly from {agent_name}")
                                mcp_toolset = tool_instance._create_mcp_toolset()
                                if mcp_toolset:
                                    logger.debug(f"Adding MCP toolset directly to micro agent for tools: {[t for t in allowed_tools if t in mcp_tool_mapping]}")
                                    agent_tools.append(mcp_toolset)
                                    added_agents.add(agent_name)
                                else:
                                    logger.warning(f"Could not create MCP toolset from {agent_name}")
                            else:
                                # Get the underlying ADK LlmAgent for other agents (skip if ADK not available)
                                adk_agent = None
                                if hasattr(tool_instance, 'get_llm_agent'):
                                    try:
                                        adk_agent = tool_instance.get_llm_agent()
                                    except RuntimeError as e:
                                        if "ADK LlmAgent is required" in str(e):
                                            logger.debug(f"Skipping ADK agent for '{agent_name}' - ADK not available")
                                            adk_agent = None
                                        else:
                                            raise
                                else:
                                    adk_agent = tool_instance
                                if adk_agent:
                                    logger.debug(f"Adding ADK agent '{agent_name}' for MCP tool '{tool_name}'")
                                    agent_tools.append(AgentTool(agent=adk_agent))
                                    added_agents.add(agent_name)
                                else:
                                    logger.warning(f"Could not get ADK agent from '{agent_name}' for MCP tool '{tool_name}'")
                        else:
                            logger.warning(f"Agent '{agent_name}' for MCP tool '{tool_name}' not found")
                else:
                    # Try to get as a direct agent/tool
                    tool_instance = await self.agent_coordinator.get_agent(tool_name)
                    if tool_instance and hasattr(tool_instance, 'execute'):
                        # Get the underlying ADK LlmAgent for AgentTool (skip if ADK not available)
                        adk_agent = None
                        if hasattr(tool_instance, 'get_llm_agent'):
                            try:
                                adk_agent = tool_instance.get_llm_agent()
                            except RuntimeError as e:
                                if "ADK LlmAgent is required" in str(e):
                                    logger.debug(f"Skipping ADK agent for '{tool_name}' - ADK not available")
                                    adk_agent = None
                                else:
                                    raise
                        else:
                            adk_agent = tool_instance
                        if adk_agent:
                            logger.debug(f"Adding direct ADK agent '{tool_name}' to micro agent")
                            agent_tools.append(AgentTool(agent=adk_agent))
                        else:
                            logger.warning(f"Could not get ADK agent from '{tool_name}'")
                    else:
                        logger.warning(f"Tool '{tool_name}' not found or not executable for micro agent")

            # Check if ADK is available before attempting LlmAgent creation
            try:
                from google.adk import Runner
                from google.adk.agents import LlmAgent
                from google.adk.sessions import InMemorySessionService
                from google.adk.tools.agent_tool import AgentTool
            except ImportError as e:
                logger.warning(f"ADK not available for micro agent {task_id}: {e}")
                logger.info("Skipping LlmAgent creation, will use direct agent coordination")
                return await self._try_direct_agent_coordination(task_metadata, allowed_tools)

            # Verify Google API key is available
            google_api_key = os.getenv('GOOGLE_API_KEY')
            if google_api_key:
                logger.debug(f"✅ Google API key found for micro agent {task_id}")
            else:
                logger.error(f"❌ Google API key NOT found for micro agent {task_id}")
                logger.error(f"❌ Available env vars: {list(os.environ.keys())}")

            # Create the LlmAgent for this specific task
            micro_agent = LlmAgent(
                model=self.config.model.primary_model,
                name=f"MicroAgent_{task_id}",
                description=f"Specialized agent for task: {task_metadata.get('title', task_id)}",
                instruction=instructions,
                tools=agent_tools
            )

            # Create session and runner for execution
            session_service = InMemorySessionService()
            session = await session_service.create_session(
                app_name="micro_agent",
                user_id="system",
                session_id=f"micro_{task_id}"
            )

            runner = Runner(
                agent=micro_agent,
                app_name="micro_agent",
                session_service=session_service
            )

            # Create the execution prompt with context
            execution_prompt = f"Execute the task: {task_metadata.get('title', task_id)}"
            if task_metadata.get('search_query'):
                execution_prompt += f"\nSearch query: {task_metadata['search_query']}"

            # Add context variables to the prompt
            context_vars = config.get('context', {})
            if context_vars:
                execution_prompt += f"\nContext variables: {context_vars}"

            content = types.Content(role="user", parts=[types.Part(text=execution_prompt)])

            # Execute the micro agent and collect results with robust error handling
            response_text = None
            try:
                async for event in runner.run_async(
                    user_id="system",
                    session_id=session.id,
                    new_message=content
                ):
                    if event.is_final_response() and event.content and event.content.parts:
                        response_text = event.content.parts[0].text
                        # Don't break - let generator complete naturally
            except GeneratorExit:
                # Handle generator cleanup gracefully
                logger.debug(f"Generator cleanup for micro agent {task_id}")
            except RuntimeError as runtime_error:
                # Handle MCP client task group issues
                if "cancel scope" in str(runtime_error) or "different task" in str(runtime_error):
                    logger.debug(f"MCP client task group issue for {task_id} (expected): {runtime_error}")
                    # This is a known MCP client library issue - continue with execution
                else:
                    logger.warning(f"Runtime error for micro agent {task_id}: {runtime_error}")
            except Exception as gen_error:
                logger.warning(f"Generator error for micro agent {task_id}: {gen_error}")
                # Continue with whatever response we got

            # Return structured result
            return {
                "task_id": task_id,
                "success": True,
                "response": response_text or "No response received",
                "tools_used": [getattr(tool, 'name', type(tool).__name__) for tool in agent_tools],
                "execution_type": "real_llm_agent"
            }

        except Exception as e:
            logger.error(f"❌ Real micro agent execution failed for {task_id}: {e}", exc_info=True)
            # Instead of simulation, try direct agent coordination
            return await self._try_direct_agent_coordination(task_metadata, allowed_tools)
        finally:
            # Ensure proper cleanup of async resources
            try:
                if 'session_service' in locals() and 'session' in locals():
                    # Clean up session if needed
                    pass  # InMemorySessionService handles cleanup automatically
            except Exception as cleanup_error:
                logger.debug(f"Session cleanup for {task_id}: {cleanup_error}")

    async def _try_direct_agent_coordination(self, task_metadata: dict[str, Any], allowed_tools: list[str]) -> dict[str, Any]:
        """Try direct agent coordination when LlmAgent creation fails."""
        task_id = task_metadata.get('task_id', 'unknown')
        logger.info(f"Attempting direct agent coordination for task {task_id}")

        # Check if we have a search query to execute
        search_query = task_metadata.get('search_query')
        if search_query and self.agent_coordinator:
            try:
                # Use the AgentCoordinator to execute the search directly
                result = await self.agent_coordinator.execute_search(
                    search_query=search_query,
                    parameters=task_metadata.get('parameters', {}),
                    agent_id="splunk_mcp"
                )

                if result.success:
                    return {
                        "task_id": task_id,
                        "success": True,
                        "response": result.data,
                        "tools_used": ["splunk_mcp"],
                        "execution_type": "direct_agent_coordination"
                    }
                else:
                    logger.error(f"Direct agent coordination failed for {task_id}: {result.error}")

            except Exception as coord_error:
                logger.error(f"Agent coordination error for {task_id}: {coord_error}")

        # If direct coordination fails, raise an error
        error_msg = f"Task {task_id} failed: Both LlmAgent creation and direct agent coordination failed"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
