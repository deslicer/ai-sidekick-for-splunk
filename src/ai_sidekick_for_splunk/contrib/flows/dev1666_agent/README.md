# Dev1666 System Health Agent

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
