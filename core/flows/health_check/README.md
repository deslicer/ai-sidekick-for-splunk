# System Health Check Flow

**Workflow ID:** `core.health_check`
**Version:** 1.0.1
**Complexity:** Beginner
**Duration:** 2-5 minutes

## Overview

The System Health Check Flow provides fast parallel assessment of Splunk infrastructure components with real-time monitoring and alerting capabilities. This workflow is designed for rapid system validation and health monitoring.

## Features

- **Parallel Execution**: Multiple health checks run simultaneously for faster results
- **Real-time Monitoring**: Live status updates during execution
- **Comprehensive Coverage**: Checks indexers, search heads, forwarders, and cluster health
- **Alert Integration**: Automatic alerting for critical issues
- **Business Intelligence**: Professional synthesis of technical results

## Workflow Phases

### 1. Rapid Health Assessment
- **Duration**: 30-60 seconds
- **Parallel Tasks**: 4 concurrent health checks
- **Coverage**: Core system components

### 2. Health Status Synthesis
- **Duration**: 30-60 seconds
- **Process**: Aggregates results and generates business insights
- **Output**: Executive summary with actionable recommendations

## Prerequisites

- Splunk MCP server running and accessible
- Search permissions on system indexes
- Access to internal Splunk metrics

## Required Permissions

- `search` capability
- Access to `_internal` index
- Cluster management visibility (if applicable)

## Usage

### Via FlowPilot Agent
```python
from splunk_ai_sidekick.core.agents.flow_pilot import create_health_check_flow_pilot

# Create health check agent
health_agent = create_health_check_flow_pilot()

# Execute health check
result = await health_agent.execute("Perform system health check")
```

### Via Direct Workflow
```python
from splunk_ai_sidekick.core.flows_engine import AgentFlow, FlowEngine

# Load workflow
workflow = AgentFlow.load_from_json("health_check.json")

# Execute with engine
engine = FlowEngine(workflow)
result = await engine.execute("System health assessment")
```

## Output Format

The workflow produces structured output including:

- **🏥 System Health Score**: Overall health percentage
- **⚡ Performance Metrics**: Key performance indicators
- **🚨 Critical Issues**: Immediate attention items
- **📊 Recommendations**: Actionable improvement suggestions
- **📈 Trends**: Historical comparison data

## Business Value

- **Reduced MTTR**: Faster issue identification and resolution
- **Proactive Monitoring**: Early detection of potential problems
- **Cost Optimization**: Efficient resource utilization insights
- **Compliance**: Automated health reporting for audits

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   - Verify Splunk MCP server is running
   - Check network connectivity
   - Validate authentication credentials

2. **Permission Denied**
   - Ensure user has search capabilities
   - Verify access to `_internal` index
   - Check role-based permissions

3. **Incomplete Results**
   - Review search timeouts
   - Check data availability in time range
   - Validate index accessibility

## Related Workflows

- [Index Analysis Flow](../index_analysis/README.md) - Deep dive into index performance
- [System Info Flow](../system_info/README.md) - Basic system information gathering

## Support

For issues or questions about this workflow:
1. Check the troubleshooting section above
2. Review Splunk logs for error details
3. Consult the main documentation
4. Contact the Deslicer team
