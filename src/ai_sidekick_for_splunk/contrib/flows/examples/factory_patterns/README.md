# Simple Factory Patterns

Factory patterns help you create multiple similar workflows quickly and easily.

## What is a Factory Pattern?

A factory pattern is like a template that can create many similar workflows with small differences.

**Example**: Instead of creating separate workflows for each department's security check, you create one "factory" that can generate security check workflows for any department.

## When to Use Factory Patterns

### Good Use Cases:
- **Multiple Departments**: Same workflow for Sales, Marketing, IT, etc.
- **Different Time Periods**: Daily, weekly, monthly versions of the same analysis
- **Various Data Sources**: Same analysis for different log types
- **Different Environments**: Dev, test, and production versions

### Simple Example:
You want to monitor different servers. Instead of creating separate workflows for each server, you create one factory that generates monitoring workflows for any server name.

## Basic Factory Approach

### Step 1: Create a Template Workflow
```json
{
  "workflow_name": "Monitor {SERVER_NAME}",
  "description": "Monitor server {SERVER_NAME} for issues",
  "search_query": "index=servers host={SERVER_NAME}"
}
```

### Step 2: Create a Simple Script
```python
def create_server_workflow(server_name):
    # Read the template
    with open('server_template.json', 'r') as f:
        template = f.read()

    # Replace the placeholder
    workflow = template.replace('{SERVER_NAME}', server_name)

    # Save the new workflow
    filename = f'monitor_{server_name}.json'
    with open(filename, 'w') as f:
        f.write(workflow)

# Create workflows for different servers
create_server_workflow('web01')
create_server_workflow('db01')
create_server_workflow('app01')
```

### Step 3: Run the Script
Now you have three workflows:
- `monitor_web01.json`
- `monitor_db01.json`
- `monitor_app01.json`

## Simple Factory Examples

### Example 1: Department Reports
**Template**: `department_template.json`
```json
{
  "workflow_name": "{DEPT} Weekly Report",
  "search_query": "index=employees department={DEPT}"
}
```

**Generate workflows for**: Sales, Marketing, Engineering, Support

### Example 2: Time-Based Analysis
**Template**: `timeframe_template.json`
```json
{
  "workflow_name": "{PERIOD} Security Analysis",
  "parameters": {"earliest_time": "{TIME_RANGE}"}
}
```

**Generate workflows for**: Daily (-1d), Weekly (-7d), Monthly (-30d)

### Example 3: Environment Monitoring
**Template**: `environment_template.json`
```json
{
  "workflow_name": "{ENV} Health Check",
  "search_query": "index={ENV}_logs"
}
```

**Generate workflows for**: dev, test, staging, production

## Tools for Creating Factories

### Option 1: Simple Python Script
- Easy to understand and modify
- Good for basic text replacement
- Works well for small numbers of workflows

### Option 2: Use the Workflow Generator
The project includes a workflow generator script that can help create factories:
```bash
python scripts/generate_workflow_template.py
```

### Option 3: Spreadsheet + Script
1. Create a spreadsheet with your variations
2. Write a script to read the spreadsheet
3. Generate workflows for each row

## Best Practices

### Keep It Simple
- Start with just one or two variables
- Use clear placeholder names like `{SERVER_NAME}`
- Test with a small number of workflows first

### Use Good Names
- Make placeholder names obvious: `{DEPARTMENT}` not `{D}`
- Use consistent naming patterns
- Document what each placeholder does

### Validate Your Output
- Check that generated workflows are valid JSON
- Test a few generated workflows manually
- Make sure all placeholders get replaced

## Common Mistakes

### Don't:
- Try to make one factory do too many different things
- Use confusing placeholder names
- Forget to test the generated workflows
- Make the template too complex

### Do:
- Start simple and add complexity gradually
- Use descriptive placeholder names
- Test each generated workflow
- Document how to use your factory

## Getting Started

### Step 1: Identify the Pattern
Look at workflows you want to create and find what's the same and what's different.

### Step 2: Create a Template
Take one workflow and replace the different parts with placeholders.

### Step 3: Write a Simple Script
Create a script that replaces the placeholders with real values.

### Step 4: Test and Improve
Generate a few workflows and test them. Fix any issues and improve the template.

## Example Factory Script

Here's a complete simple example:

```python
import json

def create_department_workflows():
    # Template workflow
    template = {
        "workflow_id": "contrib.dept.{dept_id}",
        "workflow_name": "{dept_name} Analysis",
        "description": "Analysis workflow for {dept_name} department",
        "core_phases": {
            "analyze": {
                "name": "Analyze {dept_name} Data",
                "tasks": {
                    "search": {
                        "search_query": "index=hr department=\"{dept_name}\""
                    }
                }
            }
        }
    }

    # Departments to create workflows for
    departments = [
        {"dept_id": "sales", "dept_name": "Sales"},
        {"dept_id": "marketing", "dept_name": "Marketing"},
        {"dept_id": "engineering", "dept_name": "Engineering"}
    ]

    # Generate workflows
    for dept in departments:
        # Convert template to string and replace placeholders
        workflow_str = json.dumps(template, indent=2)
        for key, value in dept.items():
            workflow_str = workflow_str.replace(f"{{{key}}}", value)

        # Save the workflow
        filename = f"analysis_{dept['dept_id']}.json"
        with open(filename, 'w') as f:
            f.write(workflow_str)

        print(f"Created {filename}")

# Run the factory
create_department_workflows()
```

This creates three workflow files ready to use!

## Need Help?

- Start with the simple examples above
- Look at existing workflows for patterns
- Ask in community discussions for specific factory ideas
- Check the workflow generator script for more advanced features
