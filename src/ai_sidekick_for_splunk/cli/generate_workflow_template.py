#!/usr/bin/env python3
"""
CLI command for generating FlowPilot workflow templates.
This script generates properly formatted workflow templates with Pydantic validation.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

def get_base_path() -> Path:
    """Get the base path for the AI Sidekick source directory."""
    # Find the src/ai_sidekick_for_splunk directory
    current_path = Path.cwd()
    
    # Look for src/ai_sidekick_for_splunk in current directory or parent directories
    for path in [current_path] + list(current_path.parents):
        src_path = path / "src" / "ai_sidekick_for_splunk"
        if src_path.exists():
            return src_path
    
    # If not found, assume we're running from the package directory
    return Path(__file__).parent.parent

def create_workflow_template(
    name: str,
    workflow_type: str,
    category: str,
    source: str,
    complexity: str,
    stability: str,
    description: str,
    business_value: str
) -> Dict[str, Any]:
    """Create a properly formatted workflow template."""
    
    # Ensure name follows the pattern requirements (lowercase, underscores only)
    clean_name = name.lower().replace('-', '_').replace(' ', '_')
    # Remove any non-alphanumeric characters except underscores
    clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
    
    workflow_id = f"{source}.{clean_name}"
    
    return {
        "workflow_id": workflow_id,
        "workflow_name": name.replace('_', ' ').title(),
        "workflow_type": workflow_type,
        "workflow_category": category,
        "source": source,
        "maintainer": "community" if source == "contrib" else "core_team",
        "stability": stability,
        "complexity_level": complexity,
        "estimated_duration": "2-5 minutes",
        "version": "1.0.0",
        "splunk_versions": ["8.0+", "9.0+"],
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "documentation_url": "./README.md",
        "description": description,
        "business_value": business_value,
        "use_cases": [
            "Add your specific use cases here",
            "Example: Performance monitoring",
            "Example: Health assessment"
        ],
        "prerequisites": {
            "splunk_access": True,
            "mcp_server": True,
            "permissions": ["search", "rest_api"]
        },
        "workflow_instructions": {
            "persona": f"You are a {name.replace('_', ' ').title()} agent that helps with {category} tasks.",
            "approach": "Execute each phase systematically, providing clear explanations and actionable insights.",
            "tone": "Professional and helpful"
        },
        "agent_dependencies": {
            "splunk_mcp": {
                "agent_id": "splunk_mcp",
                "required": True,
                "description": "Splunk MCP server for executing searches and gathering information",
                "capabilities": ["search_execution", "index_listing", "system_info_retrieval"]
            },
            "result_synthesizer": {
                "agent_id": "result_synthesizer",
                "required": True,
                "description": "Synthesizes results from multiple phases into comprehensive reports",
                "capabilities": ["result_synthesis", "report_generation", "summary_creation"]
            }
        },
        "core_phases": {
            "data_gathering": {
                "name": "data_gathering",
                "phase_name": "Data Gathering",
                "description": "Collect relevant information from Splunk environment",
                "tasks": [
                    {
                        "task_id": "gather_initial_data",
                        "title": "Gather Initial Data",
                        "tool": "splunk_mcp",
                        "goal": "Collect baseline information for analysis",
                        "prompt": "Please gather the initial data needed for this workflow. Customize this prompt based on your specific requirements.",
                        "expected_output": "Relevant data and information for the workflow"
                    }
                ]
            },
            "analysis": {
                "name": "analysis", 
                "phase_name": "Analysis",
                "description": "Analyze the gathered data and identify patterns or issues",
                "tasks": [
                    {
                        "task_id": "perform_analysis",
                        "title": "Perform Analysis",
                        "tool": "splunk_mcp",
                        "goal": "Analyze the data and identify key insights",
                        "prompt": "Based on the gathered data, perform analysis to identify patterns, issues, or insights. Customize this analysis based on your workflow requirements.",
                        "expected_output": "Analysis results with key findings and insights"
                    }
                ]
            },
            "summary": {
                "name": "summary",
                "phase_name": "Summary Report",
                "description": "Generate comprehensive summary with recommendations",
                "tasks": [
                    {
                        "task_id": "generate_summary",
                        "title": "Generate Summary",
                        "tool": "result_synthesizer",
                        "goal": "Create comprehensive summary report",
                        "prompt": "Based on the data gathering and analysis phases, create a comprehensive summary report with key findings, insights, and actionable recommendations.",
                        "expected_output": "Comprehensive summary report with recommendations"
                    }
                ]
            }
        }
    }

def create_readme(name: str, workflow_name: str, description: str, business_value: str) -> str:
    """Create a README template for the workflow."""
    return f"""# {workflow_name}

## Overview

{description}

## Business Value

{business_value}

## Workflow Phases

