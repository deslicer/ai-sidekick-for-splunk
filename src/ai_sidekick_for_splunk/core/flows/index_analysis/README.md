# Index Analysis Flow

**Workflow ID:** `core.index_analysis`
**Version:** 2.0.0
**Complexity:** Intermediate
**Duration:** 5-15 minutes

## Overview

The Index Analysis Flow provides advanced Guided Agent Flow for index analysis with bounded intelligence tasks, dynamic prompting, and embedded Splunk documentation context. This workflow delivers comprehensive index performance analysis and optimization recommendations.

## Features

- **Bounded Intelligence**: AI-powered analysis with contextual reasoning
- **Dynamic Prompting**: Adaptive queries based on index characteristics
- **Comprehensive Metrics**: Volume, performance, retention, and health analysis
- **Optimization Recommendations**: Actionable insights for index tuning
- **Business Intelligence**: Professional synthesis with ROI calculations

## Workflow Phases

### 1. Index Discovery & Validation
- **Duration**: 1-2 minutes
- **Process**: Identifies target indexes and validates accessibility
- **Output**: Index inventory with metadata

### 2. Performance Analysis
- **Duration**: 2-4 minutes
- **Process**: Analyzes search performance, ingestion rates, and resource utilization
- **Metrics**: Search latency, throughput, hot/warm bucket distribution

### 3. Data Quality Assessment
- **Duration**: 1-3 minutes
- **Process**: Evaluates data completeness, parsing quality, and field extraction
- **Coverage**: Source types, field coverage, parsing errors

### 4. Optimization Recommendations
- **Duration**: 2-4 minutes
- **Process**: Generates specific tuning recommendations
- **Output**: Prioritized action items with impact estimates

### 5. Business Intelligence Synthesis
- **Duration**: 1-2 minutes
- **Process**: Converts technical findings into business insights
- **Output**: Executive summary with cost/benefit analysis

## Prerequisites

- Splunk MCP server running and accessible
- Search permissions on target indexes
- Access to internal metrics (`_internal`, `_introspection`)
- Index management permissions (for optimization recommendations)

## Required Permissions

- `search` capability
- `list_indexes` permission
- Access to target indexes
- Read access to `_internal` and `_introspection` indexes

## Usage

### Via FlowPilot Agent
```python
from ai_sidekick_for_splunk.core.agents.flow_pilot import create_index_analysis_flow_pilot

# Create index analysis agent
analysis_agent = create_index_analysis_flow_pilot()

# Execute analysis for specific index
result = await analysis_agent.execute("analyze index=main")

# Execute analysis for multiple indexes
result = await analysis_agent.execute("analyze index=main,security,web")
```

### Via Specialized Agent
```python
from ai_sidekick_for_splunk.core.agents.index_analysis_flow import IndexAnalysisFlowAgent

# Create specialized agent
agent = IndexAnalysisFlowAgent()

# Execute comprehensive analysis
result = await agent.execute("analyze index=main")
```

## Input Parameters

- **Index Names**: Comma-separated list of indexes to analyze
- **Time Range**: Analysis period (default: last 24 hours)
- **Analysis Depth**: `basic`, `standard`, or `comprehensive`
- **Focus Areas**: Specific aspects to emphasize (performance, capacity, quality)

## Output Format

The workflow produces structured output including:

- **📊 Index Health Score**: Overall index health rating
- **⚡ Performance Metrics**: Search speed, ingestion rates, resource usage
- **💾 Storage Analysis**: Disk usage, retention compliance, bucket distribution
- **🔍 Data Quality**: Parsing success rates, field extraction coverage
- **💰 Cost Analysis**: Storage costs, performance impact, optimization ROI
- **🎯 Recommendations**: Prioritized optimization actions

## Business Value

- **Performance Optimization**: Identify and resolve bottlenecks
- **Cost Reduction**: Optimize storage and compute resource usage
- **Data Quality**: Improve parsing and field extraction
- **Capacity Planning**: Predict growth and resource needs
- **Compliance**: Ensure retention and governance requirements

## Advanced Features

### Bounded Intelligence Tasks
- Context-aware analysis based on index characteristics
- Dynamic query generation for specific use cases
- Intelligent correlation of metrics across time periods

### Integration Points
- **Search Guru**: Advanced query optimization
- **Result Synthesizer**: Business intelligence generation
- **Splunk MCP**: Direct Splunk API integration

## Troubleshooting

### Common Issues

1. **Index Not Found**
   - Verify index names are correct
   - Check user permissions for target indexes
   - Ensure indexes contain data in the analysis time range

2. **Insufficient Permissions**
   - Verify `list_indexes` capability
   - Check search permissions on target indexes
   - Ensure access to `_internal` index

3. **Analysis Timeout**
   - Reduce time range for analysis
   - Focus on specific indexes rather than all
   - Check Splunk system performance

4. **Incomplete Metrics**
   - Verify `_introspection` index availability
   - Check metric collection configuration
   - Ensure sufficient data retention

## Configuration Options

### Analysis Depth Levels

- **Basic**: Core metrics and health indicators
- **Standard**: Comprehensive analysis with recommendations
- **Comprehensive**: Deep dive with historical trends and predictions

### Custom Focus Areas

- **Performance**: Search speed and resource utilization
- **Capacity**: Storage usage and growth projections
- **Quality**: Data parsing and field extraction analysis
- **Security**: Access patterns and compliance metrics

## Related Workflows

- [System Health Check Flow](../health_check/README.md) - Overall system health assessment
- [System Info Flow](../system_info/README.md) - Basic system information

## Best Practices

1. **Regular Analysis**: Run weekly for production indexes
2. **Baseline Establishment**: Create performance baselines for comparison
3. **Trend Monitoring**: Track metrics over time for capacity planning
4. **Action Prioritization**: Focus on high-impact, low-effort optimizations first

## Support

For issues or questions about this workflow:
1. Review the troubleshooting section above
2. Check Splunk search logs for detailed error information
3. Verify all prerequisites and permissions
4. Consult the main documentation
5. Contact the Deslicer team for advanced support
