#!/usr/bin/env python3
"""
CLI command for creating FlowPilot workflow agents.
This script creates workshop-ready workflow agents with proper directory structure.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

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

def create_workflow_template(name: str, output_dir: Path) -> Dict[str, Any]:
    """Create a basic workflow template for workshop demonstrations."""
    return {
        "workflow_id": f"contrib.{name}",
        "workflow_name": f"Dev{name.title()} System Health Agent",
        "workflow_type": "troubleshooting",
        "workflow_category": "system_health",
        "source": "contrib",
        "maintainer": "community",
        "stability": "experimental",
        "complexity_level": "beginner",
        "estimated_duration": "2-3 minutes",
        "version": "1.0.0",
        "splunk_versions": ["8.0+", "9.0+"],
        "last_updated": "2025-08-30",
        "documentation_url": "./README.md",
        "description": f"A simple workshop demonstration agent that performs basic Splunk environment health checks and gathers system information. Perfect for learning the FlowPilot workflow system.",
        "business_value": "Provides quick health assessment of Splunk environment for workshop participants to understand system status and learn workflow execution patterns.",
        "use_cases": [
            "Workshop demonstrations",
            "Learning FlowPilot system",
            "Basic health monitoring",
            "Educational purposes"
        ],
        "prerequisites": {
            "splunk_access": True,
            "mcp_server": True,
            "permissions": ["search", "rest_api"]
        },
        "workflow_instructions": {
            "persona": f"You are the Dev{name.title()} System Health Agent - a friendly workshop demonstration agent that helps participants learn about Splunk health monitoring.",
            "approach": "Execute each phase step by step, providing clear explanations of what you're checking and why it matters for system health.",
            "tone": "Educational and encouraging - this is for learning purposes!"
        },
        "agent_dependencies": {
            "splunk_mcp": {
                "agent_id": "splunk_mcp",
                "required": True,
                "description": "Splunk MCP server for executing searches and gathering system information",
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
            "system_info": {
                "name": "system_info",
                "phase_name": "System Information Gathering",
                "description": "Collect basic Splunk system information and configuration details",
                "tasks": [
                    {
                        "task_id": "gather_splunk_version",
                        "title": "Gather Splunk Version",
                        "tool": "splunk_mcp",
                        "goal": "Get Splunk version and basic system information",
                        "prompt": "Please retrieve the Splunk version information and basic system details. This helps us understand what Splunk environment we're working with.",
                        "expected_output": "Splunk version, build information, and system configuration summary"
                    },
                    {
                        "task_id": "list_available_indexes",
                        "title": "List Available Indexes", 
                        "tool": "splunk_mcp",
                        "goal": "List all available indexes to understand data landscape",
                        "prompt": "List all available Splunk indexes. This gives us an overview of what data sources are configured in this environment.",
                        "expected_output": "Complete list of indexes with basic metadata"
                    }
                ]
            },
            "health_checks": {
                "name": "health_checks",
                "phase_name": "Basic Health Assessment",
                "description": "Perform fundamental health checks on the Splunk environment",
                "tasks": [
                    {
                        "task_id": "check_recent_data",
                        "title": "Check Recent Data",
                        "tool": "splunk_mcp",
                        "goal": "Verify that recent data is being indexed",
                        "prompt": "Search for events from the last 24 hours across all indexes to verify data is flowing. Use a simple search like: search earliest=-24h | head 10 | stats count. This confirms the system is actively receiving and indexing data.",
                        "expected_output": "Count of recent events and confirmation of data flow"
                    },
                    {
                        "task_id": "check_system_performance",
                        "title": "Check System Performance",
                        "tool": "splunk_mcp", 
                        "goal": "Basic performance indicators check",
                        "prompt": "Check basic system performance by running a simple search to measure response time. Search for: | rest /services/server/info | eval response_time=now() | table response_time. This gives us a baseline performance indicator.",
                        "expected_output": "Basic performance metrics and response time information"
                    }
                ]
            },
            "summary_report": {
                "name": "summary_report",
                "phase_name": "Health Summary Report",
                "description": "Compile findings into a clear, actionable summary",
                "tasks": [
                    {
                        "task_id": "generate_health_summary",
                        "title": "Generate Health Summary",
                        "tool": "result_synthesizer",
                        "goal": "Create a comprehensive but beginner-friendly health report",
                        "prompt": "Based on the system information and health checks performed, create a clear and friendly summary report. Include: 1) System overview (version, indexes), 2) Health status (data flow, performance), 3) Any recommendations for workshop participants. Keep it educational and encouraging - this is for learning purposes!",
                        "expected_output": "Comprehensive health report with educational insights for workshop participants"
                    }
                ]
            }
        }
    }

def create_readme(name: str, workflow_name: str) -> str:
    """Create a README for the workflow."""
    return f"""# {workflow_name}

