# Simple Flow Template Format

## Overview

This document describes the simple YAML template format for creating FlowPilot workflow agents. This format focuses on the essentials and automatically generates the complex JSON structure required by FlowPilot.

## Why Use Templates?

The traditional FlowPilot JSON format is powerful but complex:
- 300+ lines of JSON with many required fields
- Complex nested structure for phases, searches, dependencies
- Contributors need to understand FlowPilot internals
- Hard to focus on the actual SPL searches and business logic

Templates solve this by providing a **simple, contributor-friendly format** that focuses on what matters most: **your SPL searches and business logic**.

## Template Structure

### Basic Template (Simple Searches)

```yaml
# Basic Information
name: "my_workflow"
title: "My Custom Workflow"
description: "What this workflow does and why it's useful"
category: "security"  # security, performance, troubleshooting, analysis, monitoring, data_quality
complexity: "beginner"  # beginner, intermediate, advanced
version: "1.0.0"
author: "community"

# Requirements
splunk_versions: ["8.0+", "9.0+"]
required_permissions: ["search", "rest_api_access"]
required_indexes: ["_audit", "_internal"]  # Optional

# Business Context
business_value: "Why this workflow is valuable to users"
use_cases:
  - "First use case"
  - "Second use case"
  - "Third use case"

success_metrics:
  - "How you measure success"
  - "What good results look like"

target_audience:
  - "Who should use this"
  - "What roles benefit"

# Simple Workflow - Single Phase
searches:
  - name: "my_search"
    spl: 'index=_audit | stats count by user'
    earliest: "-24h@h"
    latest: "now"
    description: "What this search does"
    expected_results: "What you expect to find"
  
  - name: "another_search"
    spl: 'index=_internal log_level=ERROR | head 10'
    earliest: "-1h@h"
    latest: "now"
    description: "Find recent errors"
    expected_results: "List of recent system errors"

# Advanced Options
parallel_execution: true
streaming_support: true
educational_mode: false
estimated_duration: "5-10 minutes"
```

### Advanced Template (Multiple Phases)

```yaml
# Basic Information (same as above)
name: "complex_workflow"
title: "Complex Multi-Phase Workflow"
description: "Advanced workflow with multiple coordinated phases"
category: "security"
complexity: "intermediate"

# Business Context (same as above)
business_value: "Comprehensive analysis with coordinated phases"
use_cases: ["Advanced analysis", "Multi-step investigation"]

# Complex Workflow - Multiple Phases
phases:
  - name: "data_collection"
    title: "Data Collection Phase"
    description: "Gather initial data for analysis"
    parallel: true  # Searches in this phase can run in parallel
    searches:
      - name: "collect_events"
        spl: 'index=_audit | head 1000'
        earliest: "-24h@h"
        latest: "now"
        description: "Collect audit events"
      
      - name: "collect_errors"
        spl: 'index=_internal log_level=ERROR'
        earliest: "-24h@h"
        latest: "now"
        description: "Collect error events"
  
  - name: "analysis"
    title: "Analysis Phase"
    description: "Analyze collected data"
    depends_on: ["data_collection"]  # Wait for data collection to complete
    searches:
      - name: "analyze_patterns"
        spl: 'index=_audit | stats count by action'
        earliest: "-24h@h"
        latest: "now"
        description: "Analyze action patterns"

# Advanced Options
parallel_execution: false  # Phases run sequentially due to dependencies
streaming_support: true
educational_mode: true
estimated_duration: "10-15 minutes"
```

## Field Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique identifier for the template (used for file naming) |
| `title` | string | Human-readable title displayed in UI |
| `description` | string | What this workflow does and why it's useful |
| `category` | enum | Template category (see categories below) |
| `business_value` | string | Why this workflow is valuable |
| `use_cases` | array | List of use cases for this workflow |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `complexity` | enum | "beginner" | Complexity level (beginner, intermediate, advanced) |
| `version` | string | "1.0.0" | Template version |
| `author` | string | "community" | Template author |
| `splunk_versions` | array | ["8.0+", "9.0+"] | Supported Splunk versions |
| `required_permissions` | array | ["search"] | Required Splunk permissions |
| `required_indexes` | array | null | Required indexes (optional) |
| `dependencies` | array | null | Additional agent dependencies |
| `success_metrics` | array | null | How to measure success |
| `target_audience` | array | null | Who should use this |
| `parallel_execution` | boolean | false | Can phases run in parallel |
| `streaming_support` | boolean | true | Support streaming responses |
| `educational_mode` | boolean | false | Include educational explanations |
| `estimated_duration` | string | "5-10 minutes" | Expected execution time |

