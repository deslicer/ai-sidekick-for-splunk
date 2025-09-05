"""
FlowPilot - Universal Workflow Agent.

The FlowPilot is a universal agent that can execute any JSON-defined workflow
using the Guided Agent Flows framework. It dynamically adapts its behavior
based on the loaded workflow template, making it the foundation for the
community-first, enterprise-scalable architecture.

"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Optional

from google.adk.agents import LlmAgent

from ...base_agent import AgentMetadata, BaseAgent
from ...config import Config
from ...flows_engine.agent_flow import AgentFlow
from ...flows_engine.flow_engine import FlowEngine, FlowExecutionResult, ProgressUpdate

logger = logging.getLogger(__name__)


class FlowPilot(BaseAgent):
    """
    Universal Workflow Agent - The FlowPilot.

    FlowPilot can execute any JSON-defined workflow using the Guided Agent Flows
    framework. It dynamically generates instructions, tools, and behavior based
    on the loaded workflow template.

    """

    def __init__(
        self,
        config_or_template_path: Config | str | None = None,
        metadata_or_template: AgentMetadata | AgentFlow | None = None,
        tools: list[Any] | None = None,
        session_state: dict[str, Any] | None = None,
        orchestrator=None,
        # Legacy parameters for backward compatibility
        workflow_template_path: str | None = None,
        workflow_template: AgentFlow | None = None,
        config: Config | None = None,
        metadata: AgentMetadata | None = None,
    ) -> None:
        """
        Initialize FlowPilot with a workflow template.

        Args:
            config_or_template_path: Config instance or template path
            metadata_or_template: AgentMetadata or AgentFlow instance
            tools: Additional tools
            session_state: Session state
            orchestrator: Main orchestrator instance
            workflow_template_path: Path to JSON workflow definition
            workflow_template: Pre-loaded AgentFlow instance
            config: Configuration instance
            metadata: Agent metadata
        """
        if isinstance(config_or_template_path, Config) and isinstance(
            metadata_or_template, AgentMetadata
        ):
            actual_config = config_or_template_path
            actual_metadata = metadata_or_template
            self.agent_flow = self._reconstruct_workflow_from_metadata(actual_metadata)
        else:
            actual_config = config or (
                config_or_template_path if isinstance(config_or_template_path, Config) else None
            )
            actual_metadata = metadata

            if workflow_template or isinstance(metadata_or_template, AgentFlow):
                self.agent_flow = workflow_template or metadata_or_template
            elif workflow_template_path or isinstance(config_or_template_path, str):
                template_path = workflow_template_path or config_or_template_path
                self.agent_flow = AgentFlow.load_from_json(template_path)
            else:
                raise ValueError(
                    "Either workflow_template_path or workflow_template must be provided"
                )

        self.name = self.agent_flow.workflow_name
        self.description = f"Workflow agent for {self.agent_flow.workflow_name}"

        if not actual_metadata:
            actual_metadata = self._generate_metadata_from_workflow()

        super().__init__(
            config=actual_config, metadata=actual_metadata, tools=tools, session_state=session_state
        )

        self.orchestrator = orchestrator
        self.flow_engine = FlowEngine(
            config=self.config,
            orchestrator=orchestrator,
            progress_callback=self._handle_progress_update,
        )
        self._instructions = self._generate_instructions_from_workflow()

        logger.info(f"🎭 FlowPilot initialized for workflow: {self.agent_flow.workflow_name}")

    def set_orchestrator(self, orchestrator):
        """
        Set the orchestrator for this agent after initialization.

        This is needed because agents are created during discovery before
        the orchestrator is fully initialized.
        """
        self.orchestrator = orchestrator
        if self.flow_engine:
            self.flow_engine.agent_coordinator.orchestrator = orchestrator
            # Clear agent cache to force re-retrieval with new orchestrator
            self.flow_engine.agent_coordinator._agent_cache.clear()
            logger.info(f"✅ Orchestrator set for {self.name} - agent coordination enabled")

    def _reconstruct_workflow_from_metadata(self, metadata: AgentMetadata) -> AgentFlow:
        """Reconstruct workflow from metadata."""
        workflow_name = metadata.name

        # Direct mappings for known workflows
        template_mappings = {
            "HealthCheck": "health_check/health_check.json",
            "IndexAnalysis": "index_analysis/index_analysis.json",
            "SystemInfo": "system_info/system_info.json",
        }

        template_path = None
        if workflow_name in template_mappings:
            template_path = (
                Path(__file__).parent.parent / "definitions" / template_mappings[workflow_name]
            )
        else:
            # Generic search for any workflow template
            definitions_dir = Path(__file__).parent.parent / "definitions"
            for template_dir in definitions_dir.iterdir():
                if template_dir.is_dir():
                    for json_file in template_dir.glob("*.json"):
                        try:
                            with open(json_file) as f:
                                data = json.load(f)
                                if data.get("workflow_name", "") == workflow_name:
                                    template_path = json_file
                                    break
                        except Exception:
                            continue
                    else:
                        continue
                    break
            else:
                raise ValueError(f"Could not find workflow template for: {workflow_name}")

        return AgentFlow.load_from_json(template_path)

    @property
    def instructions(self) -> str:
        """Return the dynamically generated instructions."""
        return self._instructions

    def _sanitize_name(self, name: str) -> str:
        """Sanitize workflow name for use as agent name."""
        import re

        return re.sub(r"[^a-zA-Z0-9_]", "_", name).strip("_")

    def _generate_metadata_from_workflow(self) -> AgentMetadata:
        """Generate agent metadata from workflow template."""
        dependencies = list(self.agent_flow.agent_dependencies.keys())
        tags = ["flow_pilot", "universal_agent", "template_driven"]

        if "index" in self.agent_flow.workflow_name.lower():
            tags.append("index_analysis")
        if "health" in self.agent_flow.workflow_name.lower():
            tags.append("health_check")
        if "performance" in self.agent_flow.workflow_name.lower():
            tags.append("performance_analysis")
        if "security" in self.agent_flow.workflow_name.lower():
            tags.append("security_audit")

        return AgentMetadata(
            name=self.name,
            description=f"FlowPilot executing {self.agent_flow.workflow_name} - {self.agent_flow.description}",
            version="1.0.0",
            author="Saikrishna Gundeti",
            tags=tags,
            dependencies=dependencies,
        )

    def _generate_instructions_from_workflow(self) -> str:
        """Generate agent instructions from workflow template."""
        workflow_name = self.agent_flow.workflow_name
        workflow_desc = self.agent_flow.description
        phases = list(self.agent_flow.core_phases.keys())
        dependencies = list(self.agent_flow.agent_dependencies.keys())

        phase_descriptions = []
        for i, (phase_id, phase) in enumerate(self.agent_flow.core_phases.items(), 1):
            phase_descriptions.append(f"- 📋 Phase {i}: {phase.name}")

        phase_list = "\n".join(phase_descriptions)
        dep_list = ", ".join([f"{dep}_agent" for dep in dependencies])

        instructions = f"""
