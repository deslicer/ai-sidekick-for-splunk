"""
Workflow Discovery & Grouping System

This module provides automatic discovery, validation, and grouping of workflow templates
across core and contrib directories. It enables dynamic workflow registration and
intelligent categorization based on metadata.

Key Features:
- Automatic workflow discovery from multiple directories
- Pydantic-based template validation
- Metadata-driven grouping and filtering
- Dynamic FlowPilot agent registration
- Support for core and contrib workflow separation
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .agent_flow import AgentFlow
from .workflow_models import WorkflowValidationError, validate_workflow_template

logger = logging.getLogger(__name__)


class WorkflowSource(Enum):
    """Workflow source types"""
    CORE = "core"
    CONTRIB = "contrib"
    UNKNOWN = "unknown"


class WorkflowStability(Enum):
    """Workflow stability levels"""
    STABLE = "stable"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"


class ComplexityLevel(Enum):
    """Workflow complexity levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class WorkflowInfo:
    """Comprehensive workflow information"""
    # Core identification
    workflow_id: str
    file_path: Path
    agent_flow: AgentFlow

    # Metadata
    workflow_name: str
    workflow_type: str
    workflow_category: str
    source: WorkflowSource
    stability: WorkflowStability
    complexity_level: ComplexityLevel

    # Operational details
    version: str
    estimated_duration: str
    maintainer: str
    last_updated: str

    # Requirements
    target_audience: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    required_permissions: list[str] = field(default_factory=list)
    splunk_versions: list[str] = field(default_factory=list)

    # Business context
    business_value: str = ""
    use_cases: list[str] = field(default_factory=list)
    success_metrics: list[str] = field(default_factory=list)
    industry_focus: list[str] = field(default_factory=list)

    # Technical details
    data_requirements: dict[str, Any] = field(default_factory=dict)
    documentation_url: str = ""

    # Discovery metadata
    discovery_timestamp: str = ""
    validation_status: str = "unknown"
    validation_errors: list[str] = field(default_factory=list)


@dataclass
class WorkflowGroup:
    """Group of related workflows"""
    group_id: str
    group_name: str
    description: str
    workflows: list[WorkflowInfo] = field(default_factory=list)

    # Group metadata
    total_count: int = 0
    stability_distribution: dict[str, int] = field(default_factory=dict)
    complexity_distribution: dict[str, int] = field(default_factory=dict)
    source_distribution: dict[str, int] = field(default_factory=dict)