## Categories

| Category | Description | Use Cases |
|----------|-------------|-----------|
| `security` | Security analysis and compliance | Auditing, threat detection, access control |
| `performance` | Performance monitoring and optimization | System tuning, bottleneck identification |
| `troubleshooting` | Problem diagnosis and resolution | Issue investigation, root cause analysis |
| `analysis` | Data analysis and insights | Business intelligence, trend analysis |
| `monitoring` | Ongoing system monitoring | Health checks, alerting, dashboards |
| `data_quality` | Data validation and quality checks | Data integrity, completeness validation |

## Search Definition

Each search in your template must include:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique name for the search |
| `spl` | string | Yes | SPL search query |
| `description` | string | Yes | What this search does |
| `earliest` | string | No | Earliest time (default: "-24h@h") |
| `latest` | string | No | Latest time (default: "now") |
| `expected_results` | string | No | What results to expect |
| `timeout` | integer | No | Search timeout in seconds (default: 300) |

### Time Range Examples

```yaml
# Last 24 hours
earliest: "-24h@h"
latest: "now"

# Last week
earliest: "-7d@d"
latest: "now"

# Specific time window
earliest: "-2h@h"
latest: "-1h@h"

# Real-time (last 5 minutes)
earliest: "-5m@m"
latest: "now"
```

## Phase Definition (Advanced)

For complex workflows with multiple phases:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique phase identifier |
| `title` | string | Yes | Human-readable phase title |
| `description` | string | Yes | What this phase accomplishes |
| `searches` | array | Yes | List of searches in this phase |
| `parallel` | boolean | No | Can searches in this phase run in parallel |
| `depends_on` | array | No | List of phase names this phase depends on |

## Validation

Templates are automatically validated for:

### Structure Validation
- YAML syntax correctness
- Required fields presence
- Field type validation
- Enum value validation

### SPL Validation
- Basic syntax checking (quotes, brackets)
- Common SPL command validation
- Search structure validation

### Business Logic Validation
- Phase dependency validation
- Search name uniqueness
- Category and complexity consistency

## Usage Examples

### Create from Template File
```bash
# Use custom template file
ai-sidekick --create-flow-agent my_security --template-file security_audit.yaml

# Use template from any location
ai-sidekick --create-flow-agent custom_flow --template-file /path/to/my_template.yaml
```

### Generated Files
When you create a workflow from a template, the system generates:

```
contrib/flows/my_security/
├── my_security.yaml       # Template source (editable)
├── my_security.json       # Generated FlowPilot JSON
├── README.md              # Generated documentation
└── .template_source       # Origin tracking
```

## Best Practices

### 1. Start Simple
Begin with the simple search format, then move to phases as needed:

```yaml
# Start with this
searches:
  - name: "basic_check"
    spl: 'index=_internal | head 10'
    description: "Basic system check"

# Evolve to this when you need coordination
phases:
  - name: "collection"
    searches: [...]
  - name: "analysis"
    depends_on: ["collection"]
    searches: [...]
```

### 2. Focus on Real SPL
Write actual working SPL queries, not placeholders:

```yaml
# Good - Real, working SPL
spl: 'index=_audit action=login_attempt success=false | stats count by user, src_ip | sort -count | head 20'

# Bad - Placeholder text
spl: 'search for failed logins and analyze patterns'
```

### 3. Provide Context
Include meaningful descriptions and expected results:

```yaml
- name: "failed_logins"
  spl: 'index=_audit action=login_attempt success=false | stats count by user'
  description: "Identify users with failed login attempts in the last 24 hours"
  expected_results: "List of users sorted by failed login count"
```

