#!/usr/bin/env python3
"""
Workflow Template Generator

This script generates properly formatted workflow JSON templates with all required fields
and sensible defaults, making it easy for contributors to create new workflows without
dealing with complex validation issues.

Usage:
    python generate_workflow_template.py --name "My Workflow" --type analysis --category data_analysis
    python generate_workflow_template.py --interactive
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def get_template_skeleton() -> dict[str, Any]:
    """Get the basic workflow template structure with all required fields."""
    return {
        "workflow_id": "",
        "workflow_name": "",
        "workflow_type": "analysis",
        "workflow_category": "data_analysis",
        "source": "contrib",
        "maintainer": "Community",
        "stability": "experimental",
        "complexity_level": "beginner",
        "estimated_duration": "5-10 minutes",
        "version": "1.0.0",
        "splunk_versions": ["8.0+", "9.0+"],
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "documentation_url": "./README.md",
        "description": "",
        "agent": "",
        "target_audience": ["splunk_admin", "data_analyst"],
        "prerequisites": ["splunk_mcp_server"],
        "required_permissions": ["search"],
        "business_value": "",
        "use_cases": ["system_monitoring", "performance_analysis"],
        "success_metrics": ["improved_performance", "reduced_response_time"],
        "industry_focus": [],
        "data_requirements": {
            "minimum_events": 100,
            "required_sourcetypes": [],
            "optional_fields": []
        },
        "workflow_instructions": {
            "specialization": "",
            "focus_areas": [],
            "execution_style": "sequential",
            "domain": ""
        },
        "agent_dependencies": {
            "result_synthesizer": {
                "agent_id": "result_synthesizer",
                "description": "Synthesize and format results",
                "required": True,
                "capabilities": [
                    "result_synthesis",
                    "report_generation"
                ],
                "integration_points": [
                    "final_report_generation"
                ]
            },
            "splunk_mcp": {
                "agent_id": "splunk_mcp",
                "description": "Execute Splunk searches and operations",
                "required": True,
                "capabilities": [
                    "search_execution",
                    "system_information"
                ],
                "integration_points": [
                    "data_collection"
                ]
            }
        },
        "core_phases": {
            "data_collection": {
                "name": "Data Collection",
                "description": "Gather required data from Splunk",
                "mandatory": True,
                "parallel": False,
                "tasks": [
                    {
                        "task_id": "collect_data",
                        "title": "Collect Data",
                        "description": "Execute searches to collect required data",
                        "goal": "Gather data for analysis",
                        "agent": "splunk_mcp",
                        "tool": "execute_search",
                        "type": "data_collection"
                    }
                ]
            },
            "analysis": {
                "name": "Analysis",
                "description": "Analyze collected data",
                "mandatory": True,
                "parallel": False,
                "tasks": [
                    {
                        "task_id": "analyze_data",
                        "title": "Analyze Data",
                        "description": "Process and analyze the collected data",
                        "goal": "Extract insights from data",
                        "agent": "result_synthesizer",
                        "tool": "synthesize_results",
                        "type": "analysis"
                    }
                ]
            }
        },
        "tasks": [
            {
                "id": 1,
                "name": "collect_data",
                "description": "Collect required data from Splunk",
                "type": "data_collection",
                "agent": "splunk_mcp",
                "prompt": "Execute searches to collect the required data for analysis",
                "expected_output": "Search results and data",
                "dependencies": []
            },
            {
                "id": 2,
                "name": "analyze_results",
                "description": "Analyze and synthesize the collected data",
                "type": "synthesis",
                "agent": "result_synthesizer",
                "prompt": "Analyze the collected data and provide insights and recommendations",
                "expected_output": "Analysis report with insights",
                "dependencies": [1]
            }
        ],
        "expected_outcome": "",
        "troubleshooting": {
            "common_issues": [
                {
                    "issue": "No data found",
                    "solution": "Check data availability and search time range"
                }
            ]
        }
    }


def get_workflow_types() -> list[str]:
    """Get available workflow types."""
    return ["analysis", "troubleshooting", "performance", "onboarding", "security", "monitoring"]


def get_workflow_categories() -> list[str]:
    """Get available workflow categories."""
    return ["data_analysis", "system_health", "security_audit", "performance_tuning", "infrastructure_monitoring"]


def get_complexity_levels() -> list[str]:
    """Get available complexity levels."""
    return ["beginner", "intermediate", "advanced", "expert"]


def get_sources() -> list[str]:
    """Get available sources."""
    return ["core", "contrib"]


def get_stability_levels() -> list[str]:
    """Get available stability levels."""
    return ["stable", "experimental", "deprecated"]


def interactive_mode() -> dict[str, Any]:
    """Interactive mode for creating workflow templates."""
    print("🎯 Interactive Workflow Template Generator")
    print("==========================================")
    print()

    template = get_template_skeleton()

    # Basic information
    print("📋 BASIC INFORMATION:")
    print("=====================")
    workflow_name = input("Workflow name: ").strip()
    if not workflow_name:
        print("❌ Workflow name is required!")
        sys.exit(1)

    template["workflow_name"] = workflow_name
    template["workflow_id"] = f"contrib.{workflow_name.lower().replace(' ', '_').replace('-', '_')}"
    template["agent"] = f"FlowPilot_{workflow_name.replace(' ', '_')}"

    description = input("Description: ").strip()
    template["description"] = description or f"Workflow for {workflow_name}"

    # Workflow type
    print(f"\n📊 WORKFLOW TYPE (choose from: {', '.join(get_workflow_types())}):")
    workflow_type = input("Type [analysis]: ").strip() or "analysis"
    if workflow_type not in get_workflow_types():
        print("⚠️ Invalid type. Using 'analysis'")
        workflow_type = "analysis"
    template["workflow_type"] = workflow_type

    # Category
    print(f"\n📂 CATEGORY (choose from: {', '.join(get_workflow_categories())}):")
    category = input("Category [data_analysis]: ").strip() or "data_analysis"
    if category not in get_workflow_categories():
        print("⚠️ Invalid category. Using 'data_analysis'")
        category = "data_analysis"
    template["workflow_category"] = category

    # Complexity
    print(f"\n🎚️ COMPLEXITY (choose from: {', '.join(get_complexity_levels())}):")
    complexity = input("Complexity [beginner]: ").strip() or "beginner"
    if complexity not in get_complexity_levels():
        print("⚠️ Invalid complexity. Using 'beginner'")
        complexity = "beginner"
    template["complexity_level"] = complexity

    # Source
    print(f"\n📦 SOURCE (choose from: {', '.join(get_sources())}):")
    source = input("Source [contrib]: ").strip() or "contrib"
    if source not in get_sources():
        print("⚠️ Invalid source. Using 'contrib'")
        source = "contrib"
    template["source"] = source

    # Business value
    print("\n💼 BUSINESS VALUE:")
    business_value = input("Business value: ").strip()
    template["business_value"] = business_value or f"Provides insights for {workflow_name}"

    # Expected outcome
    template["expected_outcome"] = f"Successfully complete {workflow_name} workflow"

    # Update specialization
    template["workflow_instructions"]["specialization"] = f"{workflow_name.upper()} SPECIALIZATION"
    template["workflow_instructions"]["domain"] = category

    return template


def cli_mode(args) -> dict[str, Any]:
    """CLI mode for creating workflow templates."""
    template = get_template_skeleton()

    # Required fields
    template["workflow_name"] = args.name
    template["workflow_id"] = f"{args.source}.{args.name.lower().replace(' ', '_').replace('-', '_')}"
    template["agent"] = f"FlowPilot_{args.name.replace(' ', '_')}"
    template["workflow_type"] = args.type
    template["workflow_category"] = args.category
    template["source"] = args.source
    template["complexity_level"] = args.complexity
    template["stability"] = args.stability

    # Optional fields
    if args.description:
        template["description"] = args.description
    else:
        template["description"] = f"Workflow for {args.name}"

    if args.business_value:
        template["business_value"] = args.business_value
    else:
        template["business_value"] = f"Provides insights for {args.name}"

    # Update specialization
    template["workflow_instructions"]["specialization"] = f"{args.name.upper()} SPECIALIZATION"
    template["workflow_instructions"]["domain"] = args.category
    template["expected_outcome"] = f"Successfully complete {args.name} workflow"

    return template


def create_readme(workflow_name: str, description: str, output_dir: Path) -> None:
    """Create a README.md file for the workflow."""
    readme_content = f"""# {workflow_name}

