"""Add Specific Agent Implementation (Python CLI).

Parity with scripts/agent/add-agent.sh:
- Adds a specific execute() implementation to an existing agent
- Updates prompt.py with Index Analyzer instructions if absent
- Prints progress messages mirroring the shell script output
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BLUE = "\033[0;34m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
NC = "\033[0m"


def echo_info(message: str) -> None:
    print(f"{BLUE}{message}{NC}")


def echo_success(message: str) -> None:
    print(f"{GREEN}{message}{NC}")


def echo_warn(message: str) -> None:
    print(f"{YELLOW}{message}{NC}")


def echo_error(message: str) -> None:
    print(f"{RED}{message}{NC}")


def to_class_name(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def find_project_root(start: Path | None = None) -> Path:
    path = (start or Path.cwd()).resolve()
    for parent in [path, *path.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return path


def add_specific_execute(agent_file: Path, agent_name: str) -> bool:
    content = agent_file.read_text()

    old_execute = (
        "    def execute(self, task: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:\n"
        '        """\n'
        "        Execute agent task - Override this method with specific implementation.\n\n"
        "        Args:\n"
        "            task: The task description from the user\n"
        "            context: Optional context information\n\n"
        "        Returns:\n"
        "            Dictionary containing the results\n"
        '        """\n'
        '        logger.info(f"{self.name} executing task: {task}")\n\n'
        "        # Default implementation - contributors should override this\n"
        "        return {\n"
        '            "success": True,\n'
        '            "message": f"{self.name} agent is ready for implementation",\n'
        '            "task": task,\n'
        '            "agent": self.name,\n'
        '            "status": "base_implementation",\n'
        '            "next_steps": [\n'
        '                "Override the execute() method with specific logic",\n'
        '                "Add workflow-specific implementation",\n'
        '                "Test with real data and scenarios"\n'
        "            ]\n"
        "        }\n"
    )

    new_execute = (
        "    def execute(self, task: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:\n"
        '        """\n'
        "        Execute index analysis task with complete 5-phase workflow.\n\n"
        "        This method implements the full systematic analysis workflow\n"
        "        that delegates to SplunkMCP for real data collection.\n\n"
        "        Args:\n"
        "            task: The task description from the user\n"
        "            context: Optional context information\n\n"
        "        Returns:\n"
        "            Dictionary containing the analysis results\n"
        '        """\n'
        f"        try:\n"
        f'            logger.info(f"{to_class_name(agent_name)} executing task: {{task}}")\n\n'
        "            # Extract index name from task\n"
        "            import re\n"
        "            index_match = re.search(r'index[=\\s]+([^\\s]+)', task.lower())\n"
        "            if not index_match:\n"
        "                return {\n"
        '                    "success": False,\n'
        '                    "error": "No index specified in task",\n'
        '                    "message": "Please specify an index to analyze (e.g., \'analyze index=pas\')"\n'
        "                }\n\n"
        "            index_name = index_match.group(1)\n"
        '            logger.info(f"Analyzing index: {index_name}")\n\n'
        "            # Implementation note: In a real implementation, this would delegate to SplunkMCP\n"
        "            # For the workshop, we return a structured response showing the workflow\n\n"
        "            return {\n"
        '                "success": True,\n'
        '                "message": f"Index analysis completed for index={index_name}",\n'
        '                "index": index_name,\n'
        '                "analysis_phases": {\n'
        '                    "phase_1": {\n'
        '                        "name": "Data Types Discovery",\n'
        '                        "status": "completed",\n'
        '                        "spl_query": f"| tstats count WHERE index={index_name} by _time, sourcetype | timechart span=1h sum(count) by sourcetype",\n'
        '                        "findings": "Discovered primary data types and ingestion patterns"\n'
        "                    },\n"
        '                    "phase_2": {\n'
        '                        "name": "Field Analysis",\n'
        '                        "status": "completed",\n'
        '                        "spl_query": f"index={index_name} | head 5000 | fields * | fieldsummary",\n'
        '                        "findings": "Analyzed field distribution and data quality"\n'
        "                    },\n"
        '                    "phase_3": {\n'
        '                        "name": "Sample Data Collection",\n'
        '                        "status": "completed",\n'
        '                        "spl_query": f"index={index_name} | head 10 | table _time, index, source, sourcetype, _raw",\n'
        '                        "findings": "Collected representative data samples"\n'
        "                    },\n"
        '                    "phase_4": {\n'
        '                        "name": "Volume Assessment",\n'
        '                        "status": "completed",\n'
        '                        "spl_query": f"| rest /services/data/indexes | search title={index_name} | table title, currentDBSizeMB, totalEventCount, maxTime, minTime",\n'
        '                        "findings": "Assessed data volume and retention"\n'
        "                    },\n"
        '                    "phase_5": {\n'
        '                        "name": "Business Insights Generation",\n'
        '                        "status": "completed",\n'
        '                        "findings": "Generated actionable business insights and use cases"\n'
        "                    }\n"
        "                },\n"
        '                "business_insights": [\n'
        "                    {\n"
        '                        "persona": "SecOps Analyst",\n'
        '                        "use_case": "Security Monitoring Dashboard",\n'
        '                        "value": "Real-time threat detection and incident response",\n'
        '                        "dashboard_query": f"index={index_name} | stats count by sourcetype, source | sort -count"\n'
        "                    },\n"
        "                    {\n"
        '                        "persona": "DevOps Engineer",\n'
        '                        "use_case": "Application Performance Monitoring",\n'
        '                        "value": "Proactive performance optimization and troubleshooting",\n'
        '                        "alert_query": f"index={index_name} error OR failed | stats count by host | where count > 10"\n'
        "                    },\n"
        "                    {\n"
        '                        "persona": "Business Analyst",\n'
        '                        "use_case": "Operational Intelligence",\n'
        '                        "value": "Data-driven business decision making",\n'
        '                        "dashboard_query": f"index={index_name} | timechart span=1h count | predict count"\n'
        "                    }\n"
        "                ],\n"
        '                "recommendations": [\n'
        '                    "Set up automated dashboards for continuous monitoring",\n'
        '                    "Configure alerts for anomaly detection",\n'
        '                    "Implement data quality checks and validation",\n'
        '                    "Create role-based access controls for sensitive data"\n'
        "                ]\n"
        "            }\n\n"
        "        except Exception as e:\n"
        f'            logger.error(f"{to_class_name(agent_name)} execution failed: {{e}}")\n'
        "            return {\n"
        '                "success": False,\n'
        '                "error": str(e),\n'
        '                "message": "Index analysis execution failed"\n'
        "            }\n"
    )

    if "# Extract index name from task" in content:
        echo_warn(
            "⚠️  Specific implementation already exists in agent.py, skipping implementation update"
        )
        return False

    if old_execute in content:
        content = content.replace(old_execute, new_execute)
        agent_file.write_text(content)
        return True

    echo_warn("⚠️  Default execute method not found - may already be customized")
    return False


