#!/usr/bin/env python3
"""
Interactive Template Generator for FlowPilot YAML Templates.

This tool helps contributors create YAML templates through an interactive process,
reducing the learning curve and preventing common mistakes.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any

from ai_sidekick_for_splunk.core.utils.cross_platform import safe_print


def get_user_input(prompt: str, default: str = "", required: bool = True) -> str:
    """Get user input with optional default and validation."""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if user_input or not required:
            return user_input
        
        safe_print("❌ This field is required. Please provide a value.")


def get_list_input(prompt: str, min_items: int = 1) -> List[str]:
    """Get list input from user."""
    safe_print(f"\n{prompt}")
    safe_print("Enter items one per line. Press Enter twice when done.")
    
    items = []
    while True:
        item = input(f"  {len(items) + 1}. ").strip()
        if not item:
            if len(items) >= min_items:
                break
            else:
                safe_print(f"❌ Please provide at least {min_items} item(s).")
                continue
        items.append(item)
    
    return items


def get_choice(prompt: str, choices: List[str], default: str = "") -> str:
    """Get user choice from a list of options."""
    safe_print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        marker = " (default)" if choice == default else ""
        safe_print(f"  {i}. {choice}{marker}")
    
    while True:
        try:
            choice_input = input(f"Choose 1-{len(choices)}" + (f" [{choices.index(default) + 1}]" if default else "") + ": ").strip()
            
            if not choice_input and default:
                return default
            
            choice_num = int(choice_input)
            if 1 <= choice_num <= len(choices):
                return choices[choice_num - 1]
            else:
                safe_print(f"❌ Please choose a number between 1 and {len(choices)}")
        except ValueError:
            safe_print("❌ Please enter a valid number")


def create_search_definition() -> Dict[str, Any]:
    """Create a search definition interactively."""
    safe_print("\n" + "="*50)
    safe_print("🔍 SEARCH DEFINITION")
    safe_print("="*50)
    
    search = {}
    
    # Basic search info
    search["name"] = get_user_input("Search name (e.g., 'failed_logins', 'system_health')")
    search["title"] = get_user_input("Search title (human-readable)", search["name"].replace("_", " ").title())
    search["description"] = get_user_input("What does this search do?")
    
    # SPL Query
    safe_print("\n📝 SPL Query:")
    safe_print("Enter your Splunk search query. You can use multiple lines.")
    safe_print("Press Ctrl+D (Unix) or Ctrl+Z+Enter (Windows) when done:")
    
    spl_lines = []
    try:
        while True:
            line = input()
            spl_lines.append(line)
    except EOFError:
        pass
    
    search["spl"] = "\n".join(spl_lines).strip()
    
    if not search["spl"]:
        search["spl"] = get_user_input("SPL Query (required)", required=True)
    
    # Time range
    safe_print("\n⏰ Time Range:")
    time_presets = [
        "-15m@m (Last 15 minutes)",
        "-1h@h (Last hour)", 
        "-24h@h (Last 24 hours)",
        "-7d@d (Last 7 days)",
        "custom"
    ]
    
    time_choice = get_choice("Select time range:", time_presets, "-24h@h (Last 24 hours)")
    
    if "custom" in time_choice:
        search["earliest"] = get_user_input("Earliest time (Splunk format)", "-24h@h")
        search["latest"] = get_user_input("Latest time (Splunk format)", "now")
    else:
        # Extract the time format from the choice
        search["earliest"] = time_choice.split()[0]
        search["latest"] = "now"
    
    # Expected results
    search["expected_results"] = get_user_input(
        "What results do you expect? (helps users understand output)",
        f"Results from {search['name']} search",
        required=False
    )
    
    return search


def create_phase_definition() -> Dict[str, Any]:
    """Create a phase definition interactively."""
    safe_print("\n" + "="*50)
    safe_print("📋 PHASE DEFINITION")
    safe_print("="*50)
    
    phase = {}
    
    phase["name"] = get_user_input("Phase name (e.g., 'authentication_analysis')")
    phase["title"] = get_user_input("Phase title (human-readable)", phase["name"].replace("_", " ").title())
    phase["description"] = get_user_input("What does this phase do?")
    
    # Searches in this phase
    safe_print(f"\n🔍 Searches in '{phase['title']}' phase:")
    phase["searches"] = []
    
    while True:
        search = create_search_definition()
        phase["searches"].append(search)
        
        if input(f"\nAdd another search to '{phase['title']}' phase? (y/N): ").lower() != 'y':
            break
    
    return phase


def generate_template_interactively() -> Dict[str, Any]:
    """Generate a template through interactive prompts."""
    safe_print("🎯 FlowPilot Template Generator")
    safe_print("=" * 60)
    safe_print("This tool will help you create a YAML template for FlowPilot workflows.")
    safe_print("Answer the prompts to build your template step by step.\n")
    
    template = {}
    
    # Basic Information
    safe_print("📋 BASIC INFORMATION")
    safe_print("-" * 30)
    
    template["name"] = get_user_input("Template name (lowercase, underscores)")
    template["title"] = get_user_input("Template title (human-readable)", template["name"].replace("_", " ").title())
    template["description"] = get_user_input("What does this workflow do?")
    
    # Category
    categories = ["security", "performance", "troubleshooting", "analysis", "monitoring", "data_quality"]
    template["category"] = get_choice("Select category:", categories, "analysis")
    
    # Complexity
    complexities = ["beginner", "intermediate", "advanced"]
    template["complexity"] = get_choice("Select complexity level:", complexities, "beginner")
    
    template["version"] = get_user_input("Version", "1.0.0")
    template["author"] = get_user_input("Author", "community")
    
    # Requirements
    safe_print("\n🔧 REQUIREMENTS")
    safe_print("-" * 20)
    
    template["splunk_versions"] = get_list_input("Supported Splunk versions (e.g., '8.0+', '9.0+'):", 1)
    template["required_permissions"] = get_list_input("Required permissions (e.g., 'search', 'rest_api_access'):", 1)
    
    if input("Does this workflow require specific indexes? (y/N): ").lower() == 'y':
        template["required_indexes"] = get_list_input("Required indexes (e.g., '_audit', '_internal'):", 1)
    
    # Business Context
    safe_print("\n💼 BUSINESS CONTEXT")
    safe_print("-" * 25)
    
    template["business_value"] = get_user_input("Why is this workflow valuable?")
    template["use_cases"] = get_list_input("Use cases for this workflow:", 2)
    template["success_metrics"] = get_list_input("How do you measure success?", 1)
    template["target_audience"] = get_list_input("Who should use this workflow?", 1)
    
    # Workflow Structure
    safe_print("\n🔄 WORKFLOW STRUCTURE")
    safe_print("-" * 30)
    
    structure_choice = get_choice(
        "Choose workflow structure:",
        [
            "Simple (single list of searches)",
            "Complex (multiple phases with searches)"
        ],
        "Simple (single list of searches)"
    )
    
    if "Simple" in structure_choice:
        # Simple structure with searches
        safe_print("\n🔍 Creating searches for your workflow...")
        template["searches"] = []
        
        while True:
            search = create_search_definition()
            template["searches"].append(search)
            
            if input("\nAdd another search? (y/N): ").lower() != 'y':
                break
    
    else:
        # Complex structure with phases
        safe_print("\n📋 Creating phases for your workflow...")
        template["phases"] = []
        
        while True:
            phase = create_phase_definition()
            template["phases"].append(phase)
            
            if input("\nAdd another phase? (y/N): ").lower() != 'y':
                break
    
    return template


def format_yaml_template(template: Dict[str, Any]) -> str:
    """Format template as YAML string."""
    import yaml
    
    # Custom YAML formatting for better readability
    yaml_content = f"""# {template['title']}