class WorkflowDiscovery:
    """
    Automatic workflow discovery and grouping system

    Scans specified directories for workflow JSON files, validates them,
    and organizes them into logical groups based on metadata.
    """

    def __init__(self, base_paths: list[Path] | None = None):
        """
        Initialize workflow discovery

        Args:
            base_paths: List of base paths to scan. Defaults to standard locations.
        """
        self.base_paths = base_paths or self._get_default_paths()
        self.discovered_workflows: dict[str, WorkflowInfo] = {}
        self.workflow_groups: dict[str, WorkflowGroup] = {}
        self.discovery_stats = {
            "total_scanned": 0,
            "valid_workflows": 0,
            "invalid_workflows": 0,
            "discovery_errors": []
        }

        logger.info(f"🔍 WorkflowDiscovery initialized with paths: {self.base_paths}")

    def _get_default_paths(self) -> list[Path]:
        """Get default workflow discovery paths"""
        current_file = Path(__file__)
        # From workflow_discovery.py -> flows_engine -> core -> ai_sidekick_for_splunk -> src
        ai_sidekick_for_splunk_root = current_file.parent.parent.parent  # Go up to ai_sidekick_for_splunk/

        return [
            ai_sidekick_for_splunk_root / "core" / "flows",
            ai_sidekick_for_splunk_root / "contrib" / "flows"
        ]

    def discover_workflows(self, force_refresh: bool = False) -> dict[str, WorkflowInfo]:
        """
        Discover all workflows in configured paths

        Args:
            force_refresh: If True, clear existing discoveries and rescan

        Returns:
            Dictionary of workflow_id -> WorkflowInfo
        """
        if force_refresh:
            self.discovered_workflows.clear()
            self.workflow_groups.clear()
            self.discovery_stats = {
                "total_scanned": 0,
                "valid_workflows": 0,
                "invalid_workflows": 0,
                "discovery_errors": []
            }

        logger.info("🔍 Starting workflow discovery...")

        for base_path in self.base_paths:
            if not base_path.exists():
                logger.warning(f"⚠️ Workflow path does not exist: {base_path}")
                continue

            logger.info(f"📂 Scanning: {base_path}")
            self._scan_directory(base_path)

        # Group workflows after discovery
        self._group_workflows()

        logger.info(f"✅ Discovery complete: {self.discovery_stats['valid_workflows']} valid workflows found")
        return self.discovered_workflows

    def _scan_directory(self, directory: Path) -> None:
        """Recursively scan directory for workflow JSON files"""
        try:
            for json_file in directory.rglob("*.json"):
                # Skip template examples and non-workflow files
                if self._should_skip_file(json_file):
                    continue

                self.discovery_stats["total_scanned"] += 1
                workflow_info = self._process_workflow_file(json_file)

                if workflow_info:
                    self.discovered_workflows[workflow_info.workflow_id] = workflow_info
                    self.discovery_stats["valid_workflows"] += 1
                    logger.debug(f"✅ Discovered: {workflow_info.workflow_name}")
                else:
                    self.discovery_stats["invalid_workflows"] += 1

        except Exception as e:
            error_msg = f"Error scanning directory {directory}: {e}"
            logger.error(error_msg)
            self.discovery_stats["discovery_errors"].append(error_msg)

    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if a JSON file should be skipped during discovery"""
        skip_patterns = [
            "template",
            "example",
            "_template",
            "_example",
            "basic_workflow_template",
            "security_audit_example"
        ]

        file_name = file_path.stem.lower()
        return any(pattern in file_name for pattern in skip_patterns)

    def _process_workflow_file(self, file_path: Path) -> WorkflowInfo | None:
        """Process a single workflow JSON file"""
        try:
            # Load and validate JSON
            with open(file_path) as f:
                workflow_data = json.load(f)

            # Validate using Pydantic model
            try:
                validate_workflow_template(workflow_data, str(file_path))
                logger.debug(f"✅ Validated workflow template: {file_path}")
            except WorkflowValidationError as e:
                logger.warning(f"⚠️ Invalid workflow template: {file_path}")
                logger.warning(f"   Validation errors: {e.errors}")
                return None
            except Exception as e:
                logger.warning(f"⚠️ Validation failed for: {file_path}")
                logger.warning(f"   Error: {e}")
                return None

            # Create AgentFlow instance
            agent_flow = AgentFlow.load_from_json(str(file_path))

            # Extract metadata and create WorkflowInfo
            workflow_info = self._create_workflow_info(file_path, workflow_data, agent_flow)
            workflow_info.validation_status = "valid"

            return workflow_info

        except Exception as e:
            error_msg = f"Error processing workflow file {file_path}: {e}"
            logger.error(error_msg)
            self.discovery_stats["discovery_errors"].append(error_msg)
            return None

    def _create_workflow_info(self, file_path: Path, workflow_data: dict, agent_flow: AgentFlow) -> WorkflowInfo:
        """Create WorkflowInfo from workflow data"""
        from datetime import datetime

        # Determine source from file path
        source = WorkflowSource.CORE if "core/flows" in str(file_path) else WorkflowSource.CONTRIB
        if "contrib/flows" in str(file_path):
            source = WorkflowSource.CONTRIB

        # Parse enums safely
        stability = WorkflowStability.STABLE
        try:
            stability = WorkflowStability(workflow_data.get("stability", "stable"))
        except ValueError:
            pass

        complexity = ComplexityLevel.BEGINNER
        try:
            complexity = ComplexityLevel(workflow_data.get("complexity_level", "beginner"))
        except ValueError:
            pass

        return WorkflowInfo(
            # Core identification
            workflow_id=workflow_data.get("workflow_id", f"unknown_{file_path.stem}"),
            file_path=file_path,
            agent_flow=agent_flow,

            # Metadata
            workflow_name=workflow_data.get("workflow_name", workflow_data.get("name", "Unknown Workflow")),
            workflow_type=workflow_data.get("workflow_type", "unknown"),
            workflow_category=workflow_data.get("workflow_category", "general"),
            source=source,
            stability=stability,
            complexity_level=complexity,

            # Operational details
            version=workflow_data.get("version", "1.0.0"),
            estimated_duration=workflow_data.get("estimated_duration", "Unknown"),
            maintainer=workflow_data.get("maintainer", "Unknown"),
            last_updated=workflow_data.get("last_updated", "Unknown"),

            # Requirements
            target_audience=workflow_data.get("target_audience", []),
            prerequisites=workflow_data.get("prerequisites", []),
            required_permissions=workflow_data.get("required_permissions", []),
            splunk_versions=workflow_data.get("splunk_versions", []),

            # Business context
            business_value=workflow_data.get("business_value", ""),
            use_cases=workflow_data.get("use_cases", []),
            success_metrics=workflow_data.get("success_metrics", []),
            industry_focus=workflow_data.get("industry_focus", []),

            # Technical details
            data_requirements=workflow_data.get("data_requirements", {}),
            documentation_url=workflow_data.get("documentation_url", ""),

            # Discovery metadata
            discovery_timestamp=datetime.now().isoformat(),
            validation_status="valid"
        )

    def _group_workflows(self) -> None:
        """Group workflows by various criteria"""
        # Group by category
        self._group_by_category()

        # Group by source
        self._group_by_source()

        # Group by complexity
        self._group_by_complexity()

        # Group by workflow type
        self._group_by_type()

    def _group_by_category(self) -> None:
        """Group workflows by category"""
        categories = {}
        for workflow in self.discovered_workflows.values():
            category = workflow.workflow_category
            if category not in categories:
                categories[category] = []
            categories[category].append(workflow)

        for category, workflows in categories.items():
            group_id = f"category_{category}"
            self.workflow_groups[group_id] = WorkflowGroup(
                group_id=group_id,
                group_name=f"{category.replace('_', ' ').title()} Workflows",
                description=f"Workflows focused on {category.replace('_', ' ')} tasks",
                workflows=workflows,
                total_count=len(workflows)
            )

    def _group_by_source(self) -> None:
        """Group workflows by source (core vs contrib)"""
        sources = {}
        for workflow in self.discovered_workflows.values():
            source = workflow.source.value
            if source not in sources:
                sources[source] = []
            sources[source].append(workflow)

        for source, workflows in sources.items():
            group_id = f"source_{source}"
            self.workflow_groups[group_id] = WorkflowGroup(
                group_id=group_id,
                group_name=f"{source.title()} Workflows",
                description=f"Workflows maintained by {source} team",
                workflows=workflows,
                total_count=len(workflows)
            )

    def _group_by_complexity(self) -> None:
        """Group workflows by complexity level"""
        complexities = {}
        for workflow in self.discovered_workflows.values():
            complexity = workflow.complexity_level.value
            if complexity not in complexities:
                complexities[complexity] = []
            complexities[complexity].append(workflow)

        for complexity, workflows in complexities.items():
            group_id = f"complexity_{complexity}"
            self.workflow_groups[group_id] = WorkflowGroup(
                group_id=group_id,
                group_name=f"{complexity.title()} Workflows",
                description=f"Workflows suitable for {complexity} users",
                workflows=workflows,
                total_count=len(workflows)
            )

    def _group_by_type(self) -> None:
        """Group workflows by type"""
        types = {}
        for workflow in self.discovered_workflows.values():
            workflow_type = workflow.workflow_type
            if workflow_type not in types:
                types[workflow_type] = []
            types[workflow_type].append(workflow)

        for workflow_type, workflows in types.items():
            group_id = f"type_{workflow_type}"
            self.workflow_groups[group_id] = WorkflowGroup(
                group_id=group_id,
                group_name=f"{workflow_type.replace('_', ' ').title()} Workflows",
                description=f"Workflows for {workflow_type.replace('_', ' ')} purposes",
                workflows=workflows,
                total_count=len(workflows)
            )

    def get_workflows_by_criteria(
        self,
        source: WorkflowSource | None = None,
        complexity: ComplexityLevel | None = None,
        workflow_type: str | None = None,
        category: str | None = None,
        stability: WorkflowStability | None = None
    ) -> list[WorkflowInfo]:
        """Filter workflows by multiple criteria"""
        filtered = list(self.discovered_workflows.values())

        if source:
            filtered = [w for w in filtered if w.source == source]
        if complexity:
            filtered = [w for w in filtered if w.complexity_level == complexity]
        if workflow_type:
            filtered = [w for w in filtered if w.workflow_type == workflow_type]
        if category:
            filtered = [w for w in filtered if w.workflow_category == category]
        if stability:
            filtered = [w for w in filtered if w.stability == stability]

        return filtered

    def get_discovery_summary(self) -> dict[str, Any]:
        """Get comprehensive discovery summary"""
        return {
            "discovery_stats": self.discovery_stats,
            "total_workflows": len(self.discovered_workflows),
            "total_groups": len(self.workflow_groups),
            "workflows_by_source": {
                source.value: len([w for w in self.discovered_workflows.values() if w.source == source])
                for source in WorkflowSource
            },
            "workflows_by_complexity": {
                complexity.value: len([w for w in self.discovered_workflows.values() if w.complexity_level == complexity])
                for complexity in ComplexityLevel
            },
            "workflows_by_stability": {
                stability.value: len([w for w in self.discovered_workflows.values() if w.stability == stability])
                for stability in WorkflowStability
            },
            "group_names": list(self.workflow_groups.keys())
        }


# Global discovery instance
_discovery_instance: WorkflowDiscovery | None = None


def get_workflow_discovery() -> WorkflowDiscovery:
    """Get or create global workflow discovery instance"""
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = WorkflowDiscovery()
    return _discovery_instance


def discover_all_workflows(force_refresh: bool = False) -> dict[str, WorkflowInfo]:
    """Convenience function to discover all workflows"""
    discovery = get_workflow_discovery()
    return discovery.discover_workflows(force_refresh=force_refresh)


def get_workflows_by_source(source: WorkflowSource) -> list[WorkflowInfo]:
    """Get workflows filtered by source"""
    discovery = get_workflow_discovery()
    return discovery.get_workflows_by_criteria(source=source)


def get_core_workflows() -> list[WorkflowInfo]:
    """Get all core workflows"""
    return get_workflows_by_source(WorkflowSource.CORE)


def get_contrib_workflows() -> list[WorkflowInfo]:
    """Get all contrib workflows"""
    return get_workflows_by_source(WorkflowSource.CONTRIB)
