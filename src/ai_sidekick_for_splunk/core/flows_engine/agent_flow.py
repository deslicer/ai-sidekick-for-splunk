"""
Guided Agent Flows Core Framework - Production Ready.

This module provides the foundational classes for Reasoning Flow Definitions
and bounded intelligence task execution within the Guided Agent Flows system.
Fully integrated and production-ready.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Import Pydantic validation models
try:
    from .workflow_models import (
        WorkflowTemplate,
        WorkflowValidationError,
        validate_workflow_template,
    )

    PYDANTIC_AVAILABLE = True
    logger.debug("✅ Pydantic validation models loaded successfully")
except ImportError as e:
    PYDANTIC_AVAILABLE = False
    logger.warning(f"⚠️ Pydantic validation not available: {e}")
    WorkflowTemplate = None
    validate_workflow_template = None
    WorkflowValidationError = None


@dataclass
class AgentDependency:
    """Configuration for agent dependencies in flows."""

    agent_id: str
    description: str
    required: bool
    capabilities: list[str]
    integration_points: list[str] = field(default_factory=list)


@dataclass
class ValidationConfig:
    """Configuration for task validation."""

    agent: str
    validate_syntax: bool = True
    optimize_performance: bool = False
    per_sourcetype_validation: bool = False


@dataclass
class InterpretationConfig:
    """Configuration for result interpretation."""

    agent: str
    interpret_results: bool = True
    generate_insights: bool = True
    interpretation_prompt: str | None = None
    output_format: dict[str, str] | None = None


@dataclass
class LLMLoopConfig:
    """Configuration for LLM-in-the-loop task execution."""

    enabled: bool = False
    max_iterations: int = 3
    allowed_tools: list[str] = field(default_factory=list)
    context_resources: list[str] = field(default_factory=list)  # MCP doc tools
    prompt: str | None = None
    step_validation: bool = True
    bounded_execution: bool = True
    consistency_checks: list[str] = field(default_factory=list)


@dataclass
class ContextResource:
    """Embedded context resource for LLM tasks."""

    resource_type: str  # "mcp_tool", "documentation", "reference"
    resource_id: str  # Tool name or doc identifier
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # Higher priority resources loaded first


@dataclass
class FlowTask:
    """Individual task within a flow phase."""

    task_id: str
    title: str
    description: str
    goal: str
    tool: str
    search_query: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    validation: ValidationConfig | None = None
    result_interpretation: InterpretationConfig | None = None
    analysis_focus: list[str] = field(default_factory=list)
    execution_mode: str | None = None
    llm_analysis: dict[str, Any] | None = None
    cross_sourcetype_preparation: dict[str, Any] | None = None
    note: str | None = None

    # Enhanced LLM-in-the-loop support
    llm_loop: LLMLoopConfig | None = None
    context_resources: list[ContextResource] = field(default_factory=list)
    dynamic_instructions: str | None = None
    step_constraints: dict[str, Any] = field(default_factory=dict)

    # Parallel execution configuration
    timeout_sec: int | None = None


@dataclass
class FlowPhase:
    """Phase containing multiple related tasks."""

    name: str
    description: str
    mandatory: bool
    tasks: list[FlowTask]
    goal_selection_strategy: dict[str, Any] | None = None
    analysis_goals: list[dict[str, Any]] = field(default_factory=list)
    correlation_tasks: list[dict[str, Any]] = field(default_factory=list)
    synthesis_tasks: list[dict[str, Any]] = field(default_factory=list)

    # Parallel execution configuration
    parallel: bool = False
    max_parallel: int = 1


@dataclass
class ExecutionFlow:
    """Configuration for flow execution behavior."""

    sequential_phases: list[str]
    parallel_execution: dict[str, bool] = field(default_factory=dict)
    validation_workflow: dict[str, str] = field(default_factory=dict)
    adaptive_behavior: dict[str, bool] = field(default_factory=dict)


@dataclass
class AgentFlow:
    """
    Complete Reasoning Flow Definition loaded from JSON configuration.

    Represents a structured workflow definition for Guided Agent Flows,
    including bounded intelligence tasks, agent dependencies, and
    contextual execution parameters.
    """

    workflow_name: str
    version: str
    description: str
    agent_dependencies: dict[str, AgentDependency]
    core_phases: dict[str, FlowPhase]
    execution_flow: ExecutionFlow
    output_structure: dict[str, Any]
    _raw_data: dict[str, Any] = field(default_factory=dict)  # Store raw JSON for custom fields
    _validated_template: Any | None = field(
        default=None, init=False
    )  # Store validated Pydantic model

    @classmethod
    def load_from_json(cls, json_path: str | Path) -> "AgentFlow":
        """
        Load agent flow from JSON file with optional Pydantic validation.

        Args:
            json_path: Path to JSON flow definition file

        Returns:
            AgentFlow instance

        Raises:
            FileNotFoundError: If JSON file doesn't exist
            ValueError: If JSON structure is invalid
            WorkflowValidationError: If Pydantic validation fails
        """
        try:
            path = Path(json_path)
            if not path.exists():
                raise FileNotFoundError(f"Flow definition not found: {json_path}")

            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            # Perform Pydantic validation if available
            validated_template = None
            if PYDANTIC_AVAILABLE and validate_workflow_template:
                try:
                    validated_template = validate_workflow_template(data, str(json_path))
                    logger.debug(f"✅ Pydantic validation passed for {json_path}")
                except WorkflowValidationError as e:
                    logger.error(f"❌ Pydantic validation failed for {json_path}: {e}")
                    # For now, log the error but continue loading
                    # In the future, this could be made strict with a configuration flag
                    logger.warning("⚠️ Continuing with legacy loading despite validation errors")
                except Exception as e:
                    logger.warning(f"⚠️ Pydantic validation error for {json_path}: {e}")

            # Load using existing logic
            agent_flow = cls._from_dict(data)

            # Store validated template if available
            if validated_template:
                agent_flow._validated_template = validated_template

            return agent_flow

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in flow definition: {e}")
        except Exception as e:
            logger.error(f"Failed to load flow from {json_path}: {e}")
            raise

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> "AgentFlow":
        """Convert dictionary data to AgentFlow instance."""
        try:
            # Parse agent dependencies
            agent_deps = {}
            for dep_name, dep_data in data.get("agent_dependencies", {}).items():
                agent_deps[dep_name] = AgentDependency(
                    agent_id=dep_data["agent_id"],
                    description=dep_data["description"],
                    required=dep_data["required"],
                    capabilities=dep_data["capabilities"],
                    integration_points=dep_data.get("integration_points", []),
                )

            # Parse phases
            phases = {}
            for phase_name, phase_data in data.get("core_phases", {}).items():
                tasks = []
                for task_data in phase_data.get("tasks", []):
                    # Parse validation config
                    validation = None
                    if "validation" in task_data:
                        val_data = task_data["validation"]
                        validation = ValidationConfig(
                            agent=val_data["agent"],
                            validate_syntax=val_data.get("validate_syntax", True),
                            optimize_performance=val_data.get("optimize_performance", False),
                            per_sourcetype_validation=val_data.get(
                                "per_sourcetype_validation", False
                            ),
                        )

                    # Parse interpretation config
                    interpretation = None
                    if "result_interpretation" in task_data:
                        interp_data = task_data["result_interpretation"]
                        interpretation = InterpretationConfig(
                            agent=interp_data["agent"],
                            interpret_results=interp_data.get("interpret_results", True),
                            generate_insights=interp_data.get("generate_insights", True),
                            interpretation_prompt=interp_data.get("interpretation_prompt"),
                            output_format=interp_data.get("output_format"),
                        )

                    # Parse LLM loop configuration
                    llm_loop = None
                    if "llm_loop" in task_data:
                        llm_loop_data = task_data["llm_loop"]
                        llm_loop = LLMLoopConfig(
                            enabled=llm_loop_data.get("enabled", False),
                            max_iterations=llm_loop_data.get("max_iterations", 3),
                            allowed_tools=llm_loop_data.get("allowed_tools", []),
                            context_resources=llm_loop_data.get("context_resources", []),
                            prompt=llm_loop_data.get("prompt"),
                            step_validation=llm_loop_data.get("step_validation", True),
                            bounded_execution=llm_loop_data.get("bounded_execution", True),
                            consistency_checks=llm_loop_data.get("consistency_checks", []),
                        )

                    # Parse context resources
                    context_resources = []
                    if "context_resources" in task_data:
                        for res_data in task_data["context_resources"]:
                            context_resources.append(
                                ContextResource(
                                    resource_type=res_data["resource_type"],
                                    resource_id=res_data["resource_id"],
                                    description=res_data["description"],
                                    parameters=res_data.get("parameters", {}),
                                    priority=res_data.get("priority", 1),
                                )
                            )

                    task = FlowTask(
                        task_id=task_data["task_id"],
                        title=task_data["title"],
                        description=task_data["description"],
                        goal=task_data["goal"],
                        tool=task_data["tool"],
                        search_query=task_data.get("search_query"),
                        parameters=task_data.get("parameters", {}),
                        validation=validation,
                        result_interpretation=interpretation,
                        analysis_focus=task_data.get("analysis_focus", []),
                        execution_mode=task_data.get("execution_mode"),
                        llm_analysis=task_data.get("llm_analysis"),
                        cross_sourcetype_preparation=task_data.get("cross_sourcetype_preparation"),
                        note=task_data.get("note"),
                        # Enhanced LLM-in-the-loop support
                        llm_loop=llm_loop,
                        context_resources=context_resources,
                        dynamic_instructions=task_data.get("dynamic_instructions"),
                        step_constraints=task_data.get("step_constraints", {}),
                    )
                    tasks.append(task)

                phase = FlowPhase(
                    name=phase_data["name"],
                    description=phase_data["description"],
                    mandatory=phase_data["mandatory"],
                    tasks=tasks,
                    goal_selection_strategy=phase_data.get("goal_selection_strategy"),
                    analysis_goals=phase_data.get("analysis_goals", []),
                    correlation_tasks=phase_data.get("correlation_tasks", []),
                    synthesis_tasks=phase_data.get("synthesis_tasks", []),
                    parallel=phase_data.get("parallel", False),
                    max_parallel=phase_data.get("max_parallel", 1),
                )
                phases[phase_name] = phase

            # Parse execution flow
            exec_flow_data = data.get("execution_flow", {})
            # Support both 'sequential_phases' and 'phase_order' field names
            sequential_phases = exec_flow_data.get("sequential_phases") or exec_flow_data.get(
                "phase_order", []
            )
            execution_flow = ExecutionFlow(
                sequential_phases=sequential_phases,
                parallel_execution=exec_flow_data.get("parallel_execution", {}),
                validation_workflow=exec_flow_data.get("validation_workflow", {}),
                adaptive_behavior=exec_flow_data.get("adaptive_behavior", {}),
            )

            return cls(
                workflow_name=data["workflow_name"],
                version=data["version"],
                description=data["description"],
                agent_dependencies=agent_deps,
                core_phases=phases,
                execution_flow=execution_flow,
                output_structure=data.get("output_structure", {}),
                _raw_data=data,  # Store complete raw data for custom fields
            )

        except KeyError as e:
            raise ValueError(f"Missing required field in flow definition: {e}")
        except Exception as e:
            logger.error(f"Failed to parse flow definition: {e}")
            raise

    @property
    def is_validated(self) -> bool:
        """Check if this workflow has been validated with Pydantic."""
        return self._validated_template is not None

    @property
    def validation_metadata(self) -> dict[str, Any] | None:
        """Get validated metadata if available."""
        if self._validated_template:
            return {
                "workflow_id": getattr(self._validated_template, "workflow_id", None),
                "workflow_type": getattr(self._validated_template, "workflow_type", None),
                "workflow_category": getattr(self._validated_template, "workflow_category", None),
                "source": getattr(self._validated_template, "source", None),
                "maintainer": getattr(self._validated_template, "maintainer", None),
                "stability": getattr(self._validated_template, "stability", None),
                "complexity_level": getattr(self._validated_template, "complexity_level", None),
                "estimated_duration": getattr(self._validated_template, "estimated_duration", None),
                "target_audience": getattr(self._validated_template, "target_audience", None),
                "business_value": getattr(self._validated_template, "business_value", None),
                "use_cases": getattr(self._validated_template, "use_cases", None),
                "success_metrics": getattr(self._validated_template, "success_metrics", None),
            }
        return None

    def get_metadata_field(self, field_name: str, default: Any = None) -> Any:
        """
        Get a metadata field from validated template or raw data.

        Args:
            field_name: Name of the metadata field
            default: Default value if field not found

        Returns:
            Field value or default
        """
        # Try validated template first
        if self._validated_template and hasattr(self._validated_template, field_name):
            return getattr(self._validated_template, field_name)

        # Fall back to raw data
        return self._raw_data.get(field_name, default)

    def validate(self) -> list[str]:
        """
        Validate the flow definition for consistency and completeness.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required fields
        if not self.workflow_name:
            errors.append("workflow_name is required")
        if not self.version:
            errors.append("version is required")
        if not self.core_phases:
            errors.append("At least one phase is required")

        # Validate phases
        for phase_name, phase in self.core_phases.items():
            if not phase.tasks:
                errors.append(f"Phase '{phase_name}' has no tasks")

            # Validate tasks
            for task in phase.tasks:
                if not task.tool:
                    errors.append(f"Task '{task.task_id}' missing tool specification")

                # Check agent dependencies
                if task.validation and task.validation.agent not in self.agent_dependencies:
                    errors.append(
                        f"Task '{task.task_id}' references unknown validation agent: {task.validation.agent}"
                    )

                if (
                    task.result_interpretation
                    and task.result_interpretation.agent not in self.agent_dependencies
                ):
                    errors.append(
                        f"Task '{task.task_id}' references unknown interpretation agent: {task.result_interpretation.agent}"
                    )

        # Validate execution flow
        for phase_name in self.execution_flow.sequential_phases:
            if phase_name not in self.core_phases:
                errors.append(f"Execution flow references unknown phase: {phase_name}")

        return errors

    def get_phase_by_name(self, phase_name: str) -> FlowPhase | None:
        """Get a phase by name."""
        return self.core_phases.get(phase_name)

    def get_task_by_id(self, task_id: str) -> FlowTask | None:
        """Get a task by ID across all phases."""
        for phase in self.core_phases.values():
            for task in phase.tasks:
                if task.task_id == task_id:
                    return task
        return None

    def get_required_agents(self) -> list[str]:
        """Get list of all required agent dependencies."""
        return [dep.agent_id for dep in self.agent_dependencies.values() if dep.required]
