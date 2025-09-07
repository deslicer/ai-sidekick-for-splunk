# FlowPilot YAML Templates

This directory contains built-in YAML templates for creating FlowPilot workflow agents. These templates provide a simple way to create complex workflows without writing JSON.

## 🚨 **IMPORTANT REQUIREMENTS**

**FlowPilot workflows have specific requirements for proper execution:**

### **✅ Parallel Execution Required**
- All FlowPilot workflows **MUST** use parallel execution.
- Sequential execution is **NOT supported** yet.
- Templates automatically enforce `parallel: true`

### **✅ Minimum 2 Searches Required**
- FlowPilot requires **minimum 2 searches** per workflow
- Single-search workflows cannot create micro agents
- Templates will **reject** workflows with < 2 searches

### **✅ Automatic Agent Assignment**
- All tasks automatically get `"agent": "splunk_mcp"`
- Enables proper micro agent creation and MCP search execution

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

# Simple workflow (single phase) - MINIMUM 2 SEARCHES REQUIRED
searches:
  - name: "first_search"
    spl: 'index=_internal | stats count by component'
    description: "First search description"
  - name: "second_search"
    spl: 'index=_internal | stats count by sourcetype'
    description: "Second search description"

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
- **Parallel execution requirements**
- **Minimum search count (2+)**

## 🚨 **Common Validation Errors**

### **Error: "FlowPilot requires minimum 2 searches"**
```
❌ FlowPilot requires minimum 2 searches for parallel execution.
   Found: 1 search(es)
   Required: 2+ searches

💡 Recommendations:
   - Add another search to your template
   - Example: Add a complementary search like system info, license check, etc.
   - Sequential execution is not supported in FlowPilot workflows
```

**Solution:** Add at least one more search to your template.

### **Error: "Sequential execution not supported"**
FlowPilot workflows automatically use parallel execution. If you see this error, ensure your template has 2+ searches.

## 📋 **Validation Commands**

```bash
# Validate YAML template before use
ai-sidekick --validate-template my_template.yaml

# Validate generated JSON workflow
ai-sidekick --validate-workflow my_workflow.json --verbose
```

See the [Template Documentation](../templates/simple_template_format.md) for complete format specification.