### 4. Use Appropriate Time Ranges
Choose time ranges that make sense for your use case:

```yaml
# Security analysis - recent activity
earliest: "-24h@h"

# Trend analysis - longer period
earliest: "-7d@d"

# Real-time monitoring
earliest: "-5m@m"
```

### 5. Consider Your Audience
Set complexity and educational mode appropriately:

```yaml
# For beginners
complexity: "beginner"
educational_mode: true

# For experts
complexity: "advanced"
educational_mode: false
```

## Template Development Workflow

1. **Plan Your Workflow**
   - Define the business problem
   - Identify required searches
   - Determine if you need phases

2. **Create Template**
   - Start with basic information
   - Add your SPL searches
   - Test searches manually in Splunk

3. **Generate and Test**
   ```bash
   ai-sidekick --create-flow-agent test_flow --template-file my_template.yaml
   ```

4. **Iterate**
   - Edit the YAML template
   - Regenerate the workflow
   - Test with FlowPilot

5. **Share**
   - Submit your template to the community
   - Include documentation and examples

## Common Patterns

### Health Check Pattern
```yaml
category: "monitoring"
complexity: "beginner"
searches:
  - name: "system_info"
    spl: '| rest /services/server/info'
  - name: "data_flow"
    spl: 'search earliest=-24h | stats count'
```

### Security Audit Pattern
```yaml
category: "security"
complexity: "intermediate"
phases:
  - name: "authentication"
    searches: [login analysis searches]
  - name: "access_control"
    searches: [permission analysis searches]
```

### Performance Analysis Pattern
```yaml
category: "performance"
complexity: "advanced"
parallel_execution: true
searches:
  - name: "cpu_usage"
    spl: 'index=_internal group=per_host_thruput'
  - name: "memory_usage"
    spl: 'index=_internal group=memory'
```

## Migration from JSON

If you have existing FlowPilot JSON workflows, you can convert them to templates:

1. **Extract Core Information**
   - Copy workflow name, description, category
   - Identify business value and use cases

2. **Extract Searches**
   - Find the `core_phases` section
   - Extract search queries and descriptions
   - Convert to template search format

3. **Simplify Structure**
   - Remove FlowPilot-specific boilerplate
   - Focus on business logic
   - Use template defaults where possible

4. **Test and Validate**
   - Generate new JSON from template
   - Compare functionality
   - Test with FlowPilot

## Troubleshooting

### Common Validation Errors

**"Template must define either 'searches' or 'phases'"**
- You must include either a `searches` section or a `phases` section
- Don't include both in the same template

**"SPL query cannot be empty"**
- Every search must have a non-empty `spl` field
- Check for missing or empty search queries

**"Search names within a phase must be unique"**
- Each search name must be unique within its phase
- Use descriptive, unique names for all searches

**"Phase 'analysis' depends on non-existent phase 'collection'"**
- Phase dependencies must reference existing phases
- Check spelling and ensure dependent phases are defined

### Performance Issues

**Searches taking too long**
- Add appropriate time ranges with `earliest` and `latest`
- Use more specific index and sourcetype filters
- Consider breaking complex searches into phases

**Memory issues with large result sets**
- Add `| head N` to limit results
- Use `stats` commands to aggregate data
- Increase timeout values if needed

### SPL Syntax Issues

**Unmatched quotes**
- Ensure all quotes are properly paired
- Use single quotes for string literals in SPL
- Escape quotes within strings if needed

**Invalid SPL commands**
- Test your SPL queries in Splunk Search before adding to template
- Use proper SPL syntax and command order
- Check field names and index references

## Support and Community

- **Documentation**: [FlowPilot Documentation](../README.md)
- **Examples**: See built-in templates in `core/templates/`
- **Issues**: Report problems via GitHub issues
- **Community**: Join discussions in our community forums

---

*This documentation is part of the FlowPilot template system. For the latest version, see the [GitHub repository](https://github.com/deslicer/ai-sidekick-for-splunk).*