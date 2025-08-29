# Simple Workflow Templates

This directory contains template files that you can copy and modify to create your own workflows quickly.

## Available Templates

### 1. Basic Workflow Template (`basic_workflow_template.json`)
- **Best for**: Your first workflow
- **Difficulty**: Beginner
- **What it includes**: The minimum fields needed for a working workflow

### 2. Simple Workflow Template (`simple_workflow_template.json`)
- **Best for**: Most common workflows
- **Difficulty**: Beginner to Intermediate
- **What it includes**: All the common fields with helpful comments

## How to Use Templates

### Step 1: Copy a Template
```bash
cp basic_workflow_template.json ../custom_workflows/my_new_workflow.json
```

### Step 2: Change the Basic Information
Open your new file and change these fields:
- `workflow_id`: Make it unique (like "contrib.myname.my_workflow")
- `workflow_name`: Give it a clear name
- `description`: Explain what it does
- `maintainer`: Put your name

### Step 3: Customize the Tasks
Look at the `core_phases` section and change:
- Phase names and descriptions
- Task names and what they do
- Which agents to use (usually `splunk_mcp` and `result_synthesizer`)

### Step 4: Test Your Workflow
Save the file and test it to make sure it works.

## Template Fields Explained

### Required Fields (you must fill these out):
- `workflow_id`: Unique name for your workflow
- `workflow_name`: Human-readable name
- `description`: What your workflow does
- `agent_dependencies`: Which agents your workflow uses
- `core_phases`: The steps your workflow follows

### Helpful Fields (recommended):
- `business_value`: Why this workflow is useful
- `use_cases`: When you would use this workflow
- `target_audience`: Who should use this workflow
- `estimated_duration`: How long it takes to run

### Optional Fields (nice to have):
- `prerequisites`: What you need before running this workflow
- `success_metrics`: How to know if it worked
- `data_requirements`: What kind of data it needs

## Common Workflow Patterns

### Pattern 1: Simple Search and Report
```
Phase 1: Search for Data (splunk_mcp)
Phase 2: Create Report (result_synthesizer)
```

### Pattern 2: Multi-Step Analysis
```
Phase 1: Get Raw Data (splunk_mcp)
Phase 2: Process Data (splunk_mcp)
Phase 3: Create Summary (result_synthesizer)
```

### Pattern 3: Monitoring Workflow
```
Phase 1: Check System Status (splunk_mcp)
Phase 2: Look for Problems (splunk_mcp)
Phase 3: Generate Alerts (result_synthesizer)
```

## Naming Your Workflow

### Good Workflow Names:
- "Daily Security Check"
- "Website Performance Report"
- "User Login Analysis"

### Good Workflow IDs:
- "contrib.security.daily_check"
- "contrib.performance.website_report"
- "contrib.analysis.user_logins"

## Tips for Success

### Keep It Simple
- Start with 2-3 phases maximum
- Use clear, descriptive names
- Focus on one main goal

### Test Early and Often
- Test after each change
- Start with small amounts of data
- Make sure each phase works before adding the next

### Get Help When Needed
- Look at existing workflows for ideas
- Ask questions in community discussions
- Check the main documentation

## Common Mistakes to Avoid

### Don't:
- Make workflow IDs too long or complicated
- Try to do too many things in one workflow
- Forget to test your changes
- Use unclear or technical names

### Do:
- Keep names simple and clear
- Test each phase separately
- Write good descriptions
- Start small and add features gradually

## Ready to Create?

1. Pick a template that matches your needs
2. Copy it to the custom_workflows directory
3. Follow the steps above to customize it
4. Test it and make improvements
5. Share it with others if it's useful!

Need help? Check the examples in the custom_workflows directory to see real working workflows.
