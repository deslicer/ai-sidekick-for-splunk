#!/usr/bin/env python3
"""
Template Validation Tool for AI Sidekick FlowPilot Templates.

This tool helps contributors validate their YAML templates before publishing
to ensure they create valid, working FlowPilot agents.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

from ai_sidekick_for_splunk.core.utils.cross_platform import safe_print

# Import template system
try:
    from ai_sidekick_for_splunk.cli.templates import (
        load_template,
        generate_workflow_from_template,
        TemplateParseError,
    )
    from ai_sidekick_for_splunk.core.flows_engine.workflow_models import validate_workflow_template
    from ai_sidekick_for_splunk.core.flows_engine.workflow_discovery import WorkflowDiscovery
    VALIDATION_AVAILABLE = True
except ImportError as e:
    safe_print(f"❌ Validation system not available: {e}", file=sys.stderr)
    VALIDATION_AVAILABLE = False


class TemplateValidator:
    """Comprehensive template validation system."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
    
    def validate_template_file(self, template_path: Path) -> Dict[str, Any]:
        """
        Comprehensive validation of a YAML template file.
        
        Returns:
            Validation result with status, errors, warnings, and generated content
        """
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "info": [],
            "template_data": None,
            "generated_json": None,
            "validation_steps": []
        }
        
        if not VALIDATION_AVAILABLE:
            result["errors"].append("Validation system not available")
            return result
        
        # Step 1: File existence and readability
        try:
            if not template_path.exists():
                result["errors"].append(f"Template file not found: {template_path}")
                return result
            
            if not template_path.is_file():
                result["errors"].append(f"Path is not a file: {template_path}")
                return result
            
            result["validation_steps"].append("✅ File exists and is readable")
        except Exception as e:
            result["errors"].append(f"File access error: {e}")
            return result
        
        # Step 2: YAML parsing and template structure validation
        try:
            template = load_template(template_path)
            result["template_data"] = template.model_dump()
            result["validation_steps"].append("✅ YAML parsing successful")
            result["validation_steps"].append("✅ Template structure validation passed")
        except TemplateParseError as e:
            result["errors"].append(f"Template parsing failed: {e}")
            return result
        except Exception as e:
            result["errors"].append(f"Unexpected template parsing error: {e}")
            return result
        
        # Step 3: JSON generation
        try:
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_output = Path(temp_dir)
                workflow_json, readme_content = generate_workflow_from_template(
                    template, temp_output, "validation_test"
                )
                result["generated_json"] = workflow_json
                result["validation_steps"].append("✅ JSON generation successful")
        except Exception as e:
            result["errors"].append(f"JSON generation failed: {e}")
            return result
        
        # Step 4: FlowPilot JSON validation
        try:
            validate_workflow_template(workflow_json, str(template_path))
            result["validation_steps"].append("✅ FlowPilot JSON validation passed")
        except Exception as e:
            result["errors"].append(f"FlowPilot JSON validation failed: {e}")
            return result
        
        # Step 5: SPL syntax validation (basic)
        try:
            self._validate_spl_syntax(template)
            result["validation_steps"].append("✅ Basic SPL syntax validation passed")
        except Exception as e:
            result["warnings"].append(f"SPL syntax validation warning: {e}")
        
        # Step 6: Template best practices check
        try:
            self._check_best_practices(template, result)
            result["validation_steps"].append("✅ Best practices check completed")
        except Exception as e:
            result["warnings"].append(f"Best practices check warning: {e}")
        
        # If we got here, validation passed
        result["valid"] = True
        result["errors"] = []  # Clear any accumulated errors if we succeeded
        
        return result
    
    def _validate_spl_syntax(self, template) -> None:
        """Basic SPL syntax validation."""
        if hasattr(template, 'searches') and template.searches:
            for search in template.searches:
                spl = search.spl.strip()
                
                # Basic syntax checks
                if not spl:
                    raise ValueError(f"Empty SPL in search '{search.name}'")
                
                # Check for common SPL patterns
                if not (spl.startswith('search ') or spl.startswith('|') or 
                       spl.startswith('index=') or spl.startswith('sourcetype=')):
                    self.warnings.append(f"Search '{search.name}' may not be valid SPL: {spl[:50]}...")
        
        # Check phases if they exist
        if hasattr(template, 'phases') and template.phases:
            for phase in template.phases:
                if hasattr(phase, 'searches') and phase.searches:
                    for search in phase.searches:
                        spl = search.spl.strip()
                        if not spl:
                            raise ValueError(f"Empty SPL in phase '{phase.name}', search '{search.name}'")
    
    def _check_best_practices(self, template, result: Dict[str, Any]) -> None:
        """Check template against best practices."""
        
        # Check metadata completeness
        if not template.metadata.description or len(template.metadata.description) < 20:
            result["warnings"].append("Description should be at least 20 characters for clarity")
        
        if not template.business_context.business_value or len(template.business_context.business_value) < 30:
            result["warnings"].append("Business value should be detailed (at least 30 characters)")
        
        if not template.business_context.use_cases or len(template.business_context.use_cases) < 2:
            result["warnings"].append("Consider adding more use cases (at least 2)")
        
        # Check search quality
        search_count = 0
        if hasattr(template, 'searches') and template.searches:
            search_count += len(template.searches)
        
        if hasattr(template, 'phases') and template.phases:
            for phase in template.phases:
                if hasattr(phase, 'searches') and phase.searches:
                    search_count += len(phase.searches)
        
        if search_count == 0:
            result["warnings"].append("Template has no searches defined")
        elif search_count == 1:
            result["warnings"].append("Consider adding more searches for comprehensive analysis")
        
        # Check time ranges
        if hasattr(template, 'searches') and template.searches:
            for search in template.searches:
                if search.earliest == "-24h@h" and search.latest == "now":
                    result["info"].append(f"Search '{search.name}' uses default 24h time range")