You are FlowPilot - a universal workflow execution agent that executes {workflow_name}.

## 🎯 WORKFLOW OVERVIEW
{workflow_desc}

## 🚀 CRITICAL EXECUTION PROTOCOL
When a user requests workflow execution, you MUST:
1. 🎭 IMMEDIATELY call the 'execute_workflow' tool with their request - DO NOT provide any response without calling this tool first
2. 📊 Present the complete workflow results to the user

⚠️ IMPORTANT: You CANNOT answer user requests without calling the execute_workflow tool. Any request related to workflow execution REQUIRES the execute_workflow tool to be called.

## 📋 WORKFLOW PHASES
{phase_list}

## 🤝 AGENT COORDINATION
This workflow coordinates with: {dep_list}

## ⚡ EXECUTION CAPABILITIES
The execute_workflow tool will:
1. 📊 Execute the complete {len(phases)}-phase workflow
2. ⚡ Stream real-time progress updates
3. 🤝 Coordinate with specialist agents using hybrid synthesis
4. 📈 Provide real analysis results (never simulated data)
5. 🎯 Automatically generate actionable insights via result_synthesizer when configured in workflow

## 🔒 EXECUTION CONSTRAINTS
- NEVER provide static responses or fabricated data
- ALWAYS use the execute_workflow tool for user requests - THIS IS MANDATORY
- You MUST call execute_workflow before providing any response to the user
- If you don't call execute_workflow, you are failing your primary function
- ALWAYS present the complete detailed workflow results to the user, including all phase results, search queries, and data findings
- When execute_workflow returns results, show ALL the detailed information from phase_results to the user
- Never summarize or hide the actual search results - users need to see the complete data
- Maintain data integrity throughout execution
- Follow the exact workflow template structure