## Overview

This is a workshop demonstration agent designed to help participants learn about the FlowPilot workflow system while performing basic Splunk environment health checks.

## Purpose

- **Educational**: Perfect for learning how FlowPilot workflows operate
- **Interactive**: Demonstrates multi-phase workflow execution
- **Practical**: Performs real health checks on Splunk environment

## What It Does

### Phase 1: System Information Gathering
- Retrieves Splunk version and build information
- Lists all available indexes in the environment
- Provides overview of the data landscape

### Phase 2: Basic Health Assessment  
- Checks for recent data flow (last 24 hours)
- Measures basic system performance indicators
- Verifies system is actively indexing data

### Phase 3: Health Summary Report
- Compiles findings into a comprehensive report
- Provides educational insights for workshop participants
- Offers recommendations and next steps

## Usage

1. **Start AI Sidekick**: Ensure the AI Sidekick is running
2. **Find the Agent**: Look for '{workflow_name}' in the agent list
3. **Query**: Ask "Please perform a health check on this Splunk environment"
4. **Watch**: Observe the multi-phase workflow execution

## Learning Outcomes

- Understanding of FlowPilot workflow orchestration
- Real Splunk environment interaction patterns
- Multi-agent coordination and result synthesis
- Educational health monitoring techniques

## Workshop Integration

This agent is specifically designed for workshop demonstrations and provides:
- Clear explanations of each step
- Educational context for health checks
- Beginner-friendly output and recommendations
- Interactive learning experience

Perfect for demonstrating the power and flexibility of the FlowPilot system!
"""

def main():
    """Main CLI function for creating FlowPilot workflow agents."""
    parser = argparse.ArgumentParser(
        description="Create FlowPilot workflow agents for workshop demonstrations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-sidekick-create-flow-agent dev1666
  ai-sidekick-create-flow-agent workshop_demo
  ai-sidekick-create-flow-agent health_monitor
        """
    )
    
    parser.add_argument(
        "name",
        help="Name for the workflow agent (e.g., 'dev1666', 'workshop_demo')"
    )
    
    parser.add_argument(
        "--output-dir",
        help="Output directory (default: contrib/flows/NAME)",
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
            output_dir = base_path / "contrib" / "flows" / args.name
        
        # Create directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create workflow template
        workflow_template = create_workflow_template(args.name, output_dir)
        workflow_file = output_dir / f"{args.name}.json"
        
        with open(workflow_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_template, f, indent=2, ensure_ascii=False)
        
        # Create README
        readme_content = create_readme(args.name, workflow_template["workflow_name"])
        readme_file = output_dir / "README.md"
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Success output
        print("🛠 Creating FlowPilot Workshop Agent")
        print("=" * 60)
        print(f"📍 Base path: {base_path}")
        print(f"🎯 Creating workflow in: {output_dir.relative_to(base_path)}/")
        print()
        print(f"✅ Created directory: {output_dir}")
        print(f"✅ Created workflow: {args.name}.json")
        print(f"✅ Created README: README.md")
        print()
        print(f"🎉 SUCCESS! {workflow_template['workflow_name']} Created!")
        print("=" * 60)
        print()
        print("📁 Files Created:")
        print(f"├── 📄 {workflow_file}")
        print(f"└── 📖 {readme_file}")
        print()
        print("🚀 Next Steps for Workshop Participants:")
        print("1️⃣  Restart ADK Web to discover the new agent")
        print(f"2️⃣  Look for '{workflow_template['workflow_name']}' in the agent list")
        print("3️⃣  Query: 'Please perform a health check on this Splunk environment'")
        print("4️⃣  Watch the multi-phase workflow execution!")
        print()
        print("🎯 What You'll See:")
        print("├── 🔍 System information gathering")
        print("├── 💓 Health checks execution")
        print("├── 📊 Performance assessment")
        print("└── 📋 Comprehensive summary report")
        print()
        print("🎓 Learning Outcomes:")
        print("├── ✅ Multi-agent workflow orchestration")
        print("├── ✅ Real Splunk environment interaction")
        print("├── ✅ Educational health monitoring")
        print("└── ✅ FlowPilot system capabilities")
        print()
        print("🎪 Ready for an amazing workshop demonstration!")
        
    except Exception as e:
        print(f"❌ Error creating workflow agent: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
