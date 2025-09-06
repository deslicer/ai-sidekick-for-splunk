# System Info Flow

**Workflow ID:** `core.system_info`
**Version:** 1.0.0
**Complexity:** Beginner
**Duration:** 1-3 minutes

## Overview

The System Info Flow provides quick system information gathering workflow for Splunk infrastructure monitoring. This workflow is designed for rapid system discovery and basic information collection, perfect for initial assessments and routine monitoring.

## Features

- **Fast Execution**: Quick information gathering in under 3 minutes
- **Comprehensive Coverage**: System overview, version info, and basic metrics
- **Lightweight**: Minimal resource impact during execution
- **Structured Output**: Organized information for easy consumption
- **Integration Ready**: Designed to work with other workflows

## Workflow Phases

### 1. System Discovery
- **Duration**: 30-60 seconds
- **Process**: Identifies Splunk components and basic configuration
- **Output**: System topology and component inventory

### 2. Version & Configuration Info
- **Duration**: 30-60 seconds
- **Process**: Collects version information and key configuration details
- **Coverage**: Splunk version, apps, configurations

### 3. Basic Metrics Collection
- **Duration**: 30-60 seconds
- **Process**: Gathers essential system metrics
- **Metrics**: License usage, index counts, user activity

### 4. Information Synthesis
- **Duration**: 15-30 seconds
- **Process**: Organizes and formats collected information
- **Output**: Structured system summary

## Prerequisites

- Splunk MCP server running and accessible
- Basic search permissions
- Access to system information indexes

## Required Permissions

- `search` capability
- Access to `_internal` index
- Basic system visibility permissions

## Usage

### Via FlowPilot Agent
```python
from ai_sidekick_for_splunk.core.agents.flow_pilot import create_system_info_flow_pilot

# Create system info agent
info_agent = create_system_info_flow_pilot()

# Execute system info collection
result = await info_agent.execute("Gather system information")
```

### Via Direct Workflow
```python
from ai_sidekick_for_splunk.core.flows_engine import AgentFlow, FlowEngine

# Load workflow
workflow = AgentFlow.load_from_json("system_info.json")

# Execute with engine
engine = FlowEngine(workflow)
result = await engine.execute("System information gathering")
```

## Output Format

The workflow produces structured output including:

- **🖥️ System Overview**: Splunk version, build, and platform information
- **📦 Component Inventory**: Installed apps, add-ons, and configurations
- **📊 Basic Metrics**: License usage, data volume, user counts
- **🔧 Configuration Summary**: Key settings and deployment topology
- **📈 Usage Statistics**: Recent activity and performance indicators

## Information Categories

### System Details
- Splunk version and build information
- Operating system and hardware details
- Installation path and configuration locations
- License information and usage

### Component Inventory
- Installed applications and add-ons
- Configuration files and their locations
- Index definitions and settings
- User roles and permissions overview

### Basic Metrics
- Data ingestion rates and volumes
- Search activity and performance
- License usage and compliance
- System resource utilization

### Deployment Information
- Server roles and cluster configuration
- Distributed search setup
- Forwarder connections and status
- Network topology overview

## Use Cases

### Initial Assessment
- New environment discovery
- System documentation creation
- Compliance auditing preparation
- Migration planning

### Routine Monitoring
- Regular system health checks
- License usage tracking
- Configuration drift detection
- Capacity planning data collection

### Troubleshooting Support
- Environment baseline establishment
- Configuration verification
- Component inventory for support cases
- System state documentation

## Integration Points

### Upstream Workflows
- Can be used as a prerequisite for more detailed analysis workflows
- Provides baseline information for health checks
- Supports capacity planning workflows

### Downstream Processing
- Output can feed into monitoring systems
- Information can be used for automated reporting
- Data supports compliance documentation

## Troubleshooting

### Common Issues

1. **Access Denied**
   - Verify basic search permissions
   - Check access to `_internal` index
   - Ensure user has system visibility rights

2. **Incomplete Information**
   - Review permission levels for comprehensive data
   - Check if distributed search is properly configured
   - Verify forwarder connectivity for complete topology

3. **Slow Execution**
   - Check system load and performance
   - Verify network connectivity to all components
   - Consider reducing information scope if needed

## Configuration Options

### Information Scope
- **Basic**: Core system information only
- **Standard**: Comprehensive system details (default)
- **Extended**: Includes detailed configuration and metrics

### Output Format
- **Summary**: High-level overview format
- **Detailed**: Complete information with all details
- **JSON**: Structured data for programmatic use

## Best Practices

1. **Regular Collection**: Run monthly for documentation updates
2. **Baseline Creation**: Establish system baselines for comparison
3. **Change Tracking**: Monitor configuration changes over time
4. **Documentation**: Use output for system documentation maintenance

## Related Workflows

- [System Health Check Flow](../health_check/README.md) - Comprehensive health assessment
- [Index Analysis Flow](../index_analysis/README.md) - Detailed index performance analysis

## Output Examples

### System Overview
```
🖥️ Splunk Enterprise 9.1.2 (Build: b6b9c8185839)
📍 Platform: Linux x86_64
🏢 Deployment: Distributed Search Head
📄 License: Enterprise (500GB/day)
```

### Component Summary
```
📦 Applications: 15 installed (12 enabled)
🔧 Indexes: 25 total (20 active)
👥 Users: 45 active users
🔍 Saved Searches: 120 scheduled
```

## Support

For issues or questions about this workflow:
1. Check the troubleshooting section above
2. Verify basic permissions and connectivity
3. Review Splunk logs for any error details
4. Consult the main documentation
5. Contact the Deslicer team
