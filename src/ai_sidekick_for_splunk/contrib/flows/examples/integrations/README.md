# Simple Integration Examples

This directory shows you how to connect Splunk workflows with external systems and APIs.

## What is Integration?

Integration means connecting your Splunk workflow with other systems to get more information or do additional tasks.

## Available Examples

### Simple API Example (`simple_api_example.json`)
- **What it does**: Gets IP addresses from Splunk, then uses an external API to find their locations
- **Difficulty**: Intermediate
- **What you learn**: How to combine Splunk data with external APIs
- **Note**: You need to create a custom agent for the API calls

## How Integration Works

```
Splunk Data → Get Information → External API → Combine Results → Final Report
```

### Example Flow:
1. **Get Data from Splunk**: Find IP addresses in web logs
2. **Call External API**: Look up location for each IP address
3. **Combine Results**: Put Splunk data and API results together
4. **Create Report**: Make a useful report with both pieces of information

## Common Integration Types

### 1. Data Enrichment
- Get basic data from Splunk
- Add more information from external sources
- Example: IP addresses → location information

### 2. Notifications
- Detect something in Splunk
- Send alerts to external systems
- Example: Security alert → Slack message

### 3. Automation
- Find issues in Splunk
- Trigger actions in other systems
- Example: Server problem → Create ticket

## Creating Your Own Integration

### Step 1: Plan Your Integration
- What data do you want from Splunk?
- What external system will you connect to?
- What should the final result look like?

### Step 2: Create Custom Agent (if needed)
Many integrations need a custom agent to talk to external systems. This agent handles:
- API authentication
- Making API calls
- Processing responses
- Error handling

### Step 3: Design Your Workflow
- Phase 1: Get data from Splunk
- Phase 2: Call external system
- Phase 3: Combine and report results

## Simple Integration Tips

### Start Small
- Begin with one external API call
- Test each step separately
- Add complexity gradually

### Handle Errors
- What if the API is down?
- What if you get no results?
- Always have a backup plan

### Keep It Simple
- Don't try to integrate with too many systems at once
- Focus on one clear business goal
- Make sure the integration adds real value

## Popular APIs for Learning

### Free APIs (good for testing):
- **ipapi.co** - Get location from IP address
- **httpbin.org** - Test HTTP requests
- **jsonplaceholder.typicode.com** - Fake data for testing

### Business APIs:
- **Slack** - Send messages and notifications
- **ServiceNow** - Create tickets and tasks
- **PagerDuty** - Send alerts and escalations

## Security Notes

- Never put API keys directly in workflow files
- Use environment variables for sensitive information
- Always validate data before sending to external systems
- Be careful with rate limits (don't call APIs too often)

## Need Help?

- Start with the simple API example
- Check the templates for basic structure
- Look at existing integrations in your organization
- Ask in community discussions for specific API help
