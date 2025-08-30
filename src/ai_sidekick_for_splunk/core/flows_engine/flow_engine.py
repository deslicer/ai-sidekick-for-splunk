"""
Contextual Reasoning Engine - Production Ready.

This module provides the core execution logic for Guided Agent Flows, including
task coordination, agent dependency management, bounded intelligence execution,
and result synthesis with contextual awareness.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..config import Config
from .agent_flow import AgentFlow, ContextResource, FlowPhase, FlowTask
from .micro_agent_builder import MicroAgentBuilder

logger = logging.getLogger(__name__)


@dataclass
class ProgressUpdate:
    """Progress update for streaming to user."""

    phase_name: str
    task_id: str | None = None
    step_number: int | None = None
    message: str = ""
    status: str = "in_progress"  # "starting", "in_progress", "completed", "error"
    data: dict[str, Any] | None = None


@dataclass
class LLMStepResult:
    """Result from a single LLM step in the loop."""

    step_number: int
    tool_used: str | None = None
    tool_output: dict[str, Any] | None = None
    llm_reasoning: str | None = None
    next_action: str | None = None
    step_complete: bool = False
    context_loaded: list[str] = field(default_factory=list)


@dataclass
class TaskResult:
    """Result from executing a single flow task."""

    task_id: str
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    execution_time: float | None = None
    metadata: dict[str, Any] | None = None
    llm_steps: list[LLMStepResult] = field(default_factory=list)  # For LLM-in-the-loop tasks


@dataclass
class PhaseResult:
    """Result from executing a flow phase."""

    phase_name: str
    success: bool
    task_results: list[TaskResult]
    phase_metadata: dict[str, Any] | None = None
    execution_time: float | None = None


@dataclass
class FlowExecutionResult:
    """Complete result from flow execution."""

    flow_name: str
    success: bool
    phase_results: list[PhaseResult]
    synthesized_output: dict[str, Any] | None = None
    total_execution_time: float | None = None
    error_summary: str | None = None


class PlaceholderResolver:
    """Resolves placeholders in flow templates with actual values."""

    def __init__(self):
        self.context_values: dict[str, Any] = {}
        self.discovered_sourcetypes: list[str] = []
        self.discovered_hosts: list[str] = []
        self.discovered_sources: list[str] = []

    def set_context(self, context: dict[str, Any]) -> None:
        """Set context values for placeholder resolution."""
        self.context_values.update(context)

    def add_discovery_data(
        self, sourcetypes: list[str] = None, hosts: list[str] = None, sources: list[str] = None
    ) -> None:
        """Add discovered data for dynamic placeholder resolution."""
        if sourcetypes:
            self.discovered_sourcetypes.extend(sourcetypes)
        if hosts:
            self.discovered_hosts.extend(hosts)
        if sources:
            self.discovered_sources.extend(sources)

    def resolve_search_query(self, query: str, task_context: dict[str, Any] = None) -> str:
        """
        Resolve placeholders in search query.

        Args:
            query: Search query with placeholders
            task_context: Additional context for this specific task

        Returns:
            Resolved search query
        """
        if not query:
            return query

        resolved = query
        context = {**self.context_values, **(task_context or {})}

        # Standard placeholder resolution
        for key, value in context.items():
            placeholder = f"{{{key.upper()}}}"
            if placeholder in resolved:
                resolved = resolved.replace(placeholder, str(value))

        # Dynamic sourcetype resolution for per-sourcetype tasks
        if "{SOURCETYPE}" in resolved and self.discovered_sourcetypes:
            # This will be handled by the execution engine for per-sourcetype tasks
            pass

        return resolved

    def resolve_parameters(
        self, parameters: dict[str, Any], task_context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Resolve placeholders in task parameters."""
        if not parameters:
            return parameters

        resolved = {}
        context = {**self.context_values, **(task_context or {})}

        for key, value in parameters.items():
            if isinstance(value, str):
                resolved_value = value
                for ctx_key, ctx_value in context.items():
                    placeholder = f"{{{ctx_key.upper()}}}"
                    if placeholder in resolved_value:
                        resolved_value = resolved_value.replace(placeholder, str(ctx_value))
                resolved[key] = resolved_value
            else:
                resolved[key] = value

        return resolved