### Phase 1: Data Gathering
- Collects relevant information from the Splunk environment
- Establishes baseline data for analysis
- Prepares data for subsequent phases

### Phase 2: Analysis
- Analyzes the gathered data
- Identifies patterns, trends, and potential issues
- Generates insights based on the analysis

### Phase 3: Summary Report
- Compiles findings into a comprehensive report
- Provides actionable recommendations
- Delivers clear next steps

## Usage

1. **Start AI Sidekick**: Ensure the AI Sidekick is running
2. **Find the Agent**: Look for '{workflow_name}' in the agent list
3. **Query**: Provide a query relevant to this workflow's purpose
4. **Review Results**: Examine the multi-phase workflow execution results

## Customization

This template provides a basic structure. Customize the following:

- **Workflow Instructions**: Update the persona, approach, and tone
- **Phase Tasks**: Modify tasks to match your specific requirements
- **Prompts**: Customize prompts for your use case
- **Expected Outputs**: Define what each task should produce
- **Dependencies**: Add or remove agent dependencies as needed

## Prerequisites

- Splunk access with appropriate permissions
- MCP server connectivity
- Search and REST API permissions

## Expected Duration

2-5 minutes (customize based on your workflow complexity)

## Support

For questions or issues with this workflow, please refer to the project documentation or create an issue in the repository.
"""

def main():
    """Main CLI function for generating workflow templates."""
    parser = argparse.ArgumentParser(
        description="Generate FlowPilot workflow templates with proper validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-sidekick-generate-template --name security_audit --type security --category security --source contrib
  ai-sidekick-generate-template --name performance_check --type monitoring --category performance --source core
  ai-sidekick-generate-template --name custom_analysis --type analysis --category troubleshooting --source contrib
        """
    )
    
    parser.add_argument(
        "--name",
        required=True,
        help="Name for the workflow (e.g., 'security_audit', 'performance_check')"
    )
    
    parser.add_argument(
        "--type",
        required=True,
        choices=["troubleshooting", "monitoring", "analysis", "security", "onboarding", "maintenance"],
        help="Type of workflow"
    )
    
    parser.add_argument(
        "--category", 
        required=True,
        choices=["system_health", "performance", "security", "data_quality", "troubleshooting", "monitoring"],
        help="Category of workflow"
    )
    
    parser.add_argument(
        "--source",
        required=True,
        choices=["core", "contrib"],
        help="Source type (core for built-in, contrib for community)"
    )
    
    parser.add_argument(
        "--complexity",
        choices=["beginner", "intermediate", "advanced"],
        default="intermediate",
        help="Complexity level (default: intermediate)"
    )
    
    parser.add_argument(
        "--stability",
        choices=["experimental", "beta", "stable"],
        default="experimental", 
        help="Stability level (default: experimental)"
    )
    
    parser.add_argument(
        "--description",
        help="Description of the workflow",
        default="A workflow template for custom analysis and reporting"
    )
    
    parser.add_argument(
        "--business-value",
        help="Business value description",
        default="Provides automated analysis and insights for improved operational efficiency"
    )
    
    parser.add_argument(
        "--output-dir",
        help="Output directory (default: SOURCE/flows/NAME)",
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        # Get base path
        base_path = get_base_path()
        
        # Determine output directory
        if args.output_dir:
            output_dir = Path(args.output_dir)
        else:
            output_dir = base_path / args.source / "flows" / args.name
        
        # Create directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create workflow template
        workflow_template = create_workflow_template(
            args.name,
            args.type,
            args.category,
            args.source,
            args.complexity,
            args.stability,
            args.description,
            args.business_value
        )
        
        workflow_file = output_dir / f"{args.name}.json"
        
        with open(workflow_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_template, f, indent=2, ensure_ascii=False)
        
        # Create README
        readme_content = create_readme(
            args.name,
            workflow_template["workflow_name"],
            args.description,
            args.business_value
        )
        readme_file = output_dir / "README.md"
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Success output
        print(f"✅ Created workflow template: {workflow_file.relative_to(Path.cwd())}")
        print(f"✅ Created README: {readme_file.relative_to(Path.cwd())}")
        print()
        print("🎉 Workflow template created successfully!")
        print("=" * 40)
        print(f"📁 Directory: {output_dir.relative_to(base_path)}")
        print(f"📄 Template: {workflow_file.relative_to(output_dir)}")
        print(f"📖 README: {readme_file.relative_to(output_dir)}")
        print()
        print("🚀 Next steps:")
        print("1. Review and customize the generated template")
        print("2. Test the workflow with FlowPilot")
        print("3. Update the README with specific details")
        print("4. The workflow will be automatically discovered by the system!")
        
    except Exception as e:
        print(f"❌ Error creating workflow template: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
