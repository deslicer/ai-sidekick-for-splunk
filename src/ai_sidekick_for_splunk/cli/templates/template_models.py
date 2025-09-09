"""
Pydantic models for YAML template validation and parsing.

This module defines the structure for simple YAML templates that get converted
to complex FlowPilot JSON workflows.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class TemplateCategory(str, Enum):
    """Template categories for organizing workflows."""

    SECURITY = "security"
    PERFORMANCE = "performance"
    TROUBLESHOOTING = "troubleshooting"
    ANALYSIS = "analysis"
    MONITORING = "monitoring"
    DATA_QUALITY = "data_quality"


class ComplexityLevel(str, Enum):
    """Complexity levels for templates."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class SearchDefinition(BaseModel):
    """Definition of a single SPL search within a template."""

    name: str = Field(..., description="Unique name for the search")
    spl: str = Field(..., description="SPL search query")
    description: str = Field(..., description="What this search does")
    earliest: str | None = Field(default="-24h@h", description="Earliest time for the search")
    latest: str | None = Field(default="now", description="Latest time for the search")
    expected_results: str | None = Field(default=None, description="What results to expect")
    timeout: int | None = Field(default=300, description="Search timeout in seconds")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate search name is a valid identifier."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Search name must be alphanumeric with underscores or hyphens")
        return v

    @field_validator("spl")
    @classmethod
    def validate_spl(cls, v: str) -> str:
        """Basic SPL validation."""
        v = v.strip()
        if not v:
            raise ValueError("SPL query cannot be empty")

        # Basic syntax checks
        if v.count('"') % 2 != 0:
            raise ValueError("Unmatched quotes in SPL query")
        if v.count("'") % 2 != 0:
            raise ValueError("Unmatched single quotes in SPL query")

        return v


class PhaseDefinition(BaseModel):
    """Definition of a workflow phase containing multiple searches."""

    name: str = Field(..., description="Unique name for the phase")
    title: str = Field(..., description="Human-readable title for the phase")
    description: str = Field(..., description="What this phase accomplishes")
    searches: list[SearchDefinition] = Field(..., description="Searches in this phase")
    parallel: bool | None = Field(default=False, description="Can searches run in parallel")
    depends_on: list[str] | None = Field(default=None, description="Phase dependencies")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate phase name is a valid identifier."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Phase name must be alphanumeric with underscores or hyphens")
        return v

    @field_validator("searches")
    @classmethod
    def validate_searches(cls, v: list[SearchDefinition]) -> list[SearchDefinition]:
        """Validate searches list is not empty and names are unique."""
        if not v:
            raise ValueError("Phase must contain at least one search")

        names = [search.name for search in v]
        if len(names) != len(set(names)):
            raise ValueError("Search names within a phase must be unique")

        return v


class TemplateMetadata(BaseModel):
    """Metadata for the template."""

    name: str = Field(..., description="Template name (used for file naming)")
    title: str = Field(..., description="Human-readable title")
    description: str = Field(..., description="What this template does")
    category: TemplateCategory = Field(..., description="Template category")
    complexity: ComplexityLevel = Field(
        default=ComplexityLevel.BEGINNER, description="Complexity level"
    )
    version: str = Field(default="1.0.0", description="Template version")
    template_format: str = Field(default="1.0", description="Template format version")
    author: str = Field(default="community", description="Template author")

    # Auto-generated fields
    last_updated: str | None = Field(default=None, description="Last update timestamp")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate template name is a valid identifier."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Template name must be alphanumeric with underscores or hyphens")
        return v

    @model_validator(mode="after")
    def set_last_updated(self) -> "TemplateMetadata":
        """Set last_updated if not provided."""
        if self.last_updated is None:
            self.last_updated = datetime.now().strftime("%Y-%m-%d")
        return self


