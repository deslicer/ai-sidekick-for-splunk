# Creating MCP Agents from Configurations

This guide explains how to create custom MCP (Model Context Protocol) agents using the `create_mcp_agents.py` script. This allows you to automatically generate agents that integrate with any MCP server.

## Overview

The MCP agent creation system allows you to:
- ✅ **Generate agents from MCP server configurations**
- ✅ **Automatically discover and document available tools**
- ✅ **Create production-ready agents with full callback support**
- ✅ **Integrate seamlessly with the AI Sidekick orchestrator**

## Quick Start

### 1. Create MCP Configuration

Create a `mcp.json` file with your MCP server configurations:

```json
{
  "mcpServers": {
    "Firecrawl": {
      "command": "env",
      "args": [
        "FIRECRAWL_API_KEY=your_api_key",
        "npx",
        "-y", 
        "firecrawl-mcp"
      ],
      "timeout": 120.0
    },
    "GitHub": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
      }
    },
    "MyHTTPServer": {
      "url": "https://my-mcp-server.com/mcp",
      "headers": {
        "Authorization": "Bearer your_token"
      }
    }
  }
}
```

### 2. Generate Agents

```bash
# Generate agents and save to disk
uv run python src/ai_sidekick_for_splunk/cli/create_mcp_agents.py -c mcp.json --save

# Override existing agents if they exist
uv run python src/ai_sidekick_for_splunk/cli/create_mcp_agents.py -c mcp.json --save --override

# Test connections without creating agents
uv run python src/ai_sidekick_for_splunk/cli/create_mcp_agents.py -c mcp.json --test-only
```

### 3. Use Generated Agents

After generation, agents are automatically discovered by the orchestrator:

```bash
# Restart AI Sidekick to discover new agents
uv run ai-sidekick --stop
uv run ai-sidekick --start

# Access at http://localhost:8087
```

## Configuration Options

### MCP Server Types

#### **Stdio Servers (Local Processes)**
```json
{
  "ServerName": {
    "command": "npx",
    "args": ["-y", "my-mcp-server"],
    "env": {
      "API_KEY": "your_key"
    },
    "timeout": 60.0
  }
}
```

#### **HTTP Servers (Remote)**
```json
{
  "ServerName": {
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer token"
    }
  }
}
```

### Timeout Configuration

- **Default**: 60 seconds for all connections
- **Customizable**: Add `"timeout": 120.0` to any server in mcp.json
- **Post-generation**: Edit timeout in generated `agent.py` files

```python
# In generated agent.py
self.connection_params = StdioConnectionParams(
    # ... other params ...
    timeout=120.0,  # Increase for slow operations
)
```

## Command Line Options

### Basic Usage
```bash
uv run python src/ai_sidekick_for_splunk/cli/create_mcp_agents.py [options]
```

### Options

| Option | Description | Example |
|--------|-------------|---------|
| `-c, --config` | Path to mcp.json | `-c my_servers.json` |
| `--save` | Save agents to disk | `--save` |
| `--override` | Replace existing agents | `--override` |
| `--test-only` | Test connections only | `--test-only` |
| `--quiet, -q` | Reduce output verbosity | `--quiet` |

### Environment Variables

| Variable | Description | Values |
|----------|-------------|--------|
| `LOG_LEVEL` | Set logging level | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

## Generated Agent Structure

Each generated agent follows this structure:

```
src/ai_sidekick_for_splunk/contrib/agents/server_name_agent/
├── __init__.py          # Agent exports
├── agent.py             # Main agent class with callbacks
├── prompt.py            # Enhanced prompt with discovered tools
└── README.md            # Usage documentation
```

### Agent Features

Generated agents include:

- ✅ **Full callback support** for observability
- ✅ **Automatic tool discovery** and documentation
- ✅ **Enhanced prompts** with tool catalogs
- ✅ **Timeout configuration** and error handling
- ✅ **Seamless orchestrator integration**

## Advanced Usage

### Custom Prompts

Agents are generated with enhanced prompts that include discovered tools:

```python
# Base prompt + discovered tools
AGENT_PROMPT = """
# Generic MCP Agent
You are an MCP tool executor...

## Available Tools (Discovered 6 tools from MCP Server)
- **firecrawl_scrape**: Scrape a website and extract its content
- **firecrawl_crawl**: Crawl a website and extract content from multiple pages
...
"""
```

