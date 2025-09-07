"""
Template system for creating FlowPilot workflows from simple YAML templates.

This module provides a simple way for contributors to create FlowPilot workflow agents
by writing YAML templates that focus on business logic and SPL searches, rather than
complex JSON structures.

Key Components:
- template_models: Pydantic models for template validation
- template_parser: YAML parsing and validation
- template_generator: Conversion from templates to FlowPilot JSON
"""

from .template_generator import (
    TemplateGenerator,
    generate_workflow_from_template,
)
from .template_models import (
    ComplexityLevel,
    PhaseDefinition,
    SearchDefinition,
    SimpleTemplate,
    TemplateAdvancedOptions,
    TemplateBusinessContext,
    TemplateCategory,
    TemplateMetadata,
    TemplateRequirements,
)
from .template_parser import (
    TemplateParseError,
    TemplateParser,
    load_template,
    parse_template_string,
    validate_template,
)

__all__ = [
    # Models
    "SimpleTemplate",
    "TemplateMetadata",
    "TemplateRequirements",
    "TemplateBusinessContext",
    "TemplateAdvancedOptions",
    "SearchDefinition",
    "PhaseDefinition",
    "TemplateCategory",
    "ComplexityLevel",
    # Parser
    "TemplateParser",
    "TemplateParseError",
    "load_template",
    "validate_template",
    "parse_template_string",
    # Generator
    "TemplateGenerator",
    "generate_workflow_from_template",
]