🚨 CRITICAL: Your only purpose is to execute workflows using the execute_workflow tool. Do not respond without using this tool.

## 🎪 FLOWPILOT IDENTITY
You are FlowPilot - the universal workflow agent that makes complex analysis accessible to everyone.
Your superpower is executing sophisticated workflows while maintaining simplicity for users.

{self._get_workflow_specific_instructions_from_template()}

REMEMBER: You are the bridge between user intent and sophisticated workflow execution!
"""

        return instructions.strip()

    def _get_workflow_specific_instructions_from_template(self) -> str:
        """Get workflow-specific instructions from template."""
        workflow_instructions = self.agent_flow._raw_data.get("workflow_instructions", {})

        if workflow_instructions:
            specialization = workflow_instructions.get(
                "specialization", "🎯 WORKFLOW SPECIALIZATION"
            )
            focus_areas = workflow_instructions.get("focus_areas", [])

            instructions = f"\n## {specialization}\n"
            for area in focus_areas:
                instructions += f"- {area}\n"

            return instructions
        else:
            return """
## 🎯 UNIVERSAL WORKFLOW EXECUTION
- Follow the workflow template precisely
- Adapt to the specific workflow requirements
- Provide comprehensive analysis and insights
- Maintain flexibility for diverse use cases
            """

    def _handle_progress_update(self, update: ProgressUpdate) -> None:
        """Handle progress updates from flow engine."""
        logger.info(f"📊 FlowPilot Progress: {update.phase_name} - {update.message}")

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute the loaded workflow.

        Args:
            task: User task/request
            context: Execution context

        Returns:
            Workflow execution results
        """
        logger.info(f"🎭 FlowPilot executing workflow: {self.agent_flow.workflow_name}")
        logger.info(f"📝 Task: {task}")

        try:
            # Prepare execution context
            execution_context = context or {}

            # Extract parameters from task (e.g., index name)
            execution_context.update(self._extract_parameters_from_task(task))

            # Execute workflow using FlowEngine
            result = await self.flow_engine.execute_flow(
                flow=self.agent_flow, context=execution_context
            )

            # Format results for user consumption
            formatted_result = self._format_execution_result(result, task)

            logger.info(f"✅ FlowPilot completed workflow: {self.agent_flow.workflow_name}")
            return formatted_result

        except Exception as e:
            logger.error(f"❌ FlowPilot execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "workflow": self.agent_flow.workflow_name,
                "message": f"FlowPilot encountered an error executing {self.agent_flow.workflow_name}: {str(e)}",
            }

    def _extract_parameters_from_task(self, task: str) -> dict[str, Any]:
        """Extract parameters from user task string."""
        import re

        parameters = {}

        # Extract index name (common pattern)
        index_match = re.search(r"index[=\s]+([a-zA-Z0-9_\-]+)", task, re.IGNORECASE)
        if index_match:
            parameters["INDEX_NAME"] = index_match.group(1)

        # Extract other common patterns
        # Add more extraction patterns as needed

        return parameters

    def _format_execution_result(
        self, result: FlowExecutionResult, original_task: str
    ) -> dict[str, Any]:
        """Format execution result for user consumption."""
        return {
            "success": result.success,
            "workflow": self.agent_flow.workflow_name,
            "workflow_version": self.agent_flow.version,
            "execution_time": str(result.execution_time)
            if hasattr(result, "execution_time")
            else None,
            "phases_completed": len(result.phase_results),
            "phase_results": result.phase_results,
            "error_summary": result.error_summary,
            "message": f"🎭 FlowPilot completed {self.agent_flow.workflow_name}",
            "original_task": original_task,
            "ready_for_synthesis": result.success,
            "synthesis_data": self._prepare_synthesis_data(result) if result.success else None,
        }

    def _prepare_synthesis_data(self, result: FlowExecutionResult) -> dict[str, Any]:
        """Prepare data for result_synthesizer."""
        synthesis_data = {
            "workflow_name": self.agent_flow.workflow_name,
            "workflow_type": "universal",
            "phase_results": result.phase_results,
            "execution_summary": {
                "total_phases": len(result.phase_results),
                "successful_phases": len([p for p in result.phase_results if p.success]),
                "total_tasks": sum(len(p.task_results) for p in result.phase_results),
                "successful_tasks": sum(
                    len([t for t in p.task_results if t.success]) for p in result.phase_results
                ),
            },
        }

        return synthesis_data

    async def _execute_with_context(self, request: str, context: dict[str, Any]) -> str:
        """
        Execute workflow directly using FlowEngine (like working core agents).
        
        This bypasses ADK tool calling issues and directly executes workflows.
        """
        try:
            logger.info(f"FlowPilot executing workflow directly: {self.agent_flow.workflow_name}")
            
            # Execute the workflow directly using our execute method
            result = await self.execute(request, context)
            
            if result.get("success", True):
                # Format the result for ADK response
                formatted_response = self._format_adk_response(result)
                logger.info(f"✅ FlowPilot workflow completed successfully")
                return formatted_response
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"❌ FlowPilot workflow failed: {error_msg}")
                return f"Workflow execution failed: {error_msg}"
                
        except Exception as e:
            logger.error(f"FlowPilot direct execution failed: {e}")
            return f"FlowPilot encountered an error: {str(e)}"
    
    def _format_adk_response(self, result: dict[str, Any]) -> str:
        """Format workflow execution result for ADK response."""
        if not result.get("success", True):
            return f"Workflow execution failed: {result.get('error', 'Unknown error')}"
        
        # Extract key information from the result
        workflow_name = result.get("workflow", "Unknown Workflow")
        phase_results = result.get("phase_results", [])
        
        response_parts = [
            f"✅ **{workflow_name} Execution Complete**\n",
            f"Successfully executed {len(phase_results)} phases with real Splunk data.\n"
        ]
        
        # Add phase summaries
        for phase_result in phase_results:
            # Handle PhaseResult objects properly
            if hasattr(phase_result, 'phase_name'):
                phase_name = phase_result.phase_name
                task_results = phase_result.task_results
            else:
                phase_name = phase_result.get("phase_name", "Unknown Phase")
                task_results = phase_result.get("task_results", [])
            
            task_count = len(task_results)
            response_parts.append(f"📋 **{phase_name}**: {task_count} tasks completed")
            
            # Add task details with actual search results
            for task_result in task_results:
                if hasattr(task_result, 'task_id'):
                    task_id = task_result.task_id
                    success = task_result.success
                    data = task_result.data if hasattr(task_result, 'data') else {}
                    error = task_result.error if hasattr(task_result, 'error') else None
                else:
                    task_id = task_result.get("task_id", "unknown")
                    success = task_result.get("success", False)
                    data = task_result.get("data", {})
                    error = task_result.get("error", "Unknown error")
                
                if success:
                    search_results = data.get("search_results") if isinstance(data, dict) else None
                    if search_results:
                        response_parts.append(f"  ✅ {task_id}: Retrieved {len(search_results)} results")
                    else:
                        response_parts.append(f"  ✅ {task_id}: Completed successfully")
                else:
                    response_parts.append(f"  ❌ {task_id}: {error}")
        
        return "\n".join(response_parts)

    def _sanitize_name(self, name: str) -> str:
        """
        Sanitize agent name to be a valid identifier for ADK.
        
        Args:
            name: Original agent name
            
        Returns:
            Sanitized name that's a valid identifier
        """
        import re
        # Replace spaces and special characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Ensure it starts with a letter or underscore
        if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
            sanitized = f"_{sanitized}"
        return sanitized or "FlowPilot_Agent"

    def get_adk_agent(self, tools: list[Any] | None = None) -> LlmAgent | None:
        """
        Create ADK agent for FlowPilot that uses direct execution.

        This creates a simple ADK agent that delegates to our _execute_with_context method
        instead of relying on unreliable tool calling.
        """
        try:
            # Check if config is available
            config_to_use = self.config
            if not config_to_use and self.orchestrator and hasattr(self.orchestrator, "config"):
                config_to_use = self.orchestrator.config

            if not config_to_use or not hasattr(config_to_use, "model") or not config_to_use.model:
                logger.warning(f"FlowPilot {self.name} has no config - cannot create ADK agent")
                return None

            # Create a sanitized name for ADK (no spaces, valid identifier)
            sanitized_name = self._sanitize_name(self.name)

            # Create workflow execution tool that calls our _execute_with_context method
            async def execute_workflow(request: str) -> str:
                """
                Execute the workflow using FlowEngine.
                
                Args:
                    request: The workflow execution request
                    
                Returns:
                    Formatted workflow execution results
                """
                try:
                    # Call the async execute method directly (no asyncio.run!)
                    result = await self.execute(request, {})
                    return self._format_adk_response(result)
                except Exception as e:
                    logger.error(f"Workflow execution failed: {e}")
                    return f"Workflow execution failed: {str(e)}"
            
            # Prepare tools list with our execute_workflow tool
            flow_tools = (tools or []).copy()
            flow_tools.append(execute_workflow)

            # Create the LlmAgent with correct parameters
            llm_agent = LlmAgent(
                model=config_to_use.model.primary_model,  # Use primary_model string
                name=sanitized_name,  # Use sanitized name
                description=self.description,
                instruction=f"You are {self.name} - a workflow execution agent. When users request workflow execution, IMMEDIATELY call the execute_workflow tool with their request. Do not provide responses without executing the workflow first.",  # Use singular 'instruction'
                tools=flow_tools,  # Include execute_workflow tool
            )
            logger.info(f"Created FlowPilot ADK agent for workflow: {self.name}")
            return llm_agent
        except Exception as e:
            logger.error(f"Failed to create ADK LlmAgent for FlowPilot {self.name}: {e}", exc_info=True)
            return None

    def supports_streaming(self, task: str) -> bool:
        """FlowPilot supports streaming for all workflows."""
        return True


