#!/usr/bin/env python3
"""
Main CLI entry point for AI Sidekick for Splunk.
Provides a unified command interface with subcommands.
"""

import argparse
import sys
from pathlib import Path


def get_available_templates() -> list[str]:
    """Get list of available built-in templates."""
    try:
        # Find the base path (same logic as in create_flow_agent.py)
        current_path = Path.cwd()
        for path in [current_path] + list(current_path.parents):
            src_path = path / "src" / "ai_sidekick_for_splunk"
            if src_path.exists():
                templates_dir = src_path / "core" / "templates"
                if templates_dir.exists():
                    template_files = list(templates_dir.glob("*.yaml"))
                    return [f.stem for f in template_files if f.name != "README.md"]
        return []
    except Exception:
        return []


def main():
    """Main CLI function with subcommands."""
    # Get available templates dynamically
    available_templates = get_available_templates()
    
    parser = argparse.ArgumentParser(
        prog="ai-sidekick",
        description="AI Sidekick for Splunk - Multi-agent workflow orchestration system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  ai-sidekick --start                                        # Start the AI Sidekick system
  ai-sidekick --stop                                         # Stop the AI Sidekick system
  ai-sidekick --create-flow-agent dev123                     # Create a generic workflow agent
  
  # Built-in templates (curated, stable)
  ai-sidekick --create-flow-agent health_check --template simple_health_check
  ai-sidekick --create-flow-agent security_audit --template security_audit
  
  # Contributor templates (custom YAML files)
  ai-sidekick --create-flow-agent my_custom --template-file my_workflow.yaml
  ai-sidekick --create-flow-agent data_analysis --template-file /path/to/custom_template.yaml
  
  # Template creation and validation
  ai-sidekick --create-template                              # Interactive template creation
  ai-sidekick --create-template --from-example simple_health_check  # Copy and modify example
  ai-sidekick --create-template --template-dir contrib/flows/my_flow  # Create in specific directory
  ai-sidekick --validate-template my_template.yaml           # Validate YAML template before use
  ai-sidekick --validate-workflow my_workflow.json           # Validate JSON workflow structure

Available built-in templates: {', '.join(available_templates) if available_templates else 'None found'}

For more information, visit: https://github.com/deslicer/ai-sidekick-for-splunk
        """,
    )

    # Create mutually exclusive group for main actions
    action_group = parser.add_mutually_exclusive_group(required=True)

    action_group.add_argument("--start", action="store_true", help="Start the AI Sidekick system")

    action_group.add_argument("--stop", action="store_true", help="Stop the AI Sidekick system")

    action_group.add_argument(
        "--create-flow-agent",
        metavar="NAME",
        help="Create a new FlowPilot workflow agent with the specified name",
    )

    action_group.add_argument(
        "--validate-template",
        metavar="TEMPLATE_FILE",
        help="Validate a YAML template file for FlowPilot compatibility",
    )

    action_group.add_argument(
        "--validate-workflow",
        metavar="WORKFLOW_FILE",
        help="Validate a workflow JSON file for structure and format compliance",
    )

    action_group.add_argument(
        "--create-template",
        action="store_true",
        help="Create a new YAML template interactively",
    )

    # Optional arguments for create-flow-agent
    parser.add_argument(
        "--output-dir", help="Output directory for created workflow (default: contrib/flows/NAME)"
    )

    parser.add_argument(
        "--template",
        choices=available_templates if available_templates else None,
        help=f"Use a built-in template with working SPL searches. Available: {', '.join(available_templates) if available_templates else 'None found'}",
    )

    parser.add_argument(
        "--template-file",
        help="Path to a custom YAML template file for contributor workflows",
    )

    # Optional arguments for create-template
    parser.add_argument(
        "--output", "-o",
        help="Output file for generated template (used with --create-template)"
    )
    
    parser.add_argument(
        "--from-example",
        help="Start from an existing example template (used with --create-template)"
    )
    
    parser.add_argument(
        "--template-dir",
        help="Output directory for template creation (used with --create-template)"
    )

    # Optional arguments for validate-workflow
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed validation information (used with --validate-workflow)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show final result (used with --validate-workflow)"
    )

    args = parser.parse_args()

    try:
        if args.start:
            from ai_sidekick_for_splunk.cli.start_lab import main as start_main

            start_main()

        elif args.stop:
            from ai_sidekick_for_splunk.cli.stop_lab import main as stop_main

            stop_main()

        elif args.validate_template:
            # Import and call template validator
            from ai_sidekick_for_splunk.cli.validate_template import main as validate_main

            # Modify sys.argv to pass the template file to the validator
            original_argv = sys.argv.copy()
            sys.argv = ["validate_template", args.validate_template]

            try:
                validate_main()
            finally:
                # Restore original argv
                sys.argv = original_argv

        elif args.validate_workflow:
            # Import and call workflow validator
            from ai_sidekick_for_splunk.cli.validate_workflow import main as validate_workflow_main

            # Modify sys.argv to pass the workflow file and options to the validator
            original_argv = sys.argv.copy()
            new_argv = ["validate_workflow", args.validate_workflow]
            
            # Pass through relevant arguments
            if hasattr(args, 'verbose') and args.verbose:
                new_argv.append("--verbose")
            if hasattr(args, 'quiet') and args.quiet:
                new_argv.append("--quiet")
            
            sys.argv = new_argv

            try:
                validate_workflow_main()
            finally:
                # Restore original argv
                sys.argv = original_argv

        elif args.create_template:
            # Import and call template creator
            from ai_sidekick_for_splunk.cli.create_template import main as create_template_main

            # Modify sys.argv to pass any additional arguments
            original_argv = sys.argv.copy()
            new_argv = ["create_template"]
            
            # Pass through relevant arguments
            if hasattr(args, 'output') and args.output:
                new_argv.extend(["--output", args.output])
            if hasattr(args, 'from_example') and args.from_example:
                new_argv.extend(["--from-example", args.from_example])
            if hasattr(args, 'template_dir') and args.template_dir:
                new_argv.extend(["--output-dir", args.template_dir])
            
            sys.argv = new_argv

            try:
                create_template_main()
            finally:
                # Restore original argv
                sys.argv = original_argv

        elif args.create_flow_agent:
            # Import and call create_flow_agent with the name
            from ai_sidekick_for_splunk.cli.create_flow_agent import main as create_main

            # Modify sys.argv to pass the name to the create_flow_agent script
            original_argv = sys.argv.copy()
            sys.argv = ["create_flow_agent", args.create_flow_agent]

            # Add output-dir if specified
            if args.output_dir:
                sys.argv.extend(["--output-dir", args.output_dir])

            # Add template if specified
            if args.template:
                sys.argv.extend(["--template", args.template])

            # Add template-file if specified
            if args.template_file:
                sys.argv.extend(["--template-file", args.template_file])

            try:
                create_main()
            finally:
                # Restore original argv
                sys.argv = original_argv

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
