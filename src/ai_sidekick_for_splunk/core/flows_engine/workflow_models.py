"""
Pydantic models for workflow template validation.

This module provides comprehensive validation models for workflow templates,
ensuring data integrity and providing clear error messages for malformed templates.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class WorkflowType(str, Enum):
    """Supported workflow types."""
    ANALYSIS = "analysis"
    TROUBLESHOOTING = "troubleshooting"
    PERFORMANCE = "performance"
    MONITORING = "monitoring"
    ONBOARDING = "onboarding"
    SECURITY = "security"


class WorkflowCategory(str, Enum):
    """Supported workflow categories."""
    DATA_ANALYSIS = "data_analysis"
    SYSTEM_HEALTH = "system_health"
    SECURITY_AUDIT = "security_audit"
    PERFORMANCE_TUNING = "performance_tuning"
    INFRASTRUCTURE_MONITORING = "infrastructure_monitoring"


class WorkflowSource(str, Enum):
    """Workflow source classification."""
    CORE = "core"
    CONTRIB = "contrib"


class WorkflowStability(str, Enum):
    """Workflow stability levels."""
    STABLE = "stable"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"


class ComplexityLevel(str, Enum):
    """Workflow complexity levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class DataRequirements(BaseModel):
    """Data requirements for workflow execution."""
    minimum_events: int | None = Field(None, ge=0, description="Minimum number of events required")
    required_sourcetypes: list[str] | None = Field(None, description="Required sourcetypes for the workflow")
    optional_fields: list[str] | None = Field(None, description="Optional fields that enhance the workflow")


class AgentDependency(BaseModel):
    """Agent dependency specification."""
    agent_id: str = Field(..., description="Unique identifier for the dependent agent")
    description: str = Field(..., description="Description of the agent's role")
    required: bool = Field(True, description="Whether this agent is required for workflow execution")
    capabilities: list[str] | None = Field(None, description="List of capabilities this agent provides")
    integration_points: list[str] | None = Field(None, description="Points where this agent integrates")
    tools: list[str] | None = Field(None, description="Tools provided by this agent")


class WorkflowInstructions(BaseModel):
    """Workflow-specific instructions for agent behavior."""
    specialization: str = Field(..., description="Specialization description for the workflow")
    focus_areas: list[str] = Field(..., description="Key focus areas for the workflow")
    execution_style: str = Field(..., description="Execution style (e.g., 'fast_parallel', 'sequential')")
    domain: str = Field(..., description="Domain of expertise")


class TaskValidation(BaseModel):
    """Task validation specification."""
    agent: str = Field(..., description="Agent responsible for validation")
    criteria: list[str] | None = Field(None, description="Validation criteria")


class TaskResultInterpretation(BaseModel):
    """Task result interpretation specification."""
    agent: str = Field(..., description="Agent responsible for result interpretation")
    format: str | None = Field(None, description="Expected result format")


class WorkflowTask(BaseModel):
    """Individual workflow task specification."""
    task_id: str = Field(..., description="Unique identifier for the task")
    title: str = Field(..., description="Human-readable task title")
    goal: str = Field(..., description="Goal or objective of the task")
    tool: str = Field(..., description="Tool or method to be used")

    # Optional fields that may be present in templates
    description: str | None = Field(None, description="Task description")
    search_query: str | None = Field(None, description="SPL search query")
    parameters: dict[str, Any] | None = Field(None, description="Task parameters")
    timeout_sec: int | None = Field(None, description="Timeout in seconds")
    analysis_focus: list[str] | None = Field(None, description="Analysis focus areas")
    mandatory: bool | None = Field(None, description="Whether this task is mandatory")
    parallel: bool | None = Field(None, description="Whether this task can run in parallel")
    validation: TaskValidation | None = Field(None, description="Validation specification")
    result_interpretation: TaskResultInterpretation | None = Field(None, description="Result interpretation specification")

    class Config:
        extra = "allow"  # Allow additional fields not explicitly defined


class WorkflowPhase(BaseModel):
    """Workflow phase containing multiple tasks."""
    name: str = Field(..., description="Human-readable phase name")
    description: str = Field(..., description="Description of the phase")
    mandatory: bool = Field(True, description="Whether this phase is mandatory")
    parallel: bool | None = Field(False, description="Whether tasks in this phase can run in parallel")
    max_parallel: int | None = Field(None, ge=1, description="Maximum number of parallel tasks")
    tasks: list[WorkflowTask] = Field(..., min_items=1, description="Tasks in this phase")

    @field_validator('max_parallel')
    @classmethod
    def validate_max_parallel(cls, v, info):
        """Validate max_parallel only makes sense when parallel is True."""
        # Allow max_parallel=1 even when parallel=False (common pattern)
        if v is not None and v > 1 and info.data.get('parallel', False) is False:
            raise ValueError("max_parallel > 1 can only be set when parallel=True")
        return v

    class Config:
        extra = "allow"  # Allow additional fields not explicitly defined


