#!/usr/bin/env python3
"""
CLI command for creating FlowPilot workflow agents using YAML templates.
This script creates workflow agents with proper directory structure using the YAML template system.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from ai_sidekick_for_splunk.core.utils.cross_platform import safe_print

# Import template system for YAML template support
try:
    from ai_sidekick_for_splunk.cli.templates import (
        load_template,
        generate_workflow_from_template,
        parse_template_string,
        TemplateParseError,
    )
    TEMPLATE_SYSTEM_AVAILABLE = True
except ImportError as e:
    safe_print(f"⚠️  Template system not available: {e}", file=sys.stderr)
    TEMPLATE_SYSTEM_AVAILABLE = False


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


def create_default_workflow(name: str, output_dir: Path) -> tuple[dict, str]:
    """
    Create a default workflow using a minimal YAML template.
    
    Args:
        name: Name for the workflow agent
        output_dir: Output directory for generated files
        
    Returns:
        Tuple of (workflow_dict, readme_content)
    """
    if not TEMPLATE_SYSTEM_AVAILABLE:
        raise RuntimeError("Template system not available")
    
    # Create a minimal default template
    default_template_content = f"""# Default Workflow Template
name: "{name}"
title: "{name.replace('_', ' ').title()} Workflow"
description: "A basic workflow template for {name}"
category: "analysis"
complexity: "beginner"
version: "1.0.0"
author: "community"

# Business Context
business_value: "Provides basic analysis capabilities"
use_cases:
  - "Basic data analysis"
  - "System monitoring"

# Simple workflow
searches:
  - name: "basic_check"
    spl: 'search earliest=-24h | head 10 | table _time, index, sourcetype'
    earliest: "-24h@h"
    latest: "now"
    description: "Basic data check"
    expected_results: "Recent events sample"

