#!/usr/bin/env python3
"""
Create Flow Agent Script for Splunk AI Sidekick Workshop

This script creates a simple workflow agent for workshop participants to demonstrate
the FlowPilot system's capabilities. It generates a complete workflow definition
that performs basic Splunk environment health checks and system information gathering.

Usage:
    python create_flow_agent.py

The script will:
1. Create a dev1666_agent workflow in contrib/flows/
2. Generate the JSON workflow definition
3. Create a README.md file with documentation
4. Provide instructions for testing the agent

Workshop participants can then:
1. Restart ADK Web
2. See the new agent in the agent list
3. Query the agent to see it perform health checks
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def create_workflow_definition() -> dict[str, Any]:
    """Create the dev1666_agent workflow definition."""
    return {
        "workflow_id": "dev1666_agent",
        "workflow_name": "Dev1666 System Health Agent",
        "workflow_type": "troubleshooting",
        "workflow_category": "system_health",
        "source": "contrib",
        "maintainer": "community",
        "stability": "experimental",
        "complexity_level": "beginner",
        "estimated_duration": "2-3 minutes",
        "version": "1.0.0",
        "splunk_versions": ["8.0+", "9.0+"],
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "documentation_url": "README.md",
        
        "description": "A simple workshop demonstration agent that performs basic Splunk environment health checks and gathers system information. Perfect for learning the FlowPilot workflow system.",
        
        "business_value": "Provides quick health assessment of Splunk environment for workshop participants to understand system status and learn workflow execution patterns.",
        
        "use_cases": [
            "workshop_demonstration",
            "basic_health_monitoring",
            "system_status_overview",
            "learning_workflow_patterns"
        ],
        
        "success_metrics": [
            "successful_health_check_completion",
            "system_info_retrieval",
            "clear_status_reporting"
        ],
        
        "target_audience": [
            "workshop_participants",
            "splunk_beginners",
            "workflow_learners"
        ],
        
        "prerequisites": [
            "splunk_mcp_server",
            "basic_splunk_access"
        ],
        
        "required_permissions": [
            "search",
            "list_indexes"
        ],
        
        "supported_splunk_versions": ["8.0+", "9.0+"],
        
        "data_requirements": {
            "minimum_events": 100,
            "required_sourcetypes": [],
            "optional_fields": []
        },
        
        "agent": "FlowPilot",
        "agent_dependencies": {
            "splunk_mcp": {
                "required": True,
                "description": "Splunk MCP server for executing searches and gathering system information",
                "capabilities": [
                    "search_execution",
                    "index_listing", 
                    "system_info_retrieval"
                ]
            }
        },
        
        "workflow_instructions": "You are the Dev1666 System Health Agent - a friendly workshop demonstration agent that helps participants learn about Splunk health monitoring. Execute each phase step by step, providing clear explanations of what you're checking and why it matters for system health.",
        
        "core_phases": {
            "system_info": {
                "phase_name": "System Information Gathering",
                "description": "Collect basic Splunk system information and configuration details",
                "tasks": [
                    {
                        "task_name": "gather_splunk_version",
                        "agent": "splunk_mcp",
                        "goal": "Get Splunk version and basic system information",
                        "prompt": "Please retrieve the Splunk version information and basic system details. This helps us understand what Splunk environment we're working with.",
                        "expected_output": "Splunk version, build information, and system configuration summary"
                    },
                    {
                        "task_name": "list_available_indexes",
                        "agent": "splunk_mcp", 
                        "goal": "List all available indexes to understand data landscape",
                        "prompt": "List all available Splunk indexes. This gives us an overview of what data sources are configured in this environment.",
                        "expected_output": "Complete list of indexes with basic metadata"
                    }
                ]
            },
            "health_checks": {
                "phase_name": "Basic Health Assessment",
                "description": "Perform fundamental health checks on the Splunk environment",
                "tasks": [
                    {
                        "task_name": "check_recent_data",
                        "agent": "splunk_mcp",
                        "goal": "Verify that recent data is being indexed",
                        "prompt": "Search for events from the last 24 hours across all indexes to verify data is flowing. Use a simple search like: search earliest=-24h | head 10 | stats count. This confirms the system is actively receiving and indexing data.",
                        "expected_output": "Count of recent events and confirmation of data flow"
                    },
                    {
                        "task_name": "check_system_performance",
                        "agent": "splunk_mcp",
                        "goal": "Basic performance indicators check",
                        "prompt": "Check basic system performance by running a simple search to measure response time. Search for: | rest /services/server/info | eval response_time=now() | table response_time. This gives us a baseline performance indicator.",
                        "expected_output": "Basic performance metrics and response time information"
                    }
                ]
            },
            "summary_report": {
                "phase_name": "Health Summary Report",
                "description": "Compile findings into a clear, actionable summary",
                "tasks": [
                    {
                        "task_name": "generate_health_summary",
                        "agent": "result_synthesizer",
                        "goal": "Create a comprehensive but beginner-friendly health report",
                        "prompt": "Based on the system information and health checks performed, create a clear and friendly summary report. Include: 1) System overview (version, indexes), 2) Health status (data flow, performance), 3) Any recommendations for workshop participants. Keep it educational and encouraging - this is for learning purposes!",
                        "expected_output": "Comprehensive health report with educational insights for workshop participants"
                    }
                ]
            }
        }
    }

def create_readme_content() -> str:
    """Create README content for the dev1666_agent workflow."""
    return """# Dev1666 System Health Agent