class WorkflowTemplate(BaseModel):
    """Complete workflow template validation model."""

    # Core identification
    workflow_id: str = Field(..., pattern=r'^[a-z_]+\.[a-z_]+$', description="Unique workflow identifier (e.g., 'core.health_check')")
    workflow_name: str = Field(..., min_length=1, description="Human-readable workflow name")
    version: str = Field(..., pattern=r'^\d+\.\d+\.\d+$', description="Semantic version (e.g., '1.0.0')")
    description: str = Field(..., min_length=10, description="Detailed workflow description")

    # Classification metadata
    workflow_type: WorkflowType = Field(..., description="Type of workflow")
    workflow_category: WorkflowCategory = Field(..., description="Category of workflow")
    source: WorkflowSource = Field(..., description="Source classification")
    maintainer: str = Field(..., description="Maintainer name or organization")
    stability: WorkflowStability = Field(..., description="Stability level")

    # Complexity and audience
    complexity_level: ComplexityLevel = Field(..., description="Complexity level")
    estimated_duration: str = Field(..., pattern=r'^\d+-\d+\s+(minutes?|hours?)$', description="Estimated duration (e.g., '2-5 minutes')")
    target_audience: list[str] = Field(..., min_items=1, description="Target audience roles")

    # Technical metadata
    splunk_versions: list[str] = Field(..., min_items=1, description="Supported Splunk versions")
    last_updated: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Last update date (YYYY-MM-DD)")
    documentation_url: str = Field(..., description="URL to documentation")

    # Operational requirements
    prerequisites: list[str] = Field(..., min_items=1, description="Prerequisites for workflow execution")
    required_permissions: list[str] = Field(..., min_items=1, description="Required Splunk permissions")
    data_requirements: DataRequirements = Field(..., description="Data requirements specification")

    # Business value
    business_value: str = Field(..., min_length=10, description="Business value proposition")
    use_cases: list[str] = Field(..., min_items=1, description="Primary use cases")
    success_metrics: list[str] = Field(..., min_items=1, description="Success metrics")

    # Workflow structure
    agent: str | None = Field(None, description="Primary agent for workflow execution")
    workflow_instructions: WorkflowInstructions | None = Field(None, description="Workflow-specific instructions")
    agent_dependencies: dict[str, AgentDependency] = Field(..., min_items=1, description="Agent dependencies")
    core_phases: dict[str, WorkflowPhase] = Field(..., min_items=1, description="Workflow phases")

    # Optional legacy fields that may be present
    execution_flow: dict[str, Any] | None = Field(None, description="Execution flow configuration")
    output_structure: dict[str, Any] | None = Field(None, description="Output structure configuration")

    @field_validator('workflow_id')
    @classmethod
    def validate_workflow_id_format(cls, v):
        """Validate workflow ID follows the expected format."""
        parts = v.split('.')
        if len(parts) != 2:
            raise ValueError("workflow_id must be in format 'source.name' (e.g., 'core.health_check')")

        source, name = parts
        if source not in ['core', 'contrib']:
            raise ValueError("workflow_id source must be 'core' or 'contrib'")

        return v

    @field_validator('documentation_url')
    @classmethod
    def validate_documentation_url(cls, v):
        """Validate documentation URL format."""
        if not (v.startswith('./') or v.startswith('http://') or v.startswith('https://')):
            raise ValueError("documentation_url must be a relative path (./README.md) or absolute URL")
        return v

    @model_validator(mode='after')
    def validate_workflow_consistency(self):
        """Validate consistency across workflow fields."""
        workflow_id = self.workflow_id
        source = self.source

        # Ensure workflow_id source matches source field
        if workflow_id and source:
            id_source = workflow_id.split('.')[0]
            source_value = source.value if hasattr(source, 'value') else source
            if id_source != source_value:
                raise ValueError(f"workflow_id source '{id_source}' must match source field '{source_value}'")

        # Validate agent dependencies reference valid agents
        agent_deps = self.agent_dependencies
        core_phases = self.core_phases

        # Collect all agents referenced in tasks
        referenced_agents = set()
        for phase_name, phase in core_phases.items():
            for task in phase.tasks:
                if task.validation and task.validation.agent:
                    referenced_agents.add(task.validation.agent)
                if task.result_interpretation and task.result_interpretation.agent:
                    referenced_agents.add(task.result_interpretation.agent)

        # Check that all referenced agents are in dependencies
        missing_deps = referenced_agents - set(agent_deps.keys())
        if missing_deps:
            raise ValueError(f"Referenced agents not in dependencies: {missing_deps}")

        return self

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        extra = "allow"  # Allow extra fields for flexibility with existing templates


class WorkflowValidationError(Exception):
    """Custom exception for workflow validation errors."""

    def __init__(self, workflow_path: str, errors: list[dict[str, Any]]):
        self.workflow_path = workflow_path
        self.errors = errors

        # Format error message
        error_details = []
        for error in errors:
            loc = " -> ".join(str(x) for x in error.get('loc', []))
            msg = error.get('msg', 'Unknown error')
            error_details.append(f"  {loc}: {msg}")

        message = f"Validation failed for workflow '{workflow_path}':\n" + "\n".join(error_details)
        super().__init__(message)


def validate_workflow_template(template_data: dict[str, Any], template_path: str = "unknown") -> WorkflowTemplate:
    """
    Validate a workflow template using Pydantic models.

    Args:
        template_data: Raw template data from JSON
        template_path: Path to template file (for error reporting)

    Returns:
        Validated WorkflowTemplate instance

    Raises:
        WorkflowValidationError: If validation fails
    """
    try:
        return WorkflowTemplate(**template_data)
    except Exception as e:
        if hasattr(e, 'errors'):
            raise WorkflowValidationError(template_path, e.errors())
        else:
            raise WorkflowValidationError(template_path, [{"loc": ["root"], "msg": str(e)}])


def validate_workflow_file(template_path: str) -> WorkflowTemplate:
    """
    Validate a workflow template file.

    Args:
        template_path: Path to the workflow template JSON file

    Returns:
        Validated WorkflowTemplate instance

    Raises:
        WorkflowValidationError: If validation fails
        FileNotFoundError: If template file doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    import json
    from pathlib import Path

    template_file = Path(template_path)
    if not template_file.exists():
        raise FileNotFoundError(f"Workflow template not found: {template_path}")

    with open(template_file, encoding='utf-8') as f:
        template_data = json.load(f)

    return validate_workflow_template(template_data, str(template_path))
