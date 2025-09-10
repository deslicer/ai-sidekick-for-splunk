"""
YAML template parser for converting simple templates to FlowPilot JSON workflows.

This module handles loading, validating, and parsing YAML templates into
structured data that can be converted to complex FlowPilot JSON workflows.
"""

import hashlib
import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .template_models import SimpleTemplate

logger = logging.getLogger(__name__)


class TemplateParseError(Exception):
    """Raised when template parsing fails."""

    pass


class TemplateParser:
    """
    Parser for YAML templates that converts them to validated template models.
    """

    def __init__(self):
        """Initialize the template parser."""
        self.supported_formats = ["1.0"]

    def load_template_from_file(self, template_path: Path) -> SimpleTemplate:
        """
        Load and parse a YAML template from file.

        Args:
            template_path: Path to the YAML template file

        Returns:
            Validated SimpleTemplate instance

        Raises:
            TemplateParseError: If parsing or validation fails
        """
        if not template_path.exists():
            raise TemplateParseError(f"Template file not found: {template_path}")

        if template_path.suffix.lower() not in [".yaml", ".yml"]:
            raise TemplateParseError(
                f"Template file must have .yaml or .yml extension: {template_path}"
            )

        try:
            with open(template_path, encoding="utf-8") as f:
                template_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise TemplateParseError(f"Invalid YAML syntax in {template_path}: {e}")
        except Exception as e:
            raise TemplateParseError(f"Failed to read template file {template_path}: {e}")

        return self.parse_template_data(template_data, template_path)

    def load_template_from_string(
        self, template_content: str, source_name: str = "string"
    ) -> SimpleTemplate:
        """
        Load and parse a YAML template from string content.

        Args:
            template_content: YAML template content as string
            source_name: Name for error reporting

        Returns:
            Validated SimpleTemplate instance

        Raises:
            TemplateParseError: If parsing or validation fails
        """
        try:
            template_data = yaml.safe_load(template_content)
        except yaml.YAMLError as e:
            raise TemplateParseError(f"Invalid YAML syntax in {source_name}: {e}")

        return self.parse_template_data(template_data, source_name)

    def parse_template_data(
        self, template_data: dict[str, Any], source_name: str
    ) -> SimpleTemplate:
        """
        Parse and validate template data dictionary.

        Args:
            template_data: Dictionary containing template data
            source_name: Source name for error reporting

        Returns:
            Validated SimpleTemplate instance

        Raises:
            TemplateParseError: If parsing or validation fails
        """
        if not isinstance(template_data, dict):
            raise TemplateParseError(
                f"Template must be a YAML dictionary, got {type(template_data)}"
            )

        # Check template format version
        template_format = template_data.get("template_format", "1.0")
        if template_format not in self.supported_formats:
            raise TemplateParseError(
                f"Unsupported template format '{template_format}' in {source_name}. "
                f"Supported formats: {', '.join(self.supported_formats)}"
            )

        # Transform flat structure to nested structure expected by Pydantic models
        try:
            structured_data = self._transform_template_structure(template_data)
            template = SimpleTemplate(**structured_data)

            logger.info(
                f"✅ Successfully parsed template '{template.metadata.name}' from {source_name}"
            )
            logger.debug(
                f"Template has {template.get_search_count()} searches in {template.get_phase_count()} phases"
            )

            return template

        except ValidationError as e:
            error_details = self._format_validation_errors(e)
            raise TemplateParseError(
                f"Template validation failed in {source_name}:\n{error_details}"
            )
        except Exception as e:
            raise TemplateParseError(f"Failed to parse template {source_name}: {e}")

    def _transform_template_structure(self, template_data: dict[str, Any]) -> dict[str, Any]:
        """
        Transform flat YAML structure to nested structure expected by Pydantic models.

        Args:
            template_data: Raw template data from YAML

        Returns:
            Structured data for Pydantic model creation
        """
        # Extract metadata
        metadata = {
            "name": template_data.get("name"),
            "title": template_data.get("title"),
            "description": template_data.get("description"),
            "category": template_data.get("category"),
            "complexity": template_data.get("complexity", "beginner"),
            "version": template_data.get("version", "1.0.0"),
            "template_format": template_data.get("template_format", "1.0"),
            "author": template_data.get("author", "community"),
            "last_updated": template_data.get("last_updated"),
        }

        # Extract requirements
        requirements = {
            "splunk_versions": template_data.get("splunk_versions", ["8.0+", "9.0+"]),
            "required_permissions": template_data.get("required_permissions", ["search"]),
            "required_indexes": template_data.get("required_indexes"),
            "dependencies": template_data.get("dependencies"),
        }

        # Extract business context
        business_context = {
            "business_value": template_data.get("business_value"),
            "use_cases": template_data.get("use_cases"),
            "success_metrics": template_data.get("success_metrics"),
            "target_audience": template_data.get("target_audience"),
        }

        # Extract advanced options
        advanced_options = {
            "parallel_execution": template_data.get("parallel_execution", True),
            "streaming_support": template_data.get("streaming_support", True),
            "educational_mode": template_data.get("educational_mode", False),
            "estimated_duration": template_data.get("estimated_duration", "5-10 minutes"),
        }

        # Build structured data
        structured_data = {
            "metadata": metadata,
            "requirements": requirements,
            "business_context": business_context,
            "advanced_options": advanced_options,
        }

        # Add searches or phases
        if "searches" in template_data:
            structured_data["searches"] = template_data["searches"]
        elif "phases" in template_data:
            structured_data["phases"] = template_data["phases"]

        return structured_data

    def _format_validation_errors(self, validation_error: ValidationError) -> str:
        """
        Format Pydantic validation errors into readable format.

        Args:
            validation_error: Pydantic ValidationError

        Returns:
            Formatted error message
        """
        error_lines = []
        for error in validation_error.errors():
            location = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_lines.append(f"  • {location}: {message}")

        return "\n".join(error_lines)

    def calculate_template_hash(self, template_path: Path) -> str:
        """
        Calculate hash of template file for change detection.

        Args:
            template_path: Path to template file

        Returns:
            SHA256 hash of file content
        """
        try:
            with open(template_path, "rb") as f:
                content = f.read()
            return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to calculate hash for {template_path}: {e}")
            return ""

    def validate_template_syntax(self, template_path: Path) -> tuple[bool, str | None]:
        """
        Validate template syntax without full parsing.

        Args:
            template_path: Path to template file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            self.load_template_from_file(template_path)
            return True, None
        except TemplateParseError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {e}"


# Convenience functions
def load_template(template_path: Path) -> SimpleTemplate:
    """
    Load a template from file path.

    Args:
        template_path: Path to YAML template file

    Returns:
        Validated SimpleTemplate instance
    """
    parser = TemplateParser()
    return parser.load_template_from_file(template_path)


def validate_template(template_path: Path) -> tuple[bool, str | None]:
    """
    Validate a template file.

    Args:
        template_path: Path to YAML template file

    Returns:
        Tuple of (is_valid, error_message)
    """
    parser = TemplateParser()
    return parser.validate_template_syntax(template_path)


def parse_template_string(template_content: str) -> SimpleTemplate:
    """
    Parse template from string content.

    Args:
        template_content: YAML template content

    Returns:
        Validated SimpleTemplate instance
    """
    parser = TemplateParser()
    return parser.load_template_from_string(template_content)