# Generated by FlowPilot Template Generator

# Basic Information
name: "{template['name']}"
title: "{template['title']}"
description: "{template['description']}"
category: "{template['category']}"
complexity: "{template['complexity']}"
version: "{template['version']}"
author: "{template['author']}"

# Requirements
splunk_versions: {yaml.dump(template['splunk_versions'], default_flow_style=True).strip()}
required_permissions: {yaml.dump(template['required_permissions'], default_flow_style=True).strip()}"""
    
    if "required_indexes" in template:
        yaml_content += f"\nrequired_indexes: {yaml.dump(template['required_indexes'], default_flow_style=True).strip()}"
    
    yaml_content += f"""

# Business Context
business_value: "{template['business_value']}"
use_cases:"""
    
    for use_case in template['use_cases']:
        yaml_content += f'\n  - "{use_case}"'
    
    yaml_content += "\nsuccess_metrics:"
    for metric in template['success_metrics']:
        yaml_content += f'\n  - "{metric}"'
    
    yaml_content += "\ntarget_audience:"
    for audience in template['target_audience']:
        yaml_content += f'\n  - "{audience}"'
    
    # Workflow definition
    if "searches" in template:
        yaml_content += "\n\n# Simple workflow - direct searches"
        yaml_content += "\nsearches:"
        
        for search in template['searches']:
            yaml_content += f"""
  - name: "{search['name']}"
    title: "{search['title']}"
    description: "{search['description']}"
    spl: |
      {search['spl']}
    earliest: "{search['earliest']}"
    latest: "{search['latest']}\""""
            
            if search.get('expected_results'):
                yaml_content += f'\n    expected_results: "{search["expected_results"]}"'
    
    elif "phases" in template:
        yaml_content += "\n\n# Complex workflow - multiple phases"
        yaml_content += "\nphases:"
        
        for phase in template['phases']:
            yaml_content += f"""
  - name: "{phase['name']}"
    title: "{phase['title']}"
    description: "{phase['description']}"
    searches:"""
            
            for search in phase['searches']:
                yaml_content += f"""
      - name: "{search['name']}"
        title: "{search['title']}"
        description: "{search['description']}"
        spl: |
          {search['spl']}
        earliest: "{search['earliest']}"
        latest: "{search['latest']}\""""
                
                if search.get('expected_results'):
                    yaml_content += f'\n        expected_results: "{search["expected_results"]}"'
    
    return yaml_content