## Overview

{description}

## Purpose

This workflow provides automated analysis and insights for {workflow_name.lower()}.

## What This Workflow Does

1. **Data Collection**: Gathers required data from Splunk
2. **Analysis**: Processes and analyzes the collected data
3. **Report Generation**: Creates actionable insights and recommendations

## Target Audience

- Splunk Administrators
- Data Analysts
- System Engineers

## Prerequisites

- Access to Splunk MCP server
- Appropriate search permissions
- Basic Splunk knowledge

## Usage

This workflow can be executed through:
- ADK Web interface
- Direct FlowPilot agent calls
- Orchestrator workflow selection

## Expected Outcomes

- Comprehensive analysis results
- Actionable recommendations
- Clear insights for decision making

## Contributing

To modify this workflow:
1. Edit the JSON template with your changes
2. Test the workflow thoroughly
3. Update this README with any new requirements or changes
"""

    readme_path = output_dir / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)

    print(f"✅ Created README: {readme_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate workflow templates for FlowPilot")
    parser.add_argument("--name", help="Workflow name")
    parser.add_argument("--type", choices=get_workflow_types(), default="analysis", help="Workflow type")
    parser.add_argument("--category", choices=get_workflow_categories(), default="data_analysis", help="Workflow category")
    parser.add_argument("--source", choices=get_sources(), default="contrib", help="Source (core or contrib)")
    parser.add_argument("--complexity", choices=get_complexity_levels(), default="beginner", help="Complexity level")
    parser.add_argument("--stability", choices=get_stability_levels(), default="experimental", help="Stability level")
    parser.add_argument("--description", help="Workflow description")
    parser.add_argument("--business-value", help="Business value description")
    parser.add_argument("--output-dir", help="Output directory (default: contrib/flows/WORKFLOW_NAME)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    # Determine mode
    if args.interactive:
        template = interactive_mode()
    elif args.name:
        template = cli_mode(args)
    else:
        print("❌ Either --name or --interactive is required")
        parser.print_help()
        sys.exit(1)

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        workflow_dir_name = template["workflow_name"].lower().replace(' ', '_').replace('-', '_')

        # Get the correct base path relative to the script location
        script_dir = Path(__file__).parent  # scripts/
        src_root = script_dir.parent  # src/ai_sidekick_for_splunk/

        if template["source"] == "core":
            output_dir = src_root / "core" / "flows" / workflow_dir_name
        else:
            output_dir = src_root / "contrib" / "flows" / workflow_dir_name

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write JSON template
    json_filename = f"{template['workflow_name'].lower().replace(' ', '_').replace('-', '_')}.json"
    json_path = output_dir / json_filename

    with open(json_path, 'w') as f:
        json.dump(template, f, indent=2)

    print(f"✅ Created workflow template: {json_path}")

    # Create README
    create_readme(template["workflow_name"], template["description"], output_dir)

    print()
    print("🎉 Workflow template created successfully!")
    print("=======================================")
    print(f"📁 Directory: {output_dir}")
    print(f"📄 Template: {json_path}")
    print(f"📖 README: {output_dir / 'README.md'}")
    print()
    print("🚀 Next steps:")
    print("1. Review and customize the generated template")
    print("2. Test the workflow with FlowPilot")
    print("3. Update the README with specific details")
    print("4. The workflow will be automatically discovered by the system!")


if __name__ == "__main__":
    main()
