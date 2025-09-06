"""
Template-to-JSON generator for converting simple YAML templates to complex FlowPilot JSON workflows.

This module takes validated SimpleTemplate instances and generates the full
FlowPilot JSON workflow structure with all required fields and dependencies.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...core.flows_engine.workflow_models import (
    AgentDependency,
    DataRequirements,
    WorkflowCategory,
    WorkflowSource,
    WorkflowStability,
    WorkflowTemplate,
    WorkflowType,
    ComplexityLevel as FlowComplexityLevel,
)
from .template_models import SimpleTemplate, SearchDefinition, PhaseDefinition

logger = logging.getLogger(__name__)


class TemplateGenerator:
    """
    Generator that converts SimpleTemplate instances to FlowPilot JSON workflows.
    """
    
    def __init__(self):
        """Initialize the template generator."""
        self.default_dependencies = {
            "splunk_mcp": {
                "agent_id": "splunk_mcp",
                "description": "Splunk operations and search execution specialist",
                "required": True,
                "capabilities": [
                    "search_execution",
                    "system_information",
                    "rest_api_access"
                ],
                "integration_points": [
                    "search_workflow",
                    "data_retrieval"
                ]
            },
            "result_synthesizer": {
                "agent_id": "result_synthesizer",
                "description": "Result analysis and synthesis specialist",
                "required": True,
                "capabilities": [
                    "result_analysis",
                    "insight_generation",
                    "report_synthesis"
                ],
                "integration_points": [
                    "result_processing",
                    "final_synthesis"
                ]
            }
        }
    
    def generate_workflow_json(self, template: SimpleTemplate, output_dir: Path) -> Dict[str, Any]:
        """
        Generate complete FlowPilot JSON workflow from template.
        
        Args:
            template: Validated SimpleTemplate instance
            output_dir: Directory where the workflow will be saved
            
        Returns:
            Complete workflow JSON as dictionary
        """
        logger.info(f"🔄 Generating FlowPilot JSON for template '{template.metadata.name}'")
        
        # Build the complete workflow structure
        workflow_json = {
            # Basic metadata
            "workflow_id": f"contrib.{template.metadata.name}",
            "workflow_name": template.metadata.title,
            "version": template.metadata.version,
            "description": template.metadata.description,
            
            # Classification
            "workflow_type": self._map_category_to_type(template.metadata.category),
            "workflow_category": self._map_category_to_workflow_category(template.metadata.category),
            "source": "contrib",
            "maintainer": template.metadata.author,
            "stability": "experimental",
            "complexity_level": self._map_complexity_level(template.metadata.complexity),
            "estimated_duration": template.advanced_options.estimated_duration,
            
            # Agent assignment for FlowPilot
            "agent": f"FlowPilot_{template.metadata.name.replace('_', '')}",
            
            # Timestamps and versioning
            "last_updated": template.metadata.last_updated,
            "documentation_url": "./README.md",
            
            # Requirements
            "splunk_versions": template.requirements.splunk_versions,
            "required_permissions": template.requirements.required_permissions,
            "prerequisites": self._generate_prerequisites(template),
            
            # Business context
            "business_value": template.business_context.business_value,
            "use_cases": template.business_context.use_cases,
            "success_metrics": template.business_context.success_metrics or ["Successful completion of workflow phases", "Actionable insights generated"],
            "target_audience": template.business_context.target_audience or ["splunk_user"],
            
            # Data requirements
            "data_requirements": self._generate_data_requirements(template),
            
            # Workflow instructions
            "workflow_instructions": self._generate_workflow_instructions(template),
            
            # Agent dependencies
            "agent_dependencies": self._generate_agent_dependencies(template),
            
            # Core phases
            "core_phases": self._generate_core_phases(template),
            
            # Execution flow configuration
            "execution_flow": self._generate_execution_flow(template),
            
            # Output structure
            "output_structure": self._generate_output_structure(template),
        }
        
        logger.info(f"✅ Generated FlowPilot JSON with {len(workflow_json['core_phases'])} phases")
        return workflow_json
    
    def save_workflow_json(self, workflow_json: Dict[str, Any], output_path: Path) -> None:
        """
        Save workflow JSON to file.
        
        Args:
            workflow_json: Complete workflow JSON dictionary
            output_path: Path where to save the JSON file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_json, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Saved FlowPilot JSON to {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save workflow JSON to {output_path}: {e}")
            raise
    
    def generate_readme(self, template: SimpleTemplate, workflow_json: Dict[str, Any]) -> str:
        """
        Generate README.md content for the workflow.
        
        Args:
            template: SimpleTemplate instance
            workflow_json: Generated workflow JSON
            
        Returns:
            README.md content as string
        """
        readme_content = f"""# {template.metadata.title}

{template.metadata.description}

## Overview

**Category:** {template.metadata.category.title()}  
**Complexity:** {template.metadata.complexity.title()}  
**Estimated Duration:** {template.advanced_options.estimated_duration}  
**Author:** {template.metadata.author}  
**Version:** {template.metadata.version}

## Business Value

{template.business_context.business_value}

## Use Cases

"""
        
        for use_case in template.business_context.use_cases:
            readme_content += f"- {use_case}\n"
        
        readme_content += f"""
## Requirements

**Splunk Versions:** {', '.join(template.requirements.splunk_versions)}  
**Required Permissions:** {', '.join(template.requirements.required_permissions)}
"""
        
        if template.requirements.required_indexes:
            readme_content += f"**Required Indexes:** {', '.join(template.requirements.required_indexes)}\n"
        
        readme_content += """
## Workflow Phases

"""
        
        # Document phases and searches
        if template.searches:
            readme_content += "### Main Analysis Phase\n\n"
            for search in template.searches:
                readme_content += f"**{search.name}:**\n"
                readme_content += f"- Description: {search.description}\n"
                readme_content += f"- SPL: `{search.spl}`\n"
                if search.earliest != "-24h@h" or search.latest != "now":
                    readme_content += f"- Time Range: {search.earliest} to {search.latest}\n"
                readme_content += "\n"
        
        elif template.phases:
            for phase in template.phases:
                readme_content += f"### {phase.title}\n\n"
                readme_content += f"{phase.description}\n\n"
                
                for search in phase.searches:
                    readme_content += f"**{search.name}:**\n"
                    readme_content += f"- Description: {search.description}\n"
                    readme_content += f"- SPL: `{search.spl}`\n"
                    if search.earliest != "-24h@h" or search.latest != "now":
                        readme_content += f"- Time Range: {search.earliest} to {search.latest}\n"
                    readme_content += "\n"
        
        readme_content += """## Usage

1. **Start AI Sidekick:** Ensure your AI Sidekick is running
2. **Select Agent:** Choose the FlowPilot agent from the dropdown
3. **Execute Workflow:** Use the command or describe your analysis needs
4. **Review Results:** Examine the comprehensive analysis and recommendations

## Success Metrics

"""
        
        if template.business_context.success_metrics:
            for metric in template.business_context.success_metrics:
                readme_content += f"- {metric}\n"
        else:
            readme_content += "- Successful completion of all workflow phases\n- Actionable insights generated\n- Clear recommendations provided\n"
        
        readme_content += f"""
## Template Information

This workflow was generated from a YAML template on {datetime.now().strftime('%Y-%m-%d')}.

**Template Version:** {template.metadata.version}  
**Template Format:** {template.metadata.template_format}  
**Generated JSON:** `{template.metadata.name}.json`

To modify this workflow, edit the `{template.metadata.name}.yaml` template file and regenerate.
"""
        
        return readme_content
    
    def _map_category_to_type(self, category: str) -> str:
        """Map template category to workflow type."""
        mapping = {
            "security": "analysis",
            "performance": "monitoring",
            "troubleshooting": "troubleshooting",
            "analysis": "analysis",
            "monitoring": "monitoring",
            "data_quality": "analysis",
        }
        return mapping.get(category, "analysis")
    
    def _map_category_to_workflow_category(self, category: str) -> str:
        """Map template category to workflow category."""
        mapping = {
            "security": "security_audit",
            "performance": "performance_tuning",
            "troubleshooting": "system_health",
            "analysis": "data_analysis",
            "monitoring": "system_health",
            "data_quality": "data_analysis",
        }
        return mapping.get(category, "data_analysis")
    
    def _map_complexity_level(self, complexity: str) -> str:
        """Map template complexity to workflow complexity."""
        return complexity  # Direct mapping
    
    def _generate_prerequisites(self, template: SimpleTemplate) -> List[str]:
        """Generate prerequisites list."""
        prerequisites = ["splunk_mcp_server", "basic_splunk_access"]
        
        if template.requirements.required_indexes:
            prerequisites.append("required_indexes_available")
        
        if template.requirements.dependencies:
            prerequisites.extend([f"{dep}_agent_available" for dep in template.requirements.dependencies])
        
        return prerequisites
    
    def _generate_data_requirements(self, template: SimpleTemplate) -> Dict[str, Any]:
        """Generate data requirements."""
        return {
            "minimum_events": 100,
            "required_sourcetypes": template.requirements.required_indexes or [],
            "optional_fields": ["host", "source", "index"],
            "data_types": [template.metadata.category.replace('_', ' ').title()]
        }
    
    def _generate_workflow_instructions(self, template: SimpleTemplate) -> Dict[str, Any]:
        """Generate workflow instructions for FlowPilot."""
        focus_areas = [
            f"Focus on {template.metadata.category.replace('_', ' ')} analysis",
            f"Execute searches systematically and thoroughly",
            f"Provide clear insights and actionable recommendations",
        ]
        
        if template.advanced_options.parallel_execution:
            focus_areas.append("Utilize parallel execution where possible for efficiency")
        
        if template.advanced_options.educational_mode:
            focus_areas.append("Include educational explanations for learning purposes")
        
        return {
            "specialization": f"{template.metadata.category.upper().replace('_', ' ')} SPECIALIZATION",
            "focus_areas": focus_areas,
            "execution_style": "parallel" if template.advanced_options.parallel_execution else "sequential",
            "domain": template.metadata.category
        }
    
    def _generate_agent_dependencies(self, template: SimpleTemplate) -> Dict[str, Any]:
        """Generate agent dependencies."""
        dependencies = self.default_dependencies.copy()
        
        # Add custom dependencies if specified
        if template.requirements.dependencies:
            for dep in template.requirements.dependencies:
                if dep not in dependencies:
                    dependencies[dep] = {
                        "agent_id": dep,
                        "description": f"Custom {dep} agent for specialized functionality",
                        "required": True,
                        "capabilities": ["custom_functionality"],
                        "integration_points": ["workflow_integration"]
                    }
        
        return dependencies
    
    def _generate_core_phases(self, template: SimpleTemplate) -> Dict[str, Any]:
        """Generate core phases from template."""
        phases = {}
        
        if template.searches:
            # Simple template - create single phase
            phase_name = "main_analysis"
            phases[phase_name] = self._create_phase_from_searches(
                phase_name=phase_name,
                phase_title="Main Analysis",
                phase_description=f"{template.metadata.title} - Primary analysis phase",
                searches=template.searches,
                parallel=template.advanced_options.parallel_execution
            )
        
        elif template.phases:
            # Complex template - create multiple phases
            for phase_def in template.phases:
                phases[phase_def.name] = self._create_phase_from_searches(
                    phase_name=phase_def.name,
                    phase_title=phase_def.title,
                    phase_description=phase_def.description,
                    searches=phase_def.searches,
                    parallel=phase_def.parallel or template.advanced_options.parallel_execution,
                    depends_on=phase_def.depends_on
                )
        
        return phases
    
    def _create_phase_from_searches(
        self,
        phase_name: str,
        phase_title: str,
        phase_description: str,
        searches: List[SearchDefinition],
        parallel: bool = False,
        depends_on: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a phase definition from searches."""
        
        # Convert searches to tasks format (required by FlowPilot)
        tasks = []
        for search in searches:
            task = {
                "task_id": search.name,
                "title": getattr(search, 'title', search.name.replace('_', ' ').title()),
                "description": search.description,
                "goal": f"Execute {search.name} search",
                "tool": "run_splunk_search",
                "search_query": search.spl,
                "parameters": {
                    "earliest_time": search.earliest,
                    "latest_time": search.latest
                },
                "timeout_sec": search.timeout,
                "expected_output": search.expected_results or search.description,
                "analysis_focus": [search.description]
            }
            tasks.append(task)
        
        phase = {
            "name": phase_title,
            "description": phase_description,
            "mandatory": True,
            "parallel": parallel,
            "max_parallel": min(len(tasks), 6) if parallel else 1,
            "tasks": tasks,
            "success_criteria": [
                "All searches completed successfully",
                "Results available for analysis",
                "No critical errors encountered"
            ]
        }
        
        if depends_on:
            phase["depends_on"] = depends_on
        
        return phase
    
    def _generate_execution_flow(self, template: SimpleTemplate) -> Dict[str, Any]:
        """Generate execution flow configuration."""
        phase_names = []
        
        # Get phase names from template
        if template.phases:
            phase_names = [phase.name for phase in template.phases]
        else:
            phase_names = ["main_analysis"]
        
        return {
            "phase_order": phase_names,
            "error_handling": {
                "continue_on_task_failure": True,
                "max_failed_tasks_per_phase": 3,
                "retry_failed_tasks": True,
                "max_retries": 2
            },
            "performance_targets": {
                "max_total_execution_time": 600,
                "max_phase_execution_time": 300,
                "parallel_execution_timeout": 180
            },
            "adaptive_behavior": {
                "skip_slow_tasks": False,
                "prioritize_critical_checks": True,
                "dynamic_timeout_adjustment": True
            }
        }
    
    def _generate_output_structure(self, template: SimpleTemplate) -> Dict[str, Any]:
        """Generate output structure configuration."""
        return {
            "health_status": {
                "overall_status": "string",
                "component_status": "object",
                "critical_alerts": "array",
                "performance_metrics": "object",
                "recommendations": "array"
            },
            "execution_metadata": {
                "total_execution_time": "number",
                "checks_completed": "number",
                "checks_failed": "number",
                "timestamp": "string"
            }
        }


# Convenience functions
def generate_workflow_from_template(template: SimpleTemplate, output_dir: Path, workflow_name: str = None) -> tuple[Dict[str, Any], str]:
    """
    Generate workflow JSON and README from template.
    
    Args:
        template: Validated SimpleTemplate instance
        output_dir: Output directory
        workflow_name: Override name for the workflow (defaults to template name)
        
    Returns:
        Tuple of (workflow_json, readme_content)
    """
    generator = TemplateGenerator()
    
    # Override template name if workflow_name is provided
    if workflow_name:
        # Create a copy of the template with the new name
        template_dict = template.model_dump()
        template_dict['metadata']['name'] = workflow_name
        from .template_models import SimpleTemplate
        template = SimpleTemplate(**template_dict)
    
    workflow_json = generator.generate_workflow_json(template, output_dir)
    readme_content = generator.generate_readme(template, workflow_json)
    
    return workflow_json, readme_content