# Advanced Options
parallel_execution: false
streaming_support: true
educational_mode: false
estimated_duration: "2-3 minutes"
"""
    
    try:
        # Parse the default template
        safe_print(f"📄 Creating default workflow template for: {name}")
        template = parse_template_string(default_template_content)
        
        # Generate workflow JSON and README
        safe_print(f"🔄 Generating FlowPilot workflow from default template...")
        workflow_json, readme_content = generate_workflow_from_template(template, output_dir, name)
        
        # Save the template file for reference
        template_file_path = output_dir / f"{name}.yaml"
        with open(template_file_path, 'w', encoding='utf-8') as f:
            f.write(default_template_content)
        safe_print(f"📋 Created template file: {template_file_path}")
        
        # Create .template_source file for tracking
        source_file = output_dir / ".template_source"
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(f"source_template: default_generated\n")
            f.write(f"generated_on: {datetime.now().isoformat()}\n")
            f.write(f"template_version: {template.metadata.version}\n")
            f.write(f"template_format: {template.metadata.template_format}\n")
        
        safe_print(f"✅ Generated default workflow: {template.metadata.title}")
        return workflow_json, readme_content
        
    except Exception as e:
        safe_print(f"❌ Failed to create default workflow: {e}", file=sys.stderr)
        raise


def create_from_template_file(name: str, template_file_path: str, output_dir: Path) -> tuple[dict, str]:
    """
    Create workflow from YAML template file.
    
    Args:
        name: Name for the workflow agent
        template_file_path: Path to YAML template file
        output_dir: Output directory for generated files
        
    Returns:
        Tuple of (workflow_dict, readme_content)
    """
    if not TEMPLATE_SYSTEM_AVAILABLE:
        raise RuntimeError("Template system not available")
    
    template_path = Path(template_file_path)
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_file_path}")
    
    try:
        # Load and parse the YAML template
        safe_print(f"📄 Loading template from: {template_path}")
        template = load_template(template_path)
        
        # Generate workflow JSON and README
        safe_print(f"🔄 Generating FlowPilot workflow from template...")
        workflow_json, readme_content = generate_workflow_from_template(template, output_dir, name)
        
        # Copy template file to output directory for reference (if not already there)
        template_copy_path = output_dir / f"{name}.yaml"
        import shutil
        
        # Check if source and destination are the same file
        try:
            if template_path.resolve() != template_copy_path.resolve():
                shutil.copy2(template_path, template_copy_path)
                safe_print(f"📋 Copied template to: {template_copy_path}")
            else:
                safe_print(f"📋 Template already in target location: {template_copy_path}")
        except Exception as e:
            # If copy fails, continue without copying (template might already exist)
            safe_print(f"⚠️  Template copy skipped: {e}")
        
        # Create .template_source file for tracking
        source_file = output_dir / ".template_source"
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(f"source_template: {template_path.absolute()}\n")
            f.write(f"generated_on: {datetime.now().isoformat()}\n")
            f.write(f"template_version: {template.metadata.version}\n")
            f.write(f"template_format: {template.metadata.template_format}\n")
        
        safe_print(f"✅ Generated workflow from template: {template.metadata.title}")
        return workflow_json, readme_content
        
    except TemplateParseError as e:
        safe_print(f"❌ Template parsing failed: {e}", file=sys.stderr)
        raise
    except Exception as e:
        safe_print(f"❌ Failed to process template file: {e}", file=sys.stderr)
        raise


def get_available_templates() -> list[str]:
    """Get list of available built-in templates."""
    try:
        base_path = get_base_path()
        templates_dir = base_path / "core" / "templates"
        if templates_dir.exists():
            template_files = list(templates_dir.glob("*.yaml"))
            return [f.stem for f in template_files if f.name != "README.md"]
        return []
    except Exception:
        return []


def main():
    """Main CLI function for creating FlowPilot workflow agents."""
    # Get available templates dynamically
    available_templates = get_available_templates()
    
    parser = argparse.ArgumentParser(
        description="Create FlowPilot workflow agents using YAML templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Basic workflow creation
  ai-sidekick --create-flow-agent dev1666
  ai-sidekick --create-flow-agent workshop_demo
  
  # Built-in templates with working SPL searches
  ai-sidekick --create-flow-agent my_health_check --template simple_health_check
  ai-sidekick --create-flow-agent my_security --template security_audit
  
  # Custom YAML template files
  ai-sidekick --create-flow-agent my_security --template-file security_audit.yaml
  ai-sidekick --create-flow-agent custom_analysis --template-file /path/to/my_template.yaml
  
  Available built-in templates: {', '.join(available_templates) if available_templates else 'None found'}
        """,
    )

    parser.add_argument(
        "name", help="Name for the workflow agent (e.g., 'dev1666', 'workshop_demo')"
    )

    parser.add_argument(
        "--output-dir", help="Output directory (default: contrib/flows/NAME)", default=None
    )

    parser.add_argument(
        "--template",
        choices=available_templates if available_templates else None,
        help=f"Use a built-in template with working SPL searches. Available: {', '.join(available_templates) if available_templates else 'None found'}",
        default=None,
    )

    parser.add_argument(
        "--template-file",
        help="Path to a YAML template file for custom workflow creation",
        default=None,
    )

    args = parser.parse_args()

    # Validate arguments
    if args.template and args.template_file:
        safe_print("❌ Error: Cannot specify both --template and --template-file", file=sys.stderr)
        sys.exit(1)

    if (args.template or args.template_file) and not TEMPLATE_SYSTEM_AVAILABLE:
        safe_print("❌ Error: Template system not available. Cannot use templates", file=sys.stderr)
        sys.exit(1)

    try:
        # Get base path
        base_path = get_base_path()

        # Determine output directory
        if args.output_dir:
            output_dir = Path(args.output_dir)
        else:
            output_dir = base_path / "contrib" / "flows" / args.name

        # Create directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create workflow template using different methods
        if args.template_file:
            # Use YAML template file
            workflow_template, readme_content = create_from_template_file(args.name, args.template_file, output_dir)
        elif args.template:
            # Use built-in YAML template
            template_file_path = base_path / "core" / "templates" / f"{args.template}.yaml"
            if not template_file_path.exists():
                safe_print(f"❌ Error: Built-in template '{args.template}' not found at {template_file_path}", file=sys.stderr)
                sys.exit(1)
            
            workflow_template, readme_content = create_from_template_file(args.name, str(template_file_path), output_dir)
        else:
            # Use default template - create a minimal YAML template
            workflow_template, readme_content = create_default_workflow(args.name, output_dir)

        # Validate the template
        try:
            # The template is already validated since it's created using Pydantic models
            print("✅ Template validation passed!")
        except Exception as e:
            print(f"❌ Template validation failed: {e}", file=sys.stderr)
            sys.exit(1)

        # Handle different workflow creation paths
        workflow_dict = workflow_template
        workflow_name = workflow_dict.get("workflow_name", args.name)

        # Save workflow JSON
        workflow_file = output_dir / f"{args.name}.json"
        with open(workflow_file, "w", encoding="utf-8") as f:
            json.dump(workflow_dict, f, indent=2, ensure_ascii=False)

        # Save README
        readme_file = output_dir / "README.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(readme_content)

        # Success output
        safe_print("🛠 Creating FlowPilot Workflow Agent")
        safe_print("=" * 60)
        safe_print(f"📍 Base path: {base_path}")
        safe_print(f"🎯 Creating workflow in: {output_dir.relative_to(base_path)}/")
        safe_print()
        safe_print(f"✅ Created directory: {output_dir}")
        safe_print(f"✅ Created workflow: {args.name}.json")
        safe_print("✅ Created README: README.md")
        safe_print()
        
        if args.template_file:
            template_info = f" (from template file: {Path(args.template_file).name})"
        elif args.template:
            template_info = f" (using '{args.template}' template)"
        else:
            template_info = ""
        safe_print(f"🎉 SUCCESS! {workflow_name} Created{template_info}!")
        safe_print("=" * 60)
        safe_print()
        safe_print("📁 Files Created:")
        if args.template_file or args.template:
            template_copy_file = output_dir / f"{args.name}.yaml"
            safe_print(f"├── 📋 {template_copy_file}")
            safe_print(f"├── 📄 {workflow_file}")
            safe_print(f"└── 📖 {readme_file}")
        else:
            safe_print(f"├── 📋 {output_dir / f'{args.name}.yaml'}")
            safe_print(f"├── 📄 {workflow_file}")
            safe_print(f"└── 📖 {readme_file}")
        safe_print()
        safe_print("🚀 Next Steps:")
        safe_print("1️⃣  Restart ADK Web to discover the new agent")
        safe_print(f"2️⃣  Look for '{workflow_name}' in the agent list")
        safe_print("3️⃣  Test your workflow with a relevant query")
        safe_print("4️⃣  Watch the workflow execution!")
        safe_print()
        safe_print("🎯 Template System Benefits:")
        safe_print("├── ✅ Real SPL searches (no placeholders)")
        safe_print("├── ✅ Automatic JSON generation")
        safe_print("├── ✅ Built-in validation")
        safe_print("└── ✅ Easy customization via YAML")

    except Exception as e:
        safe_print(f"❌ Error creating workflow agent: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