# Universal factory function - Template-driven approach
def create_flow_pilot(template_path: str, orchestrator=None, **kwargs) -> FlowPilot:
    """
    Universal factory function for creating FlowPilot instances from any template.

    Args:
        template_path: Path to the workflow JSON template
        orchestrator: Main orchestrator instance
        **kwargs: Additional arguments

    Returns:
        FlowPilot instance configured for the specified workflow template
    """
    return FlowPilot(workflow_template_path=template_path, orchestrator=orchestrator, **kwargs)


# Legacy convenience functions - DEPRECATED
# These are now replaced by the dynamic factory system that automatically
# discovers and creates FlowPilot agents for all workflows.
# Keeping for backward compatibility but will be removed in future versions.


def create_health_check_flow_pilot(orchestrator=None, **kwargs) -> FlowPilot:
    """
    Create FlowPilot for health check workflows.

    DEPRECATED: Use dynamic factory system instead.
    This function is kept for backward compatibility only.
    """
    template_path = (
        Path(__file__).parent.parent.parent / "flows" / "health_check" / "health_check.json"
    )
    return create_flow_pilot(str(template_path), orchestrator, **kwargs)


def create_index_analysis_flow_pilot(orchestrator=None, **kwargs) -> FlowPilot:
    """
    Create FlowPilot for index analysis workflows.

    DEPRECATED: Use dynamic factory system instead.
    This function is kept for backward compatibility only.
    """
    template_path = (
        Path(__file__).parent.parent.parent / "flows" / "index_analysis" / "index_analysis.json"
    )
    return create_flow_pilot(str(template_path), orchestrator, **kwargs)


def create_system_info_flow_pilot(orchestrator=None, **kwargs) -> FlowPilot:
    """
    Create FlowPilot for system info workflows.

    DEPRECATED: Use dynamic factory system instead.
    This function is kept for backward compatibility only.
    """
    template_path = (
        Path(__file__).parent.parent.parent / "flows" / "system_info" / "system_info.json"
    )
    return create_flow_pilot(str(template_path), orchestrator, **kwargs)