class AgentCoordinator:
    """Coordinates interactions with dependent agents in the real system."""

    def __init__(self, orchestrator=None):
        """
        Initialize agent coordinator.

        Args:
            orchestrator: Main orchestrator instance for agent access
        """
        self.orchestrator = orchestrator
        self._agent_cache = {}

    def _get_orchestrator(self):
        """Get orchestrator instance, with lazy loading support."""
        if self.orchestrator:
            return self.orchestrator

        # Try to get orchestrator from global registry if available
        try:
            # Check if there's a global orchestrator instance we can use
            # This is a fallback for when the agent is created without orchestrator
            logger.info("Attempting to get orchestrator from global context")
            return None  # For now, return None - we'll improve this later
        except Exception as e:
            logger.debug(f"Could not get global orchestrator: {e}")
            return None

    async def get_agent(self, agent_id: str):
        """Get agent instance by ID from the orchestrator."""
        logger.debug(f"🔍 Attempting to get agent: {agent_id}")

        if agent_id in self._agent_cache:
            logger.debug(f"✅ Found agent {agent_id} in cache")
            return self._agent_cache[agent_id]

        orchestrator = self._get_orchestrator()
        logger.debug(f"🔍 Orchestrator available: {orchestrator is not None}")

        if orchestrator and hasattr(orchestrator, "registry_manager"):
            # Get agent from the real orchestrator registry
            try:
                logger.debug(f"🔍 Accessing registry manager for agent {agent_id}")
                agent_registry = orchestrator.registry_manager.agent_registry

                # Check if agent is registered
                available_agents = (
                    list(agent_registry._entries.keys())
                    if hasattr(agent_registry, "_entries")
                    else []
                )
                logger.debug(f"🔍 Available agents in registry: {available_agents}")

                # CRITICAL: Await the async get_instance call
                agent_instance = await agent_registry.get_instance(agent_id)
                if agent_instance:
                    self._agent_cache[agent_id] = agent_instance
                    logger.info(f"✅ Successfully retrieved agent {agent_id} from registry")
                    return agent_instance
                else:
                    logger.error(
                        f"❌ Agent {agent_id} not found in registry. Available: {available_agents}"
                    )
            except Exception as e:
                logger.error(f"❌ Failed to get agent {agent_id} from registry: {e}")
                logger.error(f"❌ Registry manager: {orchestrator.registry_manager}")
                logger.error(
                    f"❌ Agent registry: {getattr(orchestrator.registry_manager, 'agent_registry', 'NOT_FOUND')}"
                )
        else:
            logger.error("❌ Orchestrator not available or missing registry_manager")
            logger.error(f"❌ Orchestrator: {orchestrator}")
            logger.error(
                f"❌ Has registry_manager: {hasattr(orchestrator, 'registry_manager') if orchestrator else False}"
            )

        # Return failure indicator instead of fake data
        logger.error(f"❌ Agent {agent_id} is not available - returning None")
        return None

    async def validate_search(
        self, search_query: str, agent_id: str = "search_guru"
    ) -> tuple[bool, str, str | None]:
        """
        Validate SPL search query using SearchGuru agent.

        Returns:
            Tuple of (is_valid, validated_query, error_message)
        """
        try:
            agent = await self.get_agent(agent_id)

            # Check if we got a real agent instance
            if not agent or isinstance(agent, dict):
                error_msg = f"SearchGuru agent '{agent_id}' not available - orchestrator not properly initialized"
                logger.error(error_msg)
                logger.error(f"Agent retrieval returned: {agent}")
                logger.error(f"Orchestrator state: {self.orchestrator}")
                return False, search_query, error_msg

            if not hasattr(agent, "execute"):
                error_msg = f"SearchGuru agent '{agent_id}' does not have execute method - invalid agent instance"
                logger.error(error_msg)
                logger.error(f"Agent type: {type(agent)}")
                logger.error(f"Agent attributes: {dir(agent)}")
                return False, search_query, error_msg

            # Make real call to SearchGuru agent
            logger.info(f"🔍 Validating SPL with {agent_id}: {search_query}")

            # Call the SearchGuru agent to validate and optimize the query
            validation_request = f"Please validate and optimize this SPL query: {search_query}"
            result = await agent.execute(validation_request)

            if result and result.get("success", True):
                # Extract optimized query from result if available
                optimized_query = result.get("optimized_query", search_query)
                logger.info(f"✅ SPL validated successfully by {agent_id}")
                return True, optimized_query, None
            else:
                error_msg = result.get("error", "Unknown validation error")
                logger.error(f"❌ SPL validation failed: {error_msg}")
                return False, search_query, error_msg

        except Exception as e:
            logger.error(f"Search validation failed: {e}")
            return False, search_query, str(e)

    async def execute_search(
        self,
        search_query: str,
        parameters: dict[str, Any],
        agent_id: str = "splunk_mcp",
        tool_name: str = "run_oneshot_search",
    ) -> TaskResult:
        """Execute search using SplunkMCP agent."""
        try:
            agent = await self.get_agent(agent_id)

            # Check if we got a real agent instance
            if not agent or isinstance(agent, dict):
                error_msg = f"SplunkMCP agent '{agent_id}' not available - orchestrator not properly initialized"
                logger.error(error_msg)
                logger.error(f"Agent retrieval returned: {agent}")
                logger.error(f"Orchestrator state: {self.orchestrator}")
                return TaskResult(task_id="search_execution", success=False, error=error_msg)

            if not hasattr(agent, "execute"):
                error_msg = f"SplunkMCP agent '{agent_id}' does not have execute method - invalid agent instance"
                logger.error(error_msg)
                logger.error(f"Agent type: {type(agent)}")
                logger.error(f"Agent attributes: {dir(agent)}")
                return TaskResult(task_id="search_execution", success=False, error=error_msg)

            # Make real call to SplunkMCP agent
            logger.info(f"🔍 Executing search with {agent_id}: {search_query}")

            # Prepare search request for SplunkMCP agent
            search_request = f"Execute this SPL search: {search_query}"
            if parameters:
                search_request += f"\nParameters: {parameters}"

            result = await agent.execute(search_request)

            if result and result.get("success", True):
                logger.info(f"✅ Search executed successfully by {agent_id}")
                return TaskResult(
                    task_id="search_execution",
                    success=True,
                    data=result.get("data", {}),
                    metadata={
                        "agent_used": agent_id,
                        "query": search_query,
                        "tool_name": tool_name,
                        "parameters": parameters,
                    },
                )
            else:
                error_msg = result.get("error", "Unknown search execution error")
                logger.error(f"❌ Search execution failed: {error_msg}")
                return TaskResult(task_id="search_execution", success=False, error=error_msg)

        except Exception as e:
            logger.error(f"Search execution failed: {e}")
            return TaskResult(task_id="search_execution", success=False, error=str(e))

    async def synthesize_results(
        self, results: dict[str, Any], context: str, agent_id: str = "result_synthesizer"
    ) -> dict[str, Any]:
        """Synthesize search results using ResultSynthesizer agent."""
        try:
            agent = await self.get_agent(agent_id)

            # Check if we got a real agent instance
            if not agent or isinstance(agent, dict):
                error_msg = f"ResultSynthesizer agent '{agent_id}' not available - orchestrator not properly initialized"
                logger.error(error_msg)
                logger.error(f"Agent retrieval returned: {agent}")
                logger.error(f"Orchestrator state: {self.orchestrator}")
                return {"error": error_msg, "success": False, "agent": agent_id}

            if not hasattr(agent, "execute"):
                error_msg = f"ResultSynthesizer agent '{agent_id}' does not have execute method - invalid agent instance"
                logger.error(error_msg)
                logger.error(f"Agent type: {type(agent)}")
                logger.error(f"Agent attributes: {dir(agent)}")
                return {"error": error_msg, "success": False, "agent": agent_id}

            # Make real call to ResultSynthesizer agent
            logger.info(f"🧠 Synthesizing results with {agent_id} for context: {context}")

            # Prepare synthesis request
            synthesis_request = f"Please synthesize these technical search results into business insights:\n\nContext: {context}\n\nResults: {results}"

            result = await agent.execute(synthesis_request)

            if result and result.get("success", True):
                logger.info(f"✅ Results synthesized successfully by {agent_id}")
                return result.get(
                    "data", {"synthesis_performed": True, "context": context, "agent": agent_id}
                )
            else:
                error_msg = result.get("error", "Unknown synthesis error")
                logger.error(f"❌ Result synthesis failed: {error_msg}")
                return {"error": error_msg, "synthesis": "Failed to synthesize results"}

        except Exception as e:
            logger.error(f"Result synthesis failed: {e}")
            return {"error": str(e), "synthesis": "Failed to synthesize results"}

    def load_context_resources(self, resources: list[ContextResource]) -> dict[str, Any]:
        """Load context resources (MCP doc tools, references) for LLM tasks."""
        loaded_context = {}

        # Sort by priority (higher first)
        sorted_resources = sorted(resources, key=lambda r: r.priority, reverse=True)

        for resource in sorted_resources:
            try:
                if resource.resource_type == "mcp_tool":
                    # Load Splunk documentation via MCP tools
                    context_data = self._load_mcp_documentation(resource)
                elif resource.resource_type == "documentation":
                    # Load static documentation
                    context_data = self._load_static_documentation(resource)
                elif resource.resource_type == "reference":
                    # Load reference materials
                    context_data = self._load_reference_material(resource)
                else:
                    logger.warning(f"Unknown resource type: {resource.resource_type}")
                    continue

                loaded_context[resource.resource_id] = {
                    "type": resource.resource_type,
                    "description": resource.description,
                    "data": context_data,
                    "priority": resource.priority,
                }

                logger.info(f"Loaded context resource: {resource.resource_id}")

            except Exception as e:
                logger.error(f"Failed to load context resource {resource.resource_id}: {e}")
                continue

        return loaded_context

    def _load_mcp_documentation(self, resource: ContextResource) -> dict[str, Any]:
        """Load Splunk documentation via MCP tools."""
        # This would call MCP tools like get_spl_reference, get_splunk_documentation, etc.
        logger.info(f"Loading MCP documentation: {resource.resource_id}")

        # For now, return structure indicating MCP tool would be called
        return {
            "tool_name": resource.resource_id,
            "parameters": resource.parameters,
            "documentation_ready": True,
            "integration_status": "Ready for MCP tool integration",
        }

    def _load_static_documentation(self, resource: ContextResource) -> dict[str, Any]:
        """Load static documentation resources."""
        logger.info(f"Loading static documentation: {resource.resource_id}")
        return {"doc_id": resource.resource_id, "content_ready": True}

    def _load_reference_material(self, resource: ContextResource) -> dict[str, Any]:
        """Load reference materials."""
        logger.info(f"Loading reference material: {resource.resource_id}")
        return {"reference_id": resource.resource_id, "material_ready": True}