## 🎯 Overview

The **Dev1666 System Health Agent** is a workshop demonstration workflow designed to help participants learn the FlowPilot system while performing basic Splunk environment health checks.

## 🚀 What This Agent Does

This agent performs a simple but comprehensive health assessment of your Splunk environment:

### Phase 1: System Information Gathering
- **Splunk Version Check**: Retrieves version and build information
- **Index Discovery**: Lists all available indexes in the environment

### Phase 2: Basic Health Assessment  
- **Data Flow Verification**: Confirms recent data is being indexed
- **Performance Check**: Measures basic system response times

### Phase 3: Health Summary Report
- **Comprehensive Report**: Generates an educational summary of findings
- **Learning Insights**: Provides explanations suitable for workshop participants

## 🎓 Learning Objectives

This workflow demonstrates:
- **Multi-phase execution**: How FlowPilot orchestrates complex workflows
- **Agent coordination**: Integration between splunk_mcp and result_synthesizer
- **Real-world monitoring**: Practical Splunk health checking techniques
- **Clear reporting**: How to generate actionable insights from technical data

## 🛠 Workshop Usage

### Step 1: Agent Discovery
After creating this workflow, restart ADK Web to discover the new agent:
```bash
# Restart your ADK Web instance
# The agent will appear as "Dev1666 System Health Agent"
```

### Step 2: Execute the Workflow
Query the agent with a simple request:
```
"Please perform a health check on this Splunk environment"
```

### Step 3: Observe the Execution
Watch as the agent:
1. Gathers system information
2. Performs health checks
3. Generates a comprehensive report

## 📋 Prerequisites

- Splunk MCP server running and accessible
- Basic Splunk search permissions
- At least some indexed data (for meaningful health checks)

## 🎯 Expected Outcomes

After execution, you'll receive:
- **System Overview**: Version, configuration, and available data sources
- **Health Status**: Data flow confirmation and performance indicators  
- **Educational Insights**: Explanations of what each check means
- **Learning Summary**: Key takeaways for workshop participants

## 🔧 Technical Details

- **Workflow Type**: Troubleshooting
- **Category**: System Health
- **Complexity**: Beginner
- **Duration**: 2-3 minutes
- **Source**: Community Contribution

## 🎉 Workshop Success

This agent successfully demonstrates:
- ✅ FlowPilot's multi-agent orchestration
- ✅ Real Splunk environment interaction
- ✅ Educational workflow design
- ✅ Clear, actionable reporting

Perfect for learning how powerful workflows can be built with simple, reusable components!
"""

def create_agent_directory_structure(base_path: Path) -> Path:
    """Create the directory structure for the dev1666_agent workflow."""
    agent_dir = base_path / "contrib" / "flows" / "dev1666_agent"
    agent_dir.mkdir(parents=True, exist_ok=True)
    return agent_dir

def write_workflow_files(agent_dir: Path) -> tuple[Path, Path]:
    """Write the workflow JSON and README files."""
    # Write the workflow definition
    workflow_def = create_workflow_definition()
    workflow_file = agent_dir / "dev1666_agent.json"
    
    with open(workflow_file, 'w', encoding='utf-8') as f:
        json.dump(workflow_def, f, indent=2, ensure_ascii=False)
    
    # Write the README
    readme_content = create_readme_content()
    readme_file = agent_dir / "README.md"
    
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    return workflow_file, readme_file

def print_success_message(workflow_file: Path, readme_file: Path) -> None:
    """Print success message with next steps."""
    print("🎉 SUCCESS! Dev1666 System Health Agent Created!")
    print("=" * 60)
    print()
    print("📁 Files Created:")
    print(f"├── 📄 {workflow_file}")
    print(f"└── 📖 {readme_file}")
    print()
    print("🚀 Next Steps for Workshop Participants:")
    print("1️⃣  Restart ADK Web to discover the new agent")
    print("2️⃣  Look for 'Dev1666 System Health Agent' in the agent list")
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

def main():
    """Main function to create the dev1666_agent workflow."""
    print("🛠 Creating Dev1666 System Health Agent for Workshop")
    print("=" * 60)
    print()
    
    # Determine the base path (src/splunk_ai_sidekick)
    script_dir = Path(__file__).parent
    base_path = script_dir.parent
    
    print(f"📍 Base path: {base_path}")
    print("🎯 Creating workflow in: contrib/flows/dev1666_agent/")
    print()
    
    try:
        # Create directory structure
        agent_dir = create_agent_directory_structure(base_path)
        print(f"✅ Created directory: {agent_dir}")
        
        # Write workflow files
        workflow_file, readme_file = write_workflow_files(agent_dir)
        print(f"✅ Created workflow: {workflow_file.name}")
        print(f"✅ Created README: {readme_file.name}")
        print()
        
        # Print success message
        print_success_message(workflow_file, readme_file)
        
    except Exception as e:
        print(f"❌ Error creating dev1666_agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
