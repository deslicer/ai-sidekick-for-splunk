# Simple Workflow Examples

This directory contains easy-to-understand workflow examples that show you how to create your own workflows.

## Available Examples

### 1. Simple Search Example (`simple_search_example.json`)
- **What it does**: Searches for data and creates a basic report
- **Difficulty**: Beginner
- **Time**: 2-3 minutes
- **Good for**: Learning the basics of workflows

### 2. Security Audit Example (`security_audit_example.json`)
- **What it does**: Checks for security issues in your data
- **Difficulty**: Intermediate
- **Time**: 15-20 minutes
- **Good for**: Security monitoring

## How to Use These Examples

### Step 1: Look at the Examples
Open the JSON files to see how workflows are structured. Each example shows:
- Basic information about the workflow
- What agents it uses
- What steps it follows
- What kind of results it produces

### Step 2: Copy and Modify
1. Copy one of the example files
2. Change the `workflow_id` and `workflow_name`
3. Modify the tasks to do what you want
4. Test your new workflow

### Step 3: Create Your Own
Use the patterns you see in the examples to create completely new workflows.

## Simple Workflow Pattern

Most workflows follow this simple pattern:

```
1. Get Data (using splunk_mcp agent)
   ↓
2. Process Data (optional middle steps)
   ↓
3. Create Report (using result_synthesizer agent)
```

## Tips for Beginners

- **Start Simple**: Begin with just 2-3 tasks
- **Use Clear Names**: Make task names easy to understand
- **Test Often**: Try your workflow after each change
- **Ask for Help**: Check the main documentation if you get stuck

## Common Workflow Types

### Data Analysis Workflows
- Search for specific data
- Count or summarize results
- Create reports

### Monitoring Workflows
- Check system health
- Look for problems
- Send alerts

### Security Workflows
- Find suspicious activity
- Check access logs
- Generate security reports

## Need Help?

- Look at the existing examples
- Check the templates directory for starting points
- Read the main project documentation
- Ask questions in the community discussions