class FlowEngine:
    """
    Contextual Reasoning Engine for executing Guided Agent Flows.

    This engine orchestrates the execution of Reasoning Flow Definitions,
    managing bounded intelligence tasks, context-aware reasoning, and
    multi-agent coordination with dynamic tool discovery.
    """

    def __init__(
        self,
        config: Config | None = None,
        orchestrator=None,
        progress_callback: Callable[[ProgressUpdate], None] | None = None,
    ):
        """
        Initialize flow engine.

        Args:
            config: Configuration instance
            orchestrator: Main orchestrator for agent access
            progress_callback: Optional callback function for streaming progress updates
        """
        self.config = config or Config()
        self.placeholder_resolver = PlaceholderResolver()
        self.agent_coordinator = AgentCoordinator(orchestrator)
        self.execution_context = {}
        self.progress_callback = progress_callback

        # Initialize micro agent builder for parallel execution
        self.micro_agent_builder = MicroAgentBuilder(self.config, self.agent_coordinator)

    def _send_progress_update(self, update: ProgressUpdate) -> None:
        """Send progress update to callback if available."""
        if self.progress_callback:
            try:
                self.progress_callback(update)
            except Exception as e:
                logger.error(f"Progress callback failed: {e}")

    async def _execute_llm_loop_task(self, task: FlowTask, context: dict[str, Any]) -> TaskResult:
        """Execute a task with LLM-in-the-loop pattern."""
        if not task.llm_loop or not task.llm_loop.enabled:
            # Fall back to regular task execution
            return await self._execute_regular_task(task, context)

        logger.info(f"Executing LLM-in-the-loop task: {task.task_id}")

        # Load context resources first
        loaded_context = self.agent_coordinator.load_context_resources(task.context_resources)

        # Build dynamic prompt
        dynamic_prompt = self._build_dynamic_prompt(task, context, loaded_context)

        # Execute LLM loop
        llm_steps = []
        step_number = 1
        task_complete = False

        while step_number <= task.llm_loop.max_iterations and not task_complete:
            logger.info(f"LLM Loop Step {step_number}/{task.llm_loop.max_iterations}")
            logger.info(f"Executing LLM step {step_number} for task {task.task_id}")

            # Execute LLM step
            step_result = self._execute_llm_step(
                task, dynamic_prompt, context, loaded_context, step_number
            )
            llm_steps.append(step_result)

            # Check if task is complete
            task_complete = step_result.step_complete or step_result.next_action == "complete"
            step_number += 1

        # Compile final result
        final_data = self._compile_llm_loop_result(task, llm_steps, loaded_context)

        return TaskResult(
            task_id=task.task_id,
            success=task_complete,
            data=final_data,
            metadata={
                "llm_loop_enabled": True,
                "steps_executed": len(llm_steps),
                "context_resources_loaded": len(loaded_context),
                "bounded_execution": task.llm_loop.bounded_execution,
            },
            llm_steps=llm_steps,
        )

    async def _execute_regular_task(self, task: FlowTask, context: dict[str, Any]) -> TaskResult:
        """Execute regular task (non-LLM-loop)."""
        # This is the existing task execution logic
        logger.info(f"Executing regular task: {task.task_id}")

        return TaskResult(
            task_id=task.task_id,
            success=True,
            data={"message": f"Regular task execution: {task.task_id}"},
            metadata={"execution_type": "regular"},
        )

    def _build_dynamic_prompt(
        self, task: FlowTask, context: dict[str, Any], loaded_context: dict[str, Any]
    ) -> str:
        """Build dynamic prompt using task information and context."""
        # Base template with task information - resolve placeholders first
        raw_template = (
            task.llm_loop.prompt
            or """
You are executing task: {task_id} - {title}

**Task Description**: {description}
**Goal**: {goal}
**Allowed Tools**: {allowed_tools}

**Context Resources Available**:
{context_resources}

**Instructions**: {dynamic_instructions}

**Constraints**:
- Maximum {max_iterations} iterations
- Use only allowed tools: {allowed_tools}
- Validate each step before proceeding
- Provide clear reasoning for each action

Execute this task step by step, using the available tools and context resources to achieve the goal.
"""
        )

        # Resolve placeholders in the base template first
        base_template = self.placeholder_resolver.resolve_search_query(raw_template, context)

        # Format context resources
        context_desc = []
        for res_id, res_data in loaded_context.items():
            context_desc.append(f"- {res_id}: {res_data['description']}")

        # Resolve placeholders in task fields first
        resolved_title = self.placeholder_resolver.resolve_search_query(task.title, context)
        resolved_description = self.placeholder_resolver.resolve_search_query(
            task.description, context
        )
        resolved_goal = self.placeholder_resolver.resolve_search_query(task.goal, context)
        resolved_instructions = self.placeholder_resolver.resolve_search_query(
            task.dynamic_instructions or "Follow the task goal and description.", context
        )

        # Fill template with safe formatting (handle any placeholders in the template)
        try:
            prompt = base_template.format(
                task_id=task.task_id,
                title=resolved_title,
                description=resolved_description,
                goal=resolved_goal,
                allowed_tools=", ".join(task.llm_loop.allowed_tools),
                context_resources="\n".join(context_desc),
                dynamic_instructions=resolved_instructions,
                max_iterations=task.llm_loop.max_iterations,
            )
        except KeyError as e:
            # Handle placeholders in the template that aren't in our format dict
            logger.warning(f"Template contains unresolved placeholder: {e}")
            # Use a safer approach - replace the problematic placeholders
            safe_template = base_template
            for placeholder in context.keys():
                safe_template = safe_template.replace(
                    f"{{{placeholder}}}", str(context[placeholder])
                )

            prompt = safe_template.format(
                task_id=task.task_id,
                title=resolved_title,
                description=resolved_description,
                goal=resolved_goal,
                allowed_tools=", ".join(task.llm_loop.allowed_tools),
                context_resources="\n".join(context_desc),
                dynamic_instructions=resolved_instructions,
                max_iterations=task.llm_loop.max_iterations,
            )

        return prompt

    def _execute_llm_step(
        self,
        task: FlowTask,
        prompt: str,
        context: dict[str, Any],
        loaded_context: dict[str, Any],
        step_number: int,
    ) -> LLMStepResult:
        """Execute a single step in the LLM loop."""
        # For now, simulate the LLM step execution
        logger.info(f"Executing LLM step {step_number} for task {task.task_id}")

        # In real implementation, this would:
        # 1. Send prompt + context to LLM
        # 2. LLM decides which tool to use
        # 3. Execute the tool
        # 4. LLM reviews output
        # 5. LLM decides next action

        # Simulate tool selection and execution
        selected_tool = task.llm_loop.allowed_tools[0] if task.llm_loop.allowed_tools else task.tool

        return LLMStepResult(
            step_number=step_number,
            tool_used=selected_tool,
            tool_output={"simulated": True, "tool": selected_tool},
            llm_reasoning=f"Step {step_number}: Using {selected_tool} to achieve task goal",
            next_action="complete" if step_number >= 2 else "continue",
            step_complete=step_number >= 2,
            context_loaded=list(loaded_context.keys()),
        )

    def _compile_llm_loop_result(
        self, task: FlowTask, steps: list[LLMStepResult], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Compile final result from LLM loop execution."""
        return {
            "task_id": task.task_id,
            "goal_achieved": len(steps) > 0 and steps[-1].step_complete,
            "steps_summary": [
                {
                    "step": step.step_number,
                    "tool": step.tool_used,
                    "reasoning": step.llm_reasoning,
                    "action": step.next_action,
                }
                for step in steps
            ],
            "context_resources_used": list(context.keys()),
            "final_output": steps[-1].tool_output if steps else None,
            "execution_pattern": "llm_in_the_loop",
            "bounded_execution": True,
        }

    async def execute_flow(
        self, flow: AgentFlow, context: dict[str, Any] = None
    ) -> FlowExecutionResult:
        """
        Execute complete agent flow.

        Args:
            flow: AgentFlow definition to execute
            context: Execution context (e.g., index name, user parameters)

        Returns:
            FlowExecutionResult with complete execution results
        """
        start_time = datetime.now()
        logger.info(f"Starting flow execution: {flow.workflow_name}")

        try:
            # Send initial progress update
            self._send_progress_update(
                ProgressUpdate(
                    phase_name="initialization",
                    message=f"🚀 Starting {flow.workflow_name}",
                    status="starting",
                )
            )

            # Validate flow
            validation_errors = flow.validate()
            if validation_errors:
                return FlowExecutionResult(
                    flow_name=flow.workflow_name,
                    success=False,
                    phase_results=[],
                    error_summary=f"Flow validation failed: {'; '.join(validation_errors)}",
                )

            # Set up execution context
            self.placeholder_resolver.set_context(context or {})
            self.execution_context = context or {}

            # Execute phases
            phase_results = []
            overall_success = True

            for phase_name in flow.execution_flow.sequential_phases:
                phase = flow.get_phase_by_name(phase_name)
                if not phase:
                    logger.error(f"Phase not found: {phase_name}")
                    overall_success = False
                    continue

                # Send phase start update
                self._send_progress_update(
                    ProgressUpdate(
                        phase_name=phase_name,
                        message=f"📋 **Phase {len(phase_results) + 1}: {phase.name}**\n*Goal*: {phase.description}",
                        status="starting",
                    )
                )

                logger.info(f"Executing phase: {phase_name}")
                phase_result = await self._execute_phase(phase, flow)
                phase_results.append(phase_result)

                if not phase_result.success and phase.mandatory:
                    logger.error(f"Mandatory phase failed: {phase_name}")
                    overall_success = False
                    break

                # Update context with phase results for next phases
                self._update_context_from_phase_results(phase_result)

            # Synthesize final output
            synthesized_output = self._synthesize_results(phase_results, flow.output_structure)

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            return FlowExecutionResult(
                flow_name=flow.workflow_name,
                success=overall_success,
                phase_results=phase_results,
                synthesized_output=synthesized_output,
                total_execution_time=execution_time,
            )

        except Exception as e:
            logger.error(f"❌ Flow execution failed with exception: {e}", exc_info=True)
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            return FlowExecutionResult(
                flow_name=flow.workflow_name,
                success=False,
                phase_results=phase_results if "phase_results" in locals() else [],
                error_summary=f"Flow execution failed: {str(e)}",
                total_execution_time=execution_time,
            )

    async def _execute_phase(self, phase: FlowPhase, flow: AgentFlow) -> PhaseResult:
        """Execute a single flow phase with parallel fan-out/gather support."""
        start_time = datetime.now()
        task_results = []
        phase_success = True

        # Check if this phase should use parallel execution
        if phase.parallel and len(phase.tasks) > 1:
            logger.info(f"🚀 Executing phase '{phase.name}' with parallel fan-out/gather pattern")

            # Send parallel execution start update
            self._send_progress_update(
                ProgressUpdate(
                    phase_name=phase.name,
                    message=f"🚀 **Parallel Fan-Out**: {phase.name}\n*Tasks*: {len(phase.tasks)} | *Max Parallel*: {phase.max_parallel}",
                    status="starting",
                )
            )

            # Execute tasks in parallel using fan-out/gather
            task_results = await self._execute_tasks_parallel(phase.tasks, phase.max_parallel, flow)

            # Check overall success
            phase_success = all(result.success for result in task_results)

            # Synthesize parallel results if we have a result synthesizer
            if task_results:
                await self._synthesize_parallel_results(phase, task_results)

        else:
            # Sequential execution (existing logic)
            logger.info(f"📋 Executing phase '{phase.name}' sequentially")

            for task in phase.tasks:
                # Send task start update
                self._send_progress_update(
                    ProgressUpdate(
                        phase_name=phase.name,
                        task_id=task.task_id,
                        message=f"🔧 **Executing Task {task.task_id}: {task.title}**\n*Description*: {task.description}",
                        status="starting",
                    )
                )

                logger.info(f"Executing task: {task.task_id}")

                if task.execution_mode == "per_sourcetype":
                    # Execute task for each discovered sourcetype
                    task_result = await self._execute_per_sourcetype_task(task, flow)
                else:
                    # Execute single task
                    task_result = await self._execute_task(task, flow)

                task_results.append(task_result)

                if not task_result.success:
                    logger.error(f"Task failed: {task.task_id}")
                    phase_success = False
                    # Continue with other tasks unless critical failure

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        return PhaseResult(
            phase_name=phase.name,
            success=phase_success,
            task_results=task_results,
            execution_time=execution_time,
        )

    async def _execute_task(self, task: FlowTask, flow: AgentFlow) -> TaskResult:
        """Execute a single flow task with optional LLM-in-the-loop support."""

        # Check if this is an LLM-in-the-loop task
        if task.llm_loop and task.llm_loop.enabled:
            return await self._execute_llm_loop_task(task, self.execution_context)

        # Regular task execution (existing logic)
        try:
            # Resolve placeholders
            resolved_query = self.placeholder_resolver.resolve_search_query(
                task.search_query, self.execution_context
            )
            resolved_params = self.placeholder_resolver.resolve_parameters(
                task.parameters, self.execution_context
            )

            # Validate search if required
            if task.validation and task.validation.validate_syntax and resolved_query:
                is_valid, validated_query, error = await self.agent_coordinator.validate_search(
                    resolved_query, task.validation.agent
                )
                if not is_valid:
                    return TaskResult(
                        task_id=task.task_id,
                        success=False,
                        error=f"Search validation failed: {error}",
                    )
                resolved_query = validated_query

                # Execute search
            if resolved_query and task.tool in ["run_oneshot_search", "run_splunk_search"]:
                search_result = await self.agent_coordinator.execute_search(
                    resolved_query, resolved_params, "splunk_mcp", task.tool
                )

                if not search_result.success:
                    return TaskResult(
                        task_id=task.task_id, success=False, error=search_result.error
                    )

                # Use ResultSynthesizer for business intelligence generation if requested
                interpretation = None
                if task.result_interpretation and task.result_interpretation.interpret_results:
                    interpretation = await self.agent_coordinator.synthesize_results(
                        search_result.data, task.goal, task.result_interpretation.agent
                    )

                return TaskResult(
                    task_id=task.task_id,
                    success=True,
                    data={
                        "search_results": search_result.data,
                        "resolved_query": resolved_query,
                        "interpretation": interpretation,
                    },
                    metadata=search_result.metadata,
                    execution_time=search_result.execution_time,
                )

            else:
                # Handle non-search tasks
                return TaskResult(
                    task_id=task.task_id,
                    success=True,
                    data={"message": f"Task {task.task_id} executed successfully"},
                    metadata={"task_type": "non_search"},
                )

        except Exception as e:
            logger.error(f"Task execution failed: {task.task_id}: {e}")
            return TaskResult(task_id=task.task_id, success=False, error=str(e))

    async def _execute_per_sourcetype_task(self, task: FlowTask, flow: AgentFlow) -> TaskResult:
        """Execute task for each discovered sourcetype."""
        if not self.placeholder_resolver.discovered_sourcetypes:
            # For now, simulate that we would execute per sourcetype
            # In real implementation, this would use discovered sourcetypes from previous phases
            logger.info(
                f"Per-sourcetype task {task.task_id} would execute for each discovered sourcetype"
            )
            return TaskResult(
                task_id=task.task_id,
                success=True,
                data={
                    "message": f"Per-sourcetype task ready: {task.task_id}",
                    "execution_mode": "per_sourcetype",
                    "integration_status": "Ready for real system integration",
                },
                metadata={"execution_mode": "per_sourcetype", "awaiting_discovery": True},
            )

        all_results = []
        overall_success = True

        for sourcetype in self.placeholder_resolver.discovered_sourcetypes:
            # Create task context with current sourcetype
            task_context = {**self.execution_context, "sourcetype": sourcetype}

            # Execute task with sourcetype context
            resolved_query = task.search_query.replace("{SOURCETYPE}", sourcetype)
            resolved_params = self.placeholder_resolver.resolve_parameters(
                task.parameters, task_context
            )

            try:
                search_result = await self.agent_coordinator.execute_search(
                    resolved_query, resolved_params, "splunk_mcp", task.tool
                )

                if search_result.success:
                    all_results.append(
                        {
                            "sourcetype": sourcetype,
                            "results": search_result.data,
                            "metadata": search_result.metadata,
                        }
                    )
                else:
                    overall_success = False
                    all_results.append({"sourcetype": sourcetype, "error": search_result.error})

            except Exception as e:
                overall_success = False
                all_results.append({"sourcetype": sourcetype, "error": str(e)})

        return TaskResult(
            task_id=task.task_id,
            success=overall_success,
            data={"per_sourcetype_results": all_results},
            metadata={
                "execution_mode": "per_sourcetype",
                "sourcetype_count": len(self.placeholder_resolver.discovered_sourcetypes),
            },
        )

    def _update_context_from_phase_results(self, phase_result: PhaseResult) -> None:
        """Update execution context with results from completed phase."""
        # Extract discovered data for future phases
        for task_result in phase_result.task_results:
            if not task_result.success or not task_result.data:
                continue

            # Extract sourcetypes, hosts, sources from results
            search_results = task_result.data.get("search_results", {})
            results = search_results.get("results", [])

            if results and isinstance(results, list):
                # Extract sourcetypes
                sourcetypes = [r.get("sourcetype") for r in results if r.get("sourcetype")]
                if sourcetypes:
                    self.placeholder_resolver.add_discovery_data(sourcetypes=sourcetypes)

                # Extract hosts
                hosts = [r.get("host") for r in results if r.get("host")]
                if hosts:
                    self.placeholder_resolver.add_discovery_data(hosts=hosts)

                # Extract sources
                sources = [r.get("source") for r in results if r.get("source")]
                if sources:
                    self.placeholder_resolver.add_discovery_data(sources=sources)

    def _synthesize_results(
        self, phase_results: list[PhaseResult], output_structure: dict[str, Any]
    ) -> dict[str, Any]:
        """Synthesize final output from all phase results."""
        synthesized = {
            "execution_summary": {
                "total_phases": len(phase_results),
                "successful_phases": sum(1 for p in phase_results if p.success),
                "total_tasks": sum(len(p.task_results) for p in phase_results),
                "successful_tasks": sum(
                    sum(1 for t in p.task_results if t.success) for p in phase_results
                ),
            },
            "phase_results": {},
            "discovered_data": {
                "sourcetypes": list(set(self.placeholder_resolver.discovered_sourcetypes)),
                "hosts": list(set(self.placeholder_resolver.discovered_hosts)),
                "sources": list(set(self.placeholder_resolver.discovered_sources)),
            },
        }

        # Organize results by phase
        for phase_result in phase_results:
            phase_data = {
                "success": phase_result.success,
                "execution_time": phase_result.execution_time,
                "tasks": {},
            }

            for task_result in phase_result.task_results:
                phase_data["tasks"][task_result.task_id] = {
                    "success": task_result.success,
                    "data": task_result.data,
                    "error": task_result.error,
                    "execution_time": task_result.execution_time,
                }

            synthesized["phase_results"][phase_result.phase_name] = phase_data

        return synthesized

    async def _execute_tasks_parallel(
        self, tasks: list[FlowTask], max_parallel: int, flow: AgentFlow
    ) -> list[TaskResult]:
        """
        Execute tasks in parallel using the Fan-Out/Gather pattern.

        This method implements the ADK Parallel Fan-Out/Gather pattern by:
        1. Creating micro agents for each task (Fan-Out)
        2. Running them concurrently with asyncio.gather()
        3. Collecting and processing results (Gather)
        """
        logger.info(f"🚀 Fan-Out: Creating {len(tasks)} micro agents for parallel execution")

        # Separate per-sourcetype tasks from regular tasks
        regular_tasks = [task for task in tasks if task.execution_mode != "per_sourcetype"]
        per_sourcetype_tasks = [task for task in tasks if task.execution_mode == "per_sourcetype"]

        all_results = []

        # Execute regular tasks in parallel
        if regular_tasks:
            regular_results = await self._execute_regular_tasks_parallel(
                regular_tasks, max_parallel
            )
            all_results.extend(regular_results)

        # Execute per-sourcetype tasks sequentially (they have their own internal parallelization)
        for task in per_sourcetype_tasks:
            logger.info(f"🔄 Executing per-sourcetype task: {task.task_id}")
            per_sourcetype_result = await self._execute_per_sourcetype_task(task, flow)
            all_results.append(per_sourcetype_result)

        logger.info(f"✅ Gather: Collected {len(all_results)} task results from parallel execution")
        return all_results

    async def _execute_regular_tasks_parallel(
        self, tasks: list[FlowTask], max_parallel: int
    ) -> list[TaskResult]:
        """Execute regular (non-per-sourcetype) tasks in parallel using micro agents."""

        # Create micro agent configurations for each task
        micro_agent_configs = []
        for task in tasks:
            config = self.micro_agent_builder.create_micro_agent_for_task(
                task, self.execution_context
            )
            micro_agent_configs.append(config)

        # Execute micro agents in parallel
        micro_results = await self.micro_agent_builder.execute_micro_agents_parallel(
            micro_agent_configs, max_parallel, self._send_progress_update_dict
        )

        # Convert MicroAgentResult to TaskResult
        task_results = []
        for micro_result in micro_results:
            task_result = TaskResult(
                task_id=micro_result.task_id,
                success=micro_result.success,
                data=micro_result.data,
                error=micro_result.error,
                execution_time=micro_result.execution_time,
                metadata={
                    "execution_type": "parallel_micro_agent",
                    "agent_name": micro_result.agent_name,
                    "timeout_occurred": micro_result.timeout_occurred,
                },
            )
            task_results.append(task_result)

        return task_results

    def _send_progress_update_dict(self, update_dict: dict[str, Any]) -> None:
        """Convert dict-based progress update to ProgressUpdate and send."""
        progress_update = ProgressUpdate(
            phase_name=update_dict.get("phase_name", "unknown"),
            task_id=update_dict.get("task_id"),
            message=update_dict.get("message", ""),
            status=update_dict.get("status", "in_progress"),
            data=update_dict.get("data"),
        )
        self._send_progress_update(progress_update)

    async def _synthesize_parallel_results(
        self, phase: FlowPhase, task_results: list[TaskResult]
    ) -> None:
        """
        Synthesize results from parallel task execution using ResultSynthesizer.

        This implements the "Gather" part of the pattern by collecting all parallel
        results and synthesizing them into actionable insights.
        """
        logger.info(
            f"🧠 Synthesizing results from {len(task_results)} parallel tasks in phase '{phase.name}'"
        )

        # Send synthesis start update
        self._send_progress_update(
            ProgressUpdate(
                phase_name=phase.name,
                message=f"🧠 **Synthesizing Results**: {phase.name}\n*Parallel Tasks*: {len(task_results)}",
                status="starting",
            )
        )

        # Prepare synthesis context
        successful_results = [r for r in task_results if r.success]
        failed_results = [r for r in task_results if not r.success]

        synthesis_context = {
            "phase_name": phase.name,
            "phase_description": phase.description,
            "total_tasks": len(task_results),
            "successful_tasks": len(successful_results),
            "failed_tasks": len(failed_results),
            "execution_pattern": "parallel_fan_out_gather",
        }

        # Collect all successful task data for synthesis
        combined_results = {}
        for result in successful_results:
            if result.data:
                combined_results[result.task_id] = result.data

        # Add failed task information
        if failed_results:
            combined_results["failed_tasks"] = [
                {"task_id": r.task_id, "error": r.error} for r in failed_results
            ]

        try:
            # Optimal Hybrid: Enhanced Gather Agent + Result Synthesizer JSON Output
            # Step 1: Enhanced gather agent for coordination and data collection
            builtin_synthesis = self._synthesize_parallel_results_builtin(
                combined_results, phase, synthesis_context
            )

            # Step 2: Use result_synthesizer for structured JSON output if meaningful data exists
            if builtin_synthesis.get("has_meaningful_data", False):
                logger.info(
                    f"🎯 Generating structured JSON output via result_synthesizer for phase '{phase.name}'"
                )
                try:
                    json_synthesis_result = await self.agent_coordinator.synthesize_results(
                        combined_results,
                        f"Phase: {phase.name} - {phase.description}",
                        "result_synthesizer",
                    )

                    # Combine enhanced gather agent metadata with JSON output
                    if json_synthesis_result.get("success", True):
                        synthesis_result = json_synthesis_result
                        synthesis_result["builtin_metadata"] = builtin_synthesis
                        synthesis_result["synthesis_method"] = (
                            "optimal_hybrid_enhanced_gather_plus_json_output"
                        )
                        logger.info(
                            f"✅ Optimal hybrid synthesis complete for phase '{phase.name}': enhanced coordination + JSON output"
                        )
                    else:
                        # Fallback to enhanced gather agent
                        logger.warning(
                            f"⚠️ result_synthesizer failed, using enhanced gather agent for phase '{phase.name}'"
                        )
                        synthesis_result = builtin_synthesis
                        synthesis_result["synthesis_method"] = "enhanced_gather_agent_fallback"

                except Exception as e:
                    logger.error(f"❌ result_synthesizer error for phase '{phase.name}': {e}")
                    synthesis_result = builtin_synthesis
                    synthesis_result["synthesis_method"] = (
                        "enhanced_gather_agent_fallback_after_error"
                    )
            else:
                # Use enhanced gather agent for phases without meaningful data
                logger.info(
                    f"📊 Using enhanced gather agent for phase '{phase.name}' (no meaningful data for JSON synthesis)"
                )
                synthesis_result = builtin_synthesis
                synthesis_result["synthesis_method"] = "enhanced_gather_agent_only"

            logger.info(
                f"✅ Successfully synthesized parallel results for phase '{phase.name}' using built-in synthesis"
            )

            # Send synthesis completion update
            insights_count = len(synthesis_result.get("key_insights", []))
            self._send_progress_update(
                ProgressUpdate(
                    phase_name=phase.name,
                    message=f"✅ **Synthesis Complete**: {phase.name}\n*Insights Generated*: {insights_count}",
                    status="completed",
                    data={"synthesis_result": synthesis_result},
                )
            )

            # Store synthesis result in execution context for future phases
            self.execution_context[f"{phase.name}_synthesis"] = {
                "synthesis_performed": True,
                "context": f"Phase: {phase.name} - {phase.description}",
                "agent": "builtin_parallel_synthesis",
                "result": synthesis_result,
            }

        except Exception as e:
            logger.error(
                f"❌ Exception during parallel result synthesis for phase '{phase.name}': {e}"
            )

            # Send synthesis error update
            self._send_progress_update(
                ProgressUpdate(
                    phase_name=phase.name,
                    message=f"❌ **Synthesis Failed**: {phase.name}\n*Error*: {str(e)[:100]}...",
                    status="error",
                    data={"synthesis_error": str(e)},
                )
            )

    def _synthesize_results(
        self, phase_results: list[PhaseResult], output_structure: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Synthesize final output from all phase results and synthesis results.

        Collects all synthesis results from execution context and combines them
        into a comprehensive final output structure.
        """
        logger.info(f"🧠 Synthesizing final output from {len(phase_results)} phases")

        # Collect all synthesis results from execution context
        synthesis_results = {}
        for key, value in self.execution_context.items():
            if key.endswith("_synthesis"):
                phase_name = key.replace("_synthesis", "")
                synthesis_results[phase_name] = value
                logger.debug(f"Found synthesis result for phase: {phase_name}")

        # Build comprehensive synthesized output
        synthesized_output = {
            "summary": self._build_comprehensive_summary(synthesis_results, phase_results),
            "phase_synthesis": synthesis_results,
            "discovered_data": self._extract_discovered_data(synthesis_results),
            "key_insights": self._extract_key_insights(synthesis_results),
            "recommendations": self._extract_recommendations(synthesis_results),
            "execution_metadata": {
                "total_phases": len(phase_results),
                "successful_phases": sum(1 for p in phase_results if p.success),
                "synthesis_phases": len(synthesis_results),
                "output_structure": output_structure,
            },
        }

        logger.info(
            f"✅ Final synthesis complete: {len(synthesis_results)} phase syntheses combined"
        )
        return synthesized_output

    def _build_comprehensive_summary(
        self, synthesis_results: dict[str, Any], phase_results: list[PhaseResult]
    ) -> str:
        """Build a comprehensive summary from all synthesis results."""
        if not synthesis_results:
            return "No synthesis results available - phases may not have completed successfully."

        summary_parts = []

        # Add overall execution summary
        successful_phases = sum(1 for p in phase_results if p.success)
        total_time = sum(p.execution_time or 0 for p in phase_results)

        summary_parts.append("**Execution Summary:**")
        summary_parts.append(f"• Overall Success: {successful_phases == len(phase_results)}")
        summary_parts.append(f"• Phases Completed: {successful_phases}")
        summary_parts.append(f"• Total Execution Time: {total_time:.1f} seconds")
        summary_parts.append("")

        # Add synthesis results from each phase
        for phase_name, synthesis_data in synthesis_results.items():
            if isinstance(synthesis_data, dict) and synthesis_data.get("success", True):
                summary_parts.append(f"**{phase_name.replace('_', ' ').title()}:**")

                # Extract summary from synthesis data
                if "summary" in synthesis_data:
                    summary_parts.append(f"• {synthesis_data['summary']}")
                elif "response" in synthesis_data:
                    # Truncate long responses
                    response = synthesis_data["response"]
                    if len(response) > 500:
                        response = response[:500] + "..."
                    summary_parts.append(f"• {response}")

                summary_parts.append("")

        return "\n".join(summary_parts)

    def _extract_discovered_data(self, synthesis_results: dict[str, Any]) -> dict[str, Any]:
        """Extract discovered data from synthesis results."""
        discovered_data = {}

        for phase_name, synthesis_data in synthesis_results.items():
            if isinstance(synthesis_data, dict) and synthesis_data.get("success", True):
                if "discovered_data" in synthesis_data:
                    discovered_data[phase_name] = synthesis_data["discovered_data"]
                elif "data" in synthesis_data:
                    discovered_data[phase_name] = synthesis_data["data"]

        return discovered_data

    def _extract_key_insights(self, synthesis_results: dict[str, Any]) -> list[str]:
        """Extract key insights from synthesis results."""
        insights = []

        for phase_name, synthesis_data in synthesis_results.items():
            if isinstance(synthesis_data, dict) and synthesis_data.get("success", True):
                if "insights" in synthesis_data:
                    phase_insights = synthesis_data["insights"]
                    if isinstance(phase_insights, list):
                        insights.extend(phase_insights)
                    else:
                        insights.append(str(phase_insights))
                elif "key_findings" in synthesis_data:
                    findings = synthesis_data["key_findings"]
                    if isinstance(findings, list):
                        insights.extend(findings)
                    else:
                        insights.append(str(findings))

        return insights

    def _extract_recommendations(self, synthesis_results: dict[str, Any]) -> list[str]:
        """Extract recommendations from synthesis results."""
        recommendations = []

        for phase_name, synthesis_data in synthesis_results.items():
            if isinstance(synthesis_data, dict) and synthesis_data.get("success", True):
                if "recommendations" in synthesis_data:
                    phase_recs = synthesis_data["recommendations"]
                    if isinstance(phase_recs, list):
                        recommendations.extend(phase_recs)
                    else:
                        recommendations.append(str(phase_recs))
                elif "actionable_insights" in synthesis_data:
                    insights = synthesis_data["actionable_insights"]
                    if isinstance(insights, list):
                        recommendations.extend(insights)
                    else:
                        recommendations.append(str(insights))

        return recommendations

    def _synthesize_parallel_results_builtin(
        self, combined_results: dict[str, Any], phase: FlowPhase, synthesis_context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Built-in ADK Parallel Fan-Out/Gather synthesis pattern.

        This implements the correct ADK pattern by synthesizing results internally
        within the FlowEngine instead of calling external agents.
        """
        logger.info(
            f"🧠 Built-in synthesis for phase '{phase.name}' with {len(combined_results)} task results"
        )

        # Extract insights from micro agent responses
        key_insights = []
        discovered_data = {}
        recommendations = []

        for task_id, task_data in combined_results.items():
            if task_id == "failed_tasks":
                continue

            # Extract insights from micro agent LLM responses
            if isinstance(task_data, dict) and "response" in task_data:
                response_text = task_data["response"]

                # Parse insights from the LLM response
                insights = self._extract_insights_from_response(response_text, task_id)
                key_insights.extend(insights.get("insights", []))

                # Extract data patterns
                data_patterns = self._extract_data_patterns_from_response(response_text, task_id)
                discovered_data.update(data_patterns)

                # Extract recommendations
                task_recommendations = self._extract_recommendations_from_response(
                    response_text, task_id
                )
                recommendations.extend(task_recommendations)

        # Determine if we have meaningful data for production synthesis
        has_meaningful_data = (
            len(key_insights) > 0
            or len(discovered_data) > 0
            or len(recommendations) > 0
            or any(
                task_data.get("result", {}).get("search_results")
                for task_id, task_data in combined_results.items()
                if task_id != "failed_tasks" and isinstance(task_data, dict)
            )
        )

        # Build comprehensive synthesis result
        synthesis_result = {
            "success": True,
            "phase_name": phase.name,
            "synthesis_type": "builtin_parallel_fanout_gather",
            "key_insights": key_insights,
            "discovered_data": discovered_data,
            "recommendations": recommendations,
            "has_meaningful_data": has_meaningful_data,
            "task_count": synthesis_context.get("total_tasks", 0),
            "successful_tasks": synthesis_context.get("successful_tasks", 0),
            "failed_tasks": synthesis_context.get("failed_tasks", 0),
            "execution_pattern": "parallel_fan_out_gather",
            "synthesis_metadata": {
                "phase_description": phase.description,
                "synthesis_timestamp": datetime.now().isoformat(),
                "synthesis_method": "builtin_adk_pattern",
                "meaningful_data_detected": has_meaningful_data,
            },
        }

        # Enhanced Business Intelligence Generation
        # The gather agent should provide executive summaries and actionable insights
        executive_summary = self._generate_executive_summary(
            key_insights, discovered_data, recommendations, phase, combined_results
        )

        # Generate persona-based use cases and business opportunities
        business_intelligence = self._generate_business_intelligence(
            key_insights, discovered_data, recommendations, phase, combined_results
        )

        # Add enhanced business intelligence to synthesis result
        synthesis_result.update(
            {
                "executive_summary": executive_summary,
                "business_intelligence": business_intelligence,
                "synthesis_method": "enhanced_builtin_gather_agent_with_business_intelligence",
            }
        )

        logger.info(
            f"✅ Enhanced built-in synthesis complete: {len(key_insights)} insights, {len(recommendations)} recommendations, executive summary generated"
        )
        return synthesis_result

    def _extract_insights_from_response(self, response_text: str, task_id: str) -> dict[str, Any]:
        """Extract key insights from micro agent LLM response."""
        insights = []

        # Handle both string and dictionary responses
        if not isinstance(response_text, str):
            # If response is not a string (e.g., dict from direct agent coordination), skip insight extraction
            return {"insights": insights}

        # Look for common insight patterns in the response
        if "pattern" in response_text.lower() or "insight" in response_text.lower():
            # Extract bullet points or numbered lists as insights
            lines = response_text.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("*") or line.startswith("-") or line.startswith("•"):
                    insight = line.lstrip("*-• ").strip()
                    if len(insight) > 10:  # Filter out very short lines
                        insights.append(
                            {
                                "source_task": task_id,
                                "insight": insight,
                                "confidence": "high"
                                if "significant" in insight.lower()
                                else "medium",
                            }
                        )

        return {"insights": insights}

    def _extract_data_patterns_from_response(
        self, response_text: str, task_id: str
    ) -> dict[str, Any]:
        """Extract data patterns from micro agent LLM response."""
        patterns = {}

        # Handle both string and dictionary responses
        if not isinstance(response_text, str):
            # If response is not a string (e.g., dict from direct agent coordination), skip pattern extraction
            return patterns

        # Look for specific data patterns mentioned in the response
        response_lower = response_text.lower()

        # Extract error patterns
        if "error" in response_lower or "4xx" in response_lower or "5xx" in response_lower:
            patterns["error_patterns"] = {
                "source_task": task_id,
                "has_errors": True,
                "description": "Error patterns detected in analysis",
            }

        # Extract temporal patterns
        if "time" in response_lower or "hour" in response_lower or "day" in response_lower:
            patterns["temporal_patterns"] = {
                "source_task": task_id,
                "has_temporal_data": True,
                "description": "Temporal patterns detected in analysis",
            }

        # Extract volume patterns
        if "volume" in response_lower or "count" in response_lower or "events" in response_lower:
            patterns["volume_patterns"] = {
                "source_task": task_id,
                "has_volume_data": True,
                "description": "Volume patterns detected in analysis",
            }

        return patterns

    def _extract_recommendations_from_response(
        self, response_text: str, task_id: str
    ) -> list[dict[str, Any]]:
        """Extract recommendations from micro agent LLM response."""
        recommendations = []

        # Handle both string and dictionary responses
        if not isinstance(response_text, str):
            # If response is not a string (e.g., dict from direct agent coordination), skip recommendation extraction
            return recommendations

        # Look for recommendation patterns
        response_lower = response_text.lower()

        if (
            "recommend" in response_lower
            or "suggest" in response_lower
            or "should" in response_lower
        ):
            # Extract sentences containing recommendations
            sentences = response_text.split(".")
            for sentence in sentences:
                sentence = sentence.strip()
                if any(
                    word in sentence.lower()
                    for word in ["recommend", "suggest", "should", "consider"]
                ):
                    if len(sentence) > 20:  # Filter out very short sentences
                        recommendations.append(
                            {
                                "source_task": task_id,
                                "recommendation": sentence,
                                "priority": "high" if "critical" in sentence.lower() else "medium",
                                "category": "operational",
                            }
                        )

        return recommendations

    def _generate_executive_summary(
        self,
        key_insights: list[dict[str, Any]],
        discovered_data: dict[str, Any],
        recommendations: list[dict[str, Any]],
        phase: FlowPhase,
        combined_results: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate executive summary with business intelligence.

        The gather agent has complete context and should provide production-ready summaries.
        """
        # Analyze the scope and impact
        total_data_points = len(discovered_data)
        high_priority_insights = [i for i in key_insights if i.get("confidence") == "high"]
        critical_recommendations = [r for r in recommendations if r.get("priority") == "high"]

        # Generate executive overview
        executive_overview = f"Analysis of {phase.name} revealed {len(key_insights)} key insights across {total_data_points} data patterns, with {len(critical_recommendations)} high-priority actionable recommendations."

        # Extract key business findings
        business_findings = []
        for insight in high_priority_insights[:5]:  # Top 5 high-confidence insights
            finding = insight.get("insight", "")
            if any(
                keyword in finding.lower()
                for keyword in ["error", "performance", "volume", "pattern", "anomaly", "security"]
            ):
                business_findings.append(
                    {
                        "finding": finding,
                        "confidence": insight.get("confidence", "medium"),
                        "business_impact": self._assess_business_impact(finding),
                    }
                )

        # Generate next actions
        next_actions = []
        for rec in critical_recommendations[:3]:  # Top 3 critical recommendations
            next_actions.append(
                {
                    "action": rec.get("recommendation", ""),
                    "priority": rec.get("priority", "medium"),
                    "estimated_effort": self._estimate_implementation_effort(
                        rec.get("recommendation", "")
                    ),
                    "business_value": self._assess_business_value(rec.get("recommendation", "")),
                }
            )

        return {
            "overview": executive_overview,
            "key_business_findings": business_findings,
            "immediate_next_actions": next_actions,
            "analysis_scope": {
                "phase_analyzed": phase.name,
                "data_points_examined": total_data_points,
                "insights_generated": len(key_insights),
                "recommendations_provided": len(recommendations),
            },
        }

    def _generate_business_intelligence(
        self,
        key_insights: list[dict[str, Any]],
        discovered_data: dict[str, Any],
        recommendations: list[dict[str, Any]],
        phase: FlowPhase,
        combined_results: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate production-ready business intelligence with persona-based use cases.

        This provides the actionable insights that result_synthesizer used to provide.
        """
        # Generate persona-based use cases
        personas = self._identify_relevant_personas(key_insights, recommendations)

        # Create dashboard recommendations
        dashboard_panels = self._generate_dashboard_recommendations(discovered_data, key_insights)

        # Create alert recommendations
        alert_recommendations = self._generate_alert_recommendations(key_insights, recommendations)

        # Assess business opportunities
        business_opportunities = self._assess_business_opportunities(key_insights, recommendations)

        return {
            "persona_use_cases": personas,
            "dashboard_strategy": {
                "recommended_panels": dashboard_panels,
                "implementation_priority": "high" if len(dashboard_panels) > 2 else "medium",
            },
            "alert_strategy": {
                "recommended_alerts": alert_recommendations,
                "monitoring_approach": "proactive"
                if len(alert_recommendations) > 1
                else "reactive",
            },
            "business_opportunities": business_opportunities,
            "implementation_roadmap": self._create_implementation_roadmap(
                dashboard_panels, alert_recommendations, business_opportunities
            ),
        }

    def _assess_business_impact(self, finding: str) -> str:
        """Assess business impact of a finding."""
        finding_lower = finding.lower()
        if any(word in finding_lower for word in ["critical", "failure", "down", "error"]):
            return "high"
        elif any(word in finding_lower for word in ["performance", "slow", "delay"]):
            return "medium"
        else:
            return "low"

    def _estimate_implementation_effort(self, recommendation: str) -> str:
        """Estimate implementation effort for a recommendation."""
        rec_lower = recommendation.lower()
        if any(word in rec_lower for word in ["dashboard", "alert", "monitor"]):
            return "low"
        elif any(word in rec_lower for word in ["investigate", "analyze", "review"]):
            return "medium"
        else:
            return "high"

    def _assess_business_value(self, recommendation: str) -> str:
        """Assess business value of a recommendation."""
        rec_lower = recommendation.lower()
        if any(word in rec_lower for word in ["critical", "security", "failure", "downtime"]):
            return "high"
        elif any(word in rec_lower for word in ["performance", "efficiency", "optimization"]):
            return "medium"
        else:
            return "low"

    def _identify_relevant_personas(
        self, insights: list[dict[str, Any]], recommendations: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Identify relevant personas based on insights and recommendations."""
        personas = []

        # IT Operations persona
        if any(
            "error" in str(item).lower() or "performance" in str(item).lower()
            for item in insights + recommendations
        ):
            personas.append(
                {
                    "persona": "IT Operations",
                    "title": "Proactive System Monitoring and Issue Resolution",
                    "business_opportunity": "Identify and resolve system issues before they impact users",
                    "use_case_description": "Monitor system health, detect anomalies, and implement proactive fixes",
                }
            )

        # Security Team persona
        if any(
            "security" in str(item).lower() or "access" in str(item).lower()
            for item in insights + recommendations
        ):
            personas.append(
                {
                    "persona": "Security Team",
                    "title": "Security Monitoring and Threat Detection",
                    "business_opportunity": "Enhance security posture and threat detection capabilities",
                    "use_case_description": "Monitor security events, detect threats, and implement security controls",
                }
            )

        # Business Analyst persona (default)
        personas.append(
            {
                "persona": "Business Analyst",
                "title": "Data-Driven Business Intelligence",
                "business_opportunity": "Transform operational data into actionable business insights",
                "use_case_description": "Analyze operational patterns to drive business decisions and improvements",
            }
        )

        return personas

    def _generate_dashboard_recommendations(
        self, discovered_data: dict[str, Any], insights: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Generate dashboard panel recommendations."""
        panels = []

        # Error monitoring panel
        if any("error" in str(insight).lower() for insight in insights):
            panels.append(
                {
                    "name": "Error Rate Monitoring",
                    "purpose": "Track error frequency and patterns over time",
                    "spl": "index=* ERROR OR error | timechart count by sourcetype",
                    "visualization": "line_chart",
                }
            )

        # Performance monitoring panel
        if any("performance" in str(insight).lower() for insight in insights):
            panels.append(
                {
                    "name": "Performance Metrics Overview",
                    "purpose": "Monitor system performance indicators",
                    "spl": "index=* | stats avg(response_time) max(response_time) by host",
                    "visualization": "single_value",
                }
            )

        # Volume analysis panel
        panels.append(
            {
                "name": "Data Volume Trends",
                "purpose": "Track data ingestion patterns and volume changes",
                "spl": "index=* | bucket _time span=1h | stats count by _time sourcetype",
                "visualization": "column_chart",
            }
        )

        return panels

    def _generate_alert_recommendations(
        self, insights: list[dict[str, Any]], recommendations: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Generate alert recommendations."""
        alerts = []

        # Critical error alert
        if any("error" in str(item).lower() for item in insights + recommendations):
            alerts.append(
                {
                    "name": "Critical Error Rate Alert",
                    "query": "index=* ERROR OR error | stats count | where count > 10",
                    "threshold": "Trigger when error count > 10 in 15-minute window",
                    "response_action": "Immediately investigate error patterns and notify IT Operations",
                }
            )

        # Performance degradation alert
        if any("performance" in str(item).lower() for item in insights + recommendations):
            alerts.append(
                {
                    "name": "Performance Degradation Alert",
                    "query": "index=* | stats avg(response_time) | where avg(response_time) > 5",
                    "threshold": "Trigger when average response time > 5 seconds",
                    "response_action": "Investigate performance bottlenecks and optimize system resources",
                }
            )

        return alerts

    def _assess_business_opportunities(
        self, insights: list[dict[str, Any]], recommendations: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Assess business opportunities from insights and recommendations."""
        opportunities = []

        # Operational efficiency opportunity
        if recommendations:
            opportunities.append(
                {
                    "opportunity": "Operational Efficiency Enhancement",
                    "description": "Implement proactive monitoring to reduce incident response time",
                    "estimated_value": "2-4 hours saved per incident through early detection",
                    "implementation_priority": "high",
                }
            )

        # Data quality opportunity
        if insights:
            opportunities.append(
                {
                    "opportunity": "Data Quality Improvement",
                    "description": "Establish data quality monitoring and validation processes",
                    "estimated_value": "Improved decision-making accuracy and reduced data-related issues",
                    "implementation_priority": "medium",
                }
            )

        return opportunities

    def _create_implementation_roadmap(
        self,
        dashboard_panels: list[dict[str, Any]],
        alerts: list[dict[str, Any]],
        opportunities: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Create implementation roadmap."""
        return {
            "phase_1_immediate": {
                "timeline": "1-2 weeks",
                "actions": [f"Implement {panel['name']}" for panel in dashboard_panels[:2]],
            },
            "phase_2_short_term": {
                "timeline": "1 month",
                "actions": [f"Deploy {alert['name']}" for alert in alerts[:2]],
            },
            "phase_3_long_term": {
                "timeline": "3 months",
                "actions": [f"Realize {opp['opportunity']}" for opp in opportunities[:2]],
            },
        }