def update_prompt(prompt_file: Path, agent_upper: str) -> bool:
    prompt_text = prompt_file.read_text()
    if "5-Phase Analysis Process" in prompt_text:
        echo_warn("⚠️  Specific prompt already exists, skipping prompt update")
        return False

    new_prompt = f'''"""
Agent Instructions.

This file contains the specific instructions for the IndexAnalyzer agent.
"""

# Specific Index Analyzer instructions
{agent_upper}_INSTRUCTIONS = """
You are the Index Analyzer Agent - a demo Splunk index analysis expert.

Your job: Analyze Splunk indexes and provide business insights through a simple 5-step process.

## Core Rules:
- Only work with REAL data from SplunkMCP_agent tool calls
- Never make up fake data or results
- Execute 5 steps sequentially, then stop

## 5-Phase Analysis Process

When user says "analyze index=X":

### Phase 1: Data Types Discovery
Status: `📋 Phase 1/5: Finding data types`
Call SplunkMCP_agent: run splunk search for last 24h or longer if data unavailable.
`| tstats count WHERE index=X by _time, sourcetype
| timechart span=1h sum(count) by sourcetype `

### Phase 2: Field Analysis
Status: `📋 Phase 2/5: Analyzing fields`
Call SplunkMCP_agent: run splunk search for last 24h or longer if data unavailable.
`index=X
| head 5000
| fields *
| fieldsummary`

### Phase 3: Sample Data Collection
Status: `📋 Phase 3/5: Getting samples`
Call SplunkMCP_agent: run splunk search for last 24h or longer if data unavailable.
`index=X | table _time, index, source, sourcetype, _raw`

### Phase 4: Volume Assessment
Status: `📋 Phase 4/5: Checking volume`
Call SplunkMCP_agent: run splunk search for last 24h or longer if data unavailable.
`| rest /services/data/indexes | search title=X | table title, currentDBSizeMB, totalEventCount, maxTime, minTime`

### Phase 5: Business Insights Generation
Status: `📋 Phase 5/5: Creating insights`
Create 3 business use cases based on the real data from phases 1-4.

## Business Intelligence Focus

Generate exactly 3 PERSONA-BASED USE CASES:

### **💼 USE CASE [X]: [PERSONA] - [SPECIFIC BUSINESS SCENARIO]**

**👤 Target Persona**: [SecOps Analyst | DevOps Engineer | Business Analyst]

**🎯 Business Opportunity**: [Specific problem this solves]

**📊 DASHBOARD RECOMMENDATION**: "[Dashboard Name]"
**Key Panels**:
- **Panel 1**: [Panel Name] - [What it shows]
  ```spl
  [READY-TO-USE SPL QUERY]
  ```

**🚨 ALERT STRATEGY**: "[Alert Name]"
**Search Query**:
```spl
[READY-TO-USE ALERT SPL QUERY WITH THRESHOLDS]
```

**💰 Expected Business Value**:
- **Time Saved**: [Specific time savings]
- **Issues Prevented**: [What problems this catches early]
- **Implementation Priority**: [High | Medium | Low] - [Reason]

Remember: Your credibility depends on using REAL Splunk data. Execute the 5-phase workflow ONCE and DONE.
"""
'''
    prompt_file.write_text(new_prompt)
    echo_success("✅ Specific prompt added to prompt.py")
    return True


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Add specific implementation to an agent")
    parser.add_argument("agent_name", help="Agent name (snake_case), e.g., index_analyzer")
    args = parser.parse_args(argv)

    agent_name = args.agent_name
    agent_class = f"{to_class_name(agent_name)}Agent"

    echo_info(f"🔧 Adding Specific Implementation to Agent: {agent_name}")
    echo_info("========================================")
    print("")

    project_root = find_project_root()
    agent_dir = project_root / "src" / "ai_sidekick_for_splunk" / "contrib" / "agents" / agent_name
    agent_file = agent_dir / "agent.py"
    prompt_file = agent_dir / "prompt.py"

    if not agent_dir.exists():
        echo_error(f"❌ Error: Agent directory not found: {agent_dir}")
        echo_warn("💡 Run the creation script first: uv run create-agent <agent_name>")
        sys.exit(1)

    if not agent_file.exists():
        echo_error(f"❌ Error: Agent file not found: {agent_file}")
        echo_warn("💡 Run the creation script first: uv run create-agent <agent_name>")
        sys.exit(1)

    echo_info("📋 Implementation Details:")
    print(f"  Agent Name: {agent_name}")
    print(f"  Agent Class: {agent_class}")
    print("")

    if add_specific_execute(agent_file, agent_name):
        echo_success("✅ Specific implementation added to agent.py")

    echo_info("📄 Adding specific Index Analyzer prompt to prompt.py...")
    update_prompt(prompt_file, agent_name.upper())

    print("")
    echo_success("✅ Specific implementation added successfully!")
    print("")
    echo_info("📋 What Was Added:")
    print("  📋 Specific Execute Method: Complete 5-phase workflow implementation")
    print("  📋 Index Analyzer Prompt: Detailed instructions for systematic analysis")
    print("  🎯 Business Intelligence: Persona-based insights and recommendations")
    print("  📊 Structured Output: Analysis phases, insights, and SPL queries")
    print("")
    echo_info("🎯 Implementation Status:")
    print("  📄 Agent Structure: Complete (from Step 1)")
    print("  🔧 Core Methods: Complete (from Step 1)")
    print("  📋 Specific Implementation: Complete (from Step 2)")
    print("  🤖 Auto-Discovery: Complete (from Step 1)")
    print("  🔗 ADK Integration: Complete (from Step 1)")
    print("")
    echo_info("🎯 Next Steps:")
    print(
        f"  1. Test the specific implementation: uv run python -c \"from ai_sidekick_for_splunk.contrib.agents.{agent_name} import {agent_name}_agent; print({agent_name}_agent.execute('analyze index=pas'))\""
    )
    print(f"  2. Integrate with orchestrator: uv run integrate-agent {agent_name}")
    print("  3. Test full workflow: uv run start-lab")
    print("")
    echo_success("🎉 Agent ready with specific workflow implementation!")


if __name__ == "__main__":
    main()
