#!/usr/bin/env python3
"""
Workflow JSON Validation Tool.

This tool validates FlowPilot workflow JSON files to ensure they conform to the
expected schema and structure. It's designed for advanced users who create
workflow JSON files directly and want to validate them before deployment.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

def safe_print(message: str, file=None) -> None:
    """Safely print message, handling encoding issues."""
    try:
        print(message, file=file)
    except UnicodeEncodeError:
        # Fallback for systems with encoding issues
        print(message.encode('ascii', 'replace').decode('ascii'), file=file)


def validate_workflow_json(workflow_path: str, verbose: bool = False) -> tuple[bool, str]:
    """
    Validate a workflow JSON file.
    
    Args:
        workflow_path: Path to the workflow JSON file
        verbose: Whether to show detailed validation information
        
    Returns:
        Tuple of (is_valid, message)
    """
    try:
        # Import validation functions
        from ai_sidekick_for_splunk.core.flows_engine.workflow_models import (
            validate_workflow_file,
            WorkflowValidationError
        )
        from ai_sidekick_for_splunk.core.flows_engine.agent_flow import AgentFlow
        
        workflow_file = Path(workflow_path)
        
        # Check if file exists
        if not workflow_file.exists():
            return False, f"❌ File not found: {workflow_path}"
        
        # Check if it's a JSON file
        if workflow_file.suffix.lower() != '.json':
            return False, f"❌ File must have .json extension: {workflow_path}"
        
        safe_print(f"🔍 Validating workflow: {workflow_file.name}")
        
        # Test JSON parsing
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
        except json.JSONDecodeError as e:
            return False, f"❌ Invalid JSON format: {e}"
        
        # Validate using Pydantic model
        try:
            validated_template = validate_workflow_file(str(workflow_file))
            if verbose:
                safe_print(f"✅ Pydantic validation passed")
                safe_print(f"   Workflow ID: {validated_template.workflow_id}")
                safe_print(f"   Name: {validated_template.workflow_name}")
                safe_print(f"   Version: {validated_template.version}")
                safe_print(f"   Author: {getattr(validated_template, 'author', 'Unknown')}")
                safe_print(f"   Phases: {len(validated_template.core_phases)}")
        except WorkflowValidationError as e:
            return False, f"❌ Workflow validation failed:\n{e}"
        except Exception as e:
            return False, f"❌ Validation error: {e}"
        
        # Test AgentFlow loading
        try:
            agent_flow = AgentFlow.load_from_json(str(workflow_file))
            if verbose:
                safe_print(f"✅ AgentFlow loading successful")
                safe_print(f"   Workflow name: {agent_flow.workflow_name}")
                
                # Get phases safely
                phases = getattr(agent_flow, 'phases', {})
                safe_print(f"   Total phases: {len(phases)}")
                
                # Count tasks across all phases
                total_tasks = 0
                if phases:
                    for phase in phases.values():
                        tasks = getattr(phase, 'tasks', {})
                        total_tasks += len(tasks)
                safe_print(f"   Total tasks: {total_tasks}")
                
        except Exception as e:
            return False, f"❌ AgentFlow loading failed: {e}"
        
        # Additional checks
        if verbose:
            safe_print(f"✅ Additional checks:")
            
            # Check for required fields
            required_fields = ['workflow_id', 'workflow_name', 'version', 'core_phases']
            missing_fields = [field for field in required_fields if field not in workflow_data]
            if missing_fields:
                return False, f"❌ Missing required fields: {missing_fields}"
            
            safe_print(f"   Required fields: ✅ All present")
            
            # Check phase structure
            phases = workflow_data.get('core_phases', {})
            if not phases:
                return False, f"❌ No phases defined in workflow"
            
            safe_print(f"   Phase structure: ✅ Valid")
            
            # Check for tasks in phases
            total_tasks = 0
            for phase_name, phase_data in phases.items():
                tasks = phase_data.get('tasks', {})
                total_tasks += len(tasks)
                if not tasks:
                    safe_print(f"   ⚠️  Phase '{phase_name}' has no tasks")
            
            if total_tasks == 0:
                return False, f"❌ No tasks defined in any phase"
            
            safe_print(f"   Task validation: ✅ {total_tasks} tasks found")
        
        return True, f"✅ Workflow validation successful: {workflow_file.name}"
        
    except ImportError as e:
        return False, f"❌ Import error: {e}. Make sure you're running from the correct environment."
    except Exception as e:
        return False, f"❌ Unexpected error: {e}"


def main():
    """Main CLI function for workflow validation."""
    parser = argparse.ArgumentParser(
        prog="validate-workflow",
        description="Validate FlowPilot workflow JSON files for structure and format compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-sidekick --validate-workflow my_workflow.json
  ai-sidekick --validate-workflow path/to/workflow.json --verbose
  ai-sidekick --validate-workflow contrib/flows/my_flow/my_flow.json -v

This tool validates:
- JSON syntax and structure
- Pydantic schema compliance
- AgentFlow loading compatibility
- Required fields presence
- Phase and task structure
- Workflow metadata consistency

Perfect for advanced users who create workflow JSON files directly
and want to ensure they'll work seamlessly with FlowPilot agents.
        """,
    )

    parser.add_argument(
        "workflow_file",
        help="Path to the workflow JSON file to validate"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed validation information and checks"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true", 
        help="Only show final result (success/failure)"
    )

    args = parser.parse_args()

    try:
        # Validate the workflow
        is_valid, message = validate_workflow_json(args.workflow_file, args.verbose)
        
        if not args.quiet:
            safe_print(message)
        
        if is_valid:
            if args.quiet:
                safe_print("✅ VALID")
            else:
                safe_print("")
                safe_print("🎉 Workflow is ready for use!")
                safe_print("   You can now create a FlowPilot agent with this workflow.")
            sys.exit(0)
        else:
            if args.quiet:
                safe_print("❌ INVALID")
            else:
                safe_print("")
                safe_print("💡 Tips for fixing validation errors:")
                safe_print("   - Check the workflow JSON schema documentation")
                safe_print("   - Ensure all required fields are present")
                safe_print("   - Verify phase and task structure")
                safe_print("   - Use --verbose for detailed error information")
            sys.exit(1)
            
    except KeyboardInterrupt:
        safe_print("\n⚠️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        safe_print(f"❌ Validation failed with error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