class TemplateRequirements(BaseModel):
    """Requirements and constraints for the template."""

    splunk_versions: list[str] = Field(
        default=["8.0+", "9.0+"], description="Supported Splunk versions"
    )
    required_permissions: list[str] = Field(
        default=["search"], description="Required Splunk permissions"
    )
    required_indexes: list[str] | None = Field(default=None, description="Required indexes")
    dependencies: list[str] | None = Field(default=None, description="Agent dependencies")

    @field_validator("required_permissions")
    @classmethod
    def validate_permissions(cls, v: list[str]) -> list[str]:
        """Validate permissions list."""
        if not v:
            raise ValueError("At least one permission is required")
        return v


class TemplateBusinessContext(BaseModel):
    """Business context and value proposition."""

    business_value: str = Field(..., description="Business value this template provides")
    use_cases: list[str] = Field(..., description="Use cases for this template")
    success_metrics: list[str] | None = Field(default=None, description="How to measure success")
    target_audience: list[str] | None = Field(default=None, description="Who should use this")

    @field_validator("use_cases")
    @classmethod
    def validate_use_cases(cls, v: list[str]) -> list[str]:
        """Validate use cases list."""
        if not v:
            raise ValueError("At least one use case is required")
        return v


class TemplateAdvancedOptions(BaseModel):
    """Advanced options for template behavior."""

    parallel_execution: bool = Field(default=True, description="Can phases run in parallel")
    streaming_support: bool = Field(default=True, description="Support streaming responses")
    educational_mode: bool = Field(default=False, description="Include educational explanations")
    estimated_duration: str = Field(default="5-10 minutes", description="Estimated execution time")


class SimpleTemplate(BaseModel):
    """
    Main template model that represents a simple YAML template.

    This gets converted to a complex FlowPilot JSON workflow.
    """

    # Core template definition
    metadata: TemplateMetadata = Field(..., description="Template metadata")
    requirements: TemplateRequirements = Field(
        default_factory=TemplateRequirements, description="Requirements"
    )
    business_context: TemplateBusinessContext = Field(..., description="Business context")

    # Workflow definition - either simple searches or complex phases
    searches: list[SearchDefinition] | None = Field(
        default=None, description="Simple search list"
    )
    phases: list[PhaseDefinition] | None = Field(
        default=None, description="Complex phase definition"
    )

    # Advanced options
    advanced_options: TemplateAdvancedOptions = Field(
        default_factory=TemplateAdvancedOptions, description="Advanced options"
    )

    @model_validator(mode="after")
    def validate_searches_or_phases(self) -> "SimpleTemplate":
        """Ensure either searches or phases are provided, but not both."""
        if not self.searches and not self.phases:
            raise ValueError("Template must define either 'searches' or 'phases'")

        if self.searches and self.phases:
            raise ValueError(
                "Template cannot define both 'searches' and 'phases' - choose one approach"
            )

        return self

    @model_validator(mode="after")
    def validate_phase_dependencies(self) -> "SimpleTemplate":
        """Validate phase dependencies reference existing phases."""
        if not self.phases:
            return self

        phase_names = {phase.name for phase in self.phases}

        for phase in self.phases:
            if phase.depends_on:
                for dep in phase.depends_on:
                    if dep not in phase_names:
                        raise ValueError(
                            f"Phase '{phase.name}' depends on non-existent phase '{dep}'"
                        )

        return self

    def is_simple_template(self) -> bool:
        """Check if this is a simple template (searches) or complex (phases)."""
        return self.searches is not None

    def get_all_searches(self) -> list[SearchDefinition]:
        """Get all searches from either simple searches or phases."""
        if self.searches:
            return self.searches

        if self.phases:
            all_searches = []
            for phase in self.phases:
                all_searches.extend(phase.searches)
            return all_searches

        return []

    def get_search_count(self) -> int:
        """Get total number of searches in the template."""
        return len(self.get_all_searches())

    def get_phase_count(self) -> int:
        """Get number of phases (1 for simple templates)."""
        if self.searches:
            return 1  # Simple templates have one implicit phase
        return len(self.phases) if self.phases else 0
