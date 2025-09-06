# FlowPilot YAML Templates

This directory contains built-in YAML templates for creating FlowPilot workflow agents. These templates provide a simple way to create complex workflows without writing JSON.

## Available Templates

### `simple_health_check.yaml`
- **Category:** Monitoring
- **Complexity:** Beginner
- **Description:** Basic health check with essential system metrics
- **Use Cases:** Daily monitoring, educational, system validation

### `security_audit.yaml`
- **Category:** Security
- **Complexity:** Intermediate
- **Description:** Comprehensive security analysis with authentication, access control, and change tracking
- **Use Cases:** Security auditing, compliance, incident response

## Using Built-in Templates

```bash
# Use a built-in template (creates local copy)
ai-sidekick --create-flow-agent my_health_check --template simple_health_check

# Use custom template file
ai-sidekick --create-flow-agent my_security --template-file security_audit.yaml
```

## Template Format

Templates use a simple YAML format focusing on business logic and SPL searches:

```yaml
# Basic Information
name: "my_template"
title: "My Workflow"
description: "What this workflow does"
category: "analysis"  # security, performance, troubleshooting, analysis, monitoring
complexity: "beginner"  # beginner, intermediate, advanced

# Business Context
business_value: "Why this is valuable"
use_cases:
  - "First use case"
  - "Second use case"

# Simple workflow (single phase)
searches:
  - name: "my_search"
    spl: 'index=_internal | stats count'
    description: "What this search does"

# OR Complex workflow (multiple phases)
phases:
  - name: "phase1"
    title: "First Phase"
    description: "What this phase does"
    searches:
      - name: "search1"
        spl: 'index=_internal | head 10'
        description: "Phase 1 search"
```

## Contributing Templates

1. Create your YAML template file
2. Test it: `ai-sidekick --create-flow-agent test_flow --template-file your_template.yaml`
3. Submit a pull request with your template

## Template Validation

Templates are automatically validated for:
- YAML syntax
- Required fields
- SPL syntax (basic checks)
- Business logic consistency

See the [Template Documentation](../templates/simple_template_format.md) for complete format specification.