def main():
    """Main CLI function for template validation."""
    parser = argparse.ArgumentParser(
        description="Validate FlowPilot YAML templates for contributors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a single template
  uv run python -m ai_sidekick_for_splunk.cli.validate_template my_template.yaml
  
  # Validate with detailed output
  uv run python -m ai_sidekick_for_splunk.cli.validate_template my_template.yaml --verbose
  
  # Validate and show generated JSON
  uv run python -m ai_sidekick_for_splunk.cli.validate_template my_template.yaml --show-json
        """,
    )
    
    parser.add_argument(
        "template_file",
        help="Path to the YAML template file to validate"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed validation information"
    )
    
    parser.add_argument(
        "--show-json",
        action="store_true", 
        help="Show the generated FlowPilot JSON"
    )
    
    parser.add_argument(
        "--output-json",
        help="Save generated JSON to file"
    )
    
    args = parser.parse_args()
    
    if not VALIDATION_AVAILABLE:
        safe_print("❌ Template validation system not available", file=sys.stderr)
        safe_print("Make sure you're running from the correct environment with all dependencies installed.", file=sys.stderr)
        sys.exit(1)
    
    template_path = Path(args.template_file)
    
    safe_print(f"🔍 Validating template: {template_path}")
    safe_print("=" * 60)
    
    validator = TemplateValidator()
    result = validator.validate_template_file(template_path)
    
    # Show validation steps
    if args.verbose:
        safe_print("\n📋 Validation Steps:")
        for step in result["validation_steps"]:
            safe_print(f"  {step}")
    
    # Show results
    if result["valid"]:
        safe_print("\n✅ Template Validation PASSED!")
        safe_print(f"📄 Template: {result['template_data']['metadata']['title']}")
        safe_print(f"📝 Description: {result['template_data']['metadata']['description']}")
        safe_print(f"🏷️  Category: {result['template_data']['metadata']['category']}")
        safe_print(f"⚡ Complexity: {result['template_data']['metadata']['complexity']}")
        
        # Count searches
        search_count = 0
        if 'searches' in result['template_data'] and result['template_data']['searches']:
            search_count += len(result['template_data']['searches'])
        if 'phases' in result['template_data'] and result['template_data']['phases']:
            for phase in result['template_data']['phases']:
                if 'searches' in phase and phase['searches']:
                    search_count += len(phase['searches'])
        
        safe_print(f"🔍 Total searches: {search_count}")
        
    else:
        safe_print("\n❌ Template Validation FAILED!")
        for error in result["errors"]:
            safe_print(f"  ❌ {error}")
    
    # Show warnings
    if result["warnings"]:
        safe_print(f"\n⚠️  Warnings ({len(result['warnings'])}):")
        for warning in result["warnings"]:
            safe_print(f"  ⚠️  {warning}")
    
    # Show info
    if result["info"] and args.verbose:
        safe_print(f"\nℹ️  Information:")
        for info in result["info"]:
            safe_print(f"  ℹ️  {info}")
    
    # Show generated JSON if requested
    if args.show_json and result["generated_json"]:
        safe_print("\n📄 Generated FlowPilot JSON:")
        safe_print(json.dumps(result["generated_json"], indent=2))
    
    # Save JSON if requested
    if args.output_json and result["generated_json"]:
        output_path = Path(args.output_json)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result["generated_json"], f, indent=2, ensure_ascii=False)
        safe_print(f"\n💾 Generated JSON saved to: {output_path}")
    
    # Exit with appropriate code
    if result["valid"]:
        safe_print(f"\n🎉 Template is ready for use!")
        safe_print("You can now create a FlowPilot agent with:")
        safe_print(f"  ai-sidekick --create-flow-agent my_agent --template-file {template_path}")
        sys.exit(0)
    else:
        safe_print(f"\n🔧 Please fix the errors above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()