### Callback Customization

Generated agents include callback methods that you can customize:

```python
def before_tool_callback(self, tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[Dict]:
    """Log and optionally modify tool arguments before execution."""
    # Add custom validation or argument modification here
    return None

def after_tool_callback(self, tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Any) -> Optional[Any]:
    """Log and optionally modify tool response after execution."""
    # Add custom response processing or validation here
    return None
```

### Connection Parameter Customization

Modify connection parameters in generated agents:

```python
# For stdio connections
self.connection_params = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="your_command",
        args=["arg1", "arg2"],
        env={"DEBUG": "1"}
    ),
    terminate_on_close=True,
    timeout=120.0,  # Adjust as needed
)

# For HTTP connections  
self.connection_params = StreamableHTTPConnectionParams(
    url="https://your-server.com/mcp",
    headers={"Authorization": "Bearer token"},
    timeout=15.0,
    sse_read_timeout=300.0,
)
```

## Troubleshooting

### Common Issues

**Connection Timeouts:**
```bash
# Increase timeout in mcp.json
{
  "ServerName": {
    "command": "...",
    "timeout": 120.0
  }
}

# Or edit generated agent.py after creation
```

**Tool Discovery Issues:**
```bash
# Test connection first
uv run python src/ai_sidekick_for_splunk/cli/create_mcp_agents.py -c mcp.json --test-only

# Check MCP server logs for errors
```

**Agent Not Discovered:**
```bash
# Verify agent structure
ls src/ai_sidekick_for_splunk/contrib/agents/your_agent/

# Restart orchestrator
uv run ai-sidekick --stop
uv run ai-sidekick --start
```

**Import Errors:**
```bash
# Check generated agent imports
python -c "from src.ai_sidekick_for_splunk.contrib.agents.your_agent import YourAgent"
```

### Logging and Debugging

**Enable Debug Logging:**
```bash
# Set LOG_LEVEL in .env
echo "LOG_LEVEL=DEBUG" >> .env

# Or use command-line override
LOG_LEVEL=DEBUG uv run python src/ai_sidekick_for_splunk/cli/create_mcp_agents.py -c mcp.json --save
```

**Quiet Mode:**
```bash
# Reduce output for production
uv run python src/ai_sidekick_for_splunk/cli/create_mcp_agents.py -c mcp.json --save --quiet
```

## Best Practices

### Configuration Management

1. **Use descriptive server names** in mcp.json
2. **Set appropriate timeouts** for your use case
3. **Test connections** before generating agents
4. **Version control** your mcp.json configurations

### Agent Customization

1. **Review generated prompts** and customize if needed
2. **Adjust timeouts** based on server performance
3. **Customize callbacks** for specific observability needs
4. **Test agents** before deploying to production

### Production Deployment

1. **Use `--save --override`** for updates
2. **Monitor logs** for timeout or connection issues
3. **Backup configurations** before major changes
4. **Document customizations** for team members

## Examples

### Example 1: Web Scraping Agent
```bash
# Create mcp.json with Firecrawl
echo '{
  "mcpServers": {
    "WebScraper": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "timeout": 180.0
    }
  }
}' > web_scraper.json

# Generate agent
uv run python src/ai_sidekick_for_splunk/cli/create_mcp_agents.py -c web_scraper.json --save
```

### Example 2: GitHub Integration
```bash
# Create mcp.json with GitHub
echo '{
  "mcpServers": {
    "GitHubIntegration": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"],
      "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "your_token"}
    }
  }
}' > github_integration.json

# Generate agent
uv run python src/ai_sidekick_for_splunk/cli/create_mcp_agents.py -c github_integration.json --save
```

## Next Steps

- **Explore Generated Agents**: Review the created agent files
- **Customize Prompts**: Modify prompts for your specific use cases
- **Test Integration**: Use agents through the orchestrator web interface
- **Monitor Performance**: Use callback logs to optimize operations
- **Share Configurations**: Contribute useful MCP configurations to the community

For more information, see the [main documentation](GETTING_STARTED.md) or [project README](../README.md).
