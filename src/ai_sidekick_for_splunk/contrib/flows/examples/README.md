# Simple Workflow Examples

This directory contains easy-to-understand examples that help you learn how to create your own workflows.

## What's Here?

```
examples/
├── templates/           # Ready-to-use templates you can copy and modify
├── custom_workflows/    # Complete working examples
├── integrations/        # Examples that connect to external systems
└── factory_patterns/    # How to create many similar workflows quickly
```

## Getting Started

### 1. New to Workflows? Start Here!
- Look at `templates/basic_workflow_template.json`
- Read `custom_workflows/simple_search_example.json`
- Follow the step-by-step guides in each README

### 2. Want to Create Your Own?
- Copy a template from `templates/`
- Modify it for your needs
- Test it and make improvements

### 3. Need to Connect to External Systems?
- Check out `integrations/simple_api_example.json`
- Read the integration guide in `integrations/README.md`

### 4. Creating Many Similar Workflows?
- Learn about factory patterns in `factory_patterns/README.md`

## How Workflows Work

Every workflow follows this basic pattern:

```
1. Get Data from Splunk
   ↓
2. Process or Analyze the Data
   ↓
3. Create a Report or Take Action
```

### Example:
- **Get Data**: Search for failed logins in the last hour
- **Analyze**: Count how many failures per user
- **Report**: Create a security alert if too many failures

## Types of Workflows

### Data Analysis
- Search for specific information
- Count, summarize, or calculate results
- Create reports and dashboards

### System Monitoring
- Check if systems are healthy
- Look for problems or errors
- Send alerts when issues are found

### Security Monitoring
- Watch for suspicious activity
- Check access logs and permissions
- Generate security reports

### Automation
- Detect problems automatically
- Take actions to fix issues
- Create tickets or notifications

## Basic Workflow Structure

Every workflow needs these parts:

### 1. Basic Information
```json
{
  "workflow_id": "contrib.myname.my_workflow",
  "workflow_name": "My Workflow",
  "description": "What this workflow does"
}
```

### 2. Agents (the tools that do the work)
```json
{
  "agent_dependencies": {
    "splunk_mcp": {
      "description": "Searches Splunk data"
    },
    "result_synthesizer": {
      "description": "Creates reports"
    }
  }
}
```

### 3. Phases (the steps to follow)
```json
{
  "core_phases": {
    "get_data": {
      "name": "Get Data",
      "tasks": {
        "search": {
          "title": "Search for Data",
          "agent": "splunk_mcp"
        }
      }
    }
  }
}
```

## Tips for Success

### Start Simple
- Begin with just 2-3 steps
- Use one data source
- Focus on one clear goal

### Use Clear Names
- Make workflow names descriptive
- Use simple task names
- Write good descriptions

### Test Often
- Test after each change
- Start with small data sets
- Make sure each step works

### Get Help
- Look at the examples
- Read the documentation
- Ask questions in discussions

## Common Questions

### Q: Which template should I use?
**A**: Start with `basic_workflow_template.json` for your first workflow. Use `simple_workflow_template.json` when you're more comfortable.

### Q: How do I test my workflow?
**A**: Save your JSON file in the right directory, restart the system, and look for your workflow in the available agents.

### Q: What if I get errors?
**A**: Check that your JSON is valid, make sure all required fields are filled out, and verify your workflow ID is unique.

### Q: Can I modify existing workflows?
**A**: Yes! Copy an existing workflow, change the ID and name, then modify it for your needs.

## Need More Help?

- **Examples**: Look in each subdirectory for specific examples
- **Templates**: Use the templates as starting points
- **Documentation**: Check the main project documentation
- **Community**: Ask questions in community discussions
- **Generator**: Use the workflow generator script for help creating new workflows

## Contributing Your Examples

Created a useful workflow? Share it with the community!

1. Make sure it works well
2. Add clear documentation
3. Test it thoroughly
4. Submit it as an example

Good examples help everyone learn faster!