def main():
    """Main CLI function for template generation."""
    parser = argparse.ArgumentParser(
        description="Interactive FlowPilot template generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive template creation
  ai-sidekick --create-template
  
  # Create template with specific output file
  ai-sidekick --create-template --output my_workflow.yaml
  
  # Create template from example (copy and modify)
  ai-sidekick --create-template --from-example simple_health_check
        """,
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file for the generated template (default: <template_name>.yaml)"
    )
    
    parser.add_argument(
        "--output-dir",
        help="Output directory for the template (default: current directory)"
    )
    
    parser.add_argument(
        "--from-example",
        help="Start from an existing example template (copy and modify)"
    )
    
    args = parser.parse_args()
    
    if args.from_example:
        # Copy from example functionality
        safe_print(f"🔄 Creating template from example: {args.from_example}")
        
        # Find example template
        import os
        base_path = Path(__file__).parent.parent
        example_path = base_path / "core" / "templates" / f"{args.from_example}.yaml"
        
        if not example_path.exists():
            safe_print(f"❌ Example template not found: {example_path}")
            safe_print("Available examples:")
            templates_dir = base_path / "core" / "templates"
            if templates_dir.exists():
                for template_file in templates_dir.glob("*.yaml"):
                    safe_print(f"  - {template_file.stem}")
            sys.exit(1)
        
        # Copy and modify
        with open(example_path, 'r', encoding='utf-8') as f:
            example_content = f.read()
        
        safe_print(f"📄 Loaded example template: {example_path}")
        safe_print("You can now modify this template:")
        
        # Determine output file and directory
        output_file = args.output or f"my_{args.from_example}.yaml"
        
        if args.output_dir:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / output_file
        else:
            output_path = Path(output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(example_content)
        
        safe_print(f"✅ Template copied to: {output_path}")
        safe_print(f"📝 Edit the file and then validate: uv run ai-sidekick --validate-template {output_path}")
        
    else:
        # Interactive creation
        try:
            template = generate_template_interactively()
            yaml_content = format_yaml_template(template)
            
            # Determine output file and directory
            output_file = args.output or f"{template['name']}.yaml"
            
            if args.output_dir:
                output_dir = Path(args.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / output_file
            else:
                output_path = Path(output_file)
            
            # Write template
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            
            safe_print(f"\n🎉 Template created successfully!")
            safe_print(f"📄 File: {output_path}")
            safe_print(f"📝 Template: {template['title']}")
            safe_print(f"🔍 Searches: {len(template.get('searches', []))} direct" + 
                      (f" + {sum(len(p.get('searches', [])) for p in template.get('phases', []))} in phases" if 'phases' in template else ""))
            
            safe_print(f"\n🔧 Next steps:")
            safe_print(f"1. Validate: uv run ai-sidekick --validate-template {output_path}")
            safe_print(f"2. Test: uv run ai-sidekick --create-flow-agent test_workflow --template-file {output_path}")
            safe_print(f"3. Use: uv run ai-sidekick --create-flow-agent my_workflow --template-file {output_path}")
            
        except KeyboardInterrupt:
            safe_print(f"\n\n❌ Template creation cancelled.")
            sys.exit(1)
        except Exception as e:
            safe_print(f"\n❌ Error creating template: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
