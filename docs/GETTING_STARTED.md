# Getting Started with AI Sidekick for Splunk

This guide will help you set up AI Sidekick for Splunk for development or contribution.

## Prerequisites

- Git (will be checked and installed if needed)
- Internet connection for downloading dependencies
- Google API key (Gemini) or OpenAI API key

## Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/deslicer/ai-sidekick-for-splunk.git
cd ai-sidekick-for-splunk
```

### 2. Run Prerequisites Check

**macOS/Linux:**
```bash
./scripts/lab/check-prerequisites.sh
```

**Windows (PowerShell):**
```powershell
.\scripts\lab\check-prerequisites.ps1
```

**Cross-Platform (Python):**
```bash
python scripts/check-prerequisites.py
```

This will automatically:
- ✅ Install `uv` (fast Python package manager) - handles Python automatically
- ✅ Create virtual environment and install dependencies using `uv sync`
- ✅ Verify Git installation and install if needed
- ✅ Complete environment setup in one step

### 3. Activate Environment

> **💡 Great news!** The prerequisite scripts have already created your virtual environment and installed all dependencies. You can start immediately!

```bash
# Activate virtual environment (if not already active)
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 4. Set Up Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
# Required:
# GOOGLE_API_KEY=your_gemini_api_key_here
# 
# Optional:
# SPLUNK_MCP_SERVER_URL=http://localhost:8003
```

### 5. Verify Installation

```bash
# Test CLI installation
uv run ai-sidekick --help

# Test Python package import
uv run python -c "import ai_sidekick_for_splunk; print('✅ Package imported successfully')"
```

### 6. Start AI Sidekick

```bash
# Start the AI Sidekick system
uv run ai-sidekick --start

# Access web interface at http://localhost:8087
```

## Development Workflow

### Starting the AI Sidekick

```bash
# Start the AI Sidekick (web interface + agents)
uv run ai-sidekick --start

# The web interface will be available at:
# http://localhost:8087
```

### Stopping the AI Sidekick

```bash
# Stop the AI Sidekick
uv run ai-sidekick --stop

# Or use Ctrl+C if running in foreground
```

### Agent Management

AI Sidekick includes several built-in agents for different tasks:

#### **Active Agents**
- **SplunkMCP**: Core agent for Splunk search operations
- **SearchGuru**: Advanced search query optimization and analysis
- **ResultSynthesizer**: Intelligent result aggregation and insights
- **FlowPilot**: Universal workflow execution engine for JSON-defined workflows

#### **Experimental Agent Control**

For developers and contributors, agents can be disabled/enabled for experimentation without breaking the system:

```python
# In agent metadata (e.g., src/ai_sidekick_for_splunk/contrib/agents/my_agent/agent.py)
METADATA = AgentMetadata(
    name="MyExperimentalAgent",
    description="My experimental agent",
    disabled=True,  # Set to False to enable
)
```

**Benefits:**
- **Safe Experimentation**: Disable agents without deleting code
- **Easy Re-enable**: Change `disabled=False` and restart
- **No File Moves**: Code stays in logical locations
- **Clean System**: Disabled agents are skipped during discovery

### Creating Workflow Agents

#### **Using Built-in Templates (Recommended)**

```bash
# Create workflow from curated templates
ai-sidekick --create-flow-agent health_check --template simple_health_check
ai-sidekick --create-flow-agent security_audit --template security_audit
ai-sidekick --create-flow-agent data_quality --template data_quality_check
```

#### **Using Custom Templates**

```bash
# Create workflow from your YAML template
ai-sidekick --create-flow-agent my_workflow --template-file custom_template.yaml
```

#### **Generic Workflow (Advanced)**

```bash
# Create a generic workflow (requires manual JSON editing)
ai-sidekick --create-flow-agent my_new_workflow
```

#### **Restart to Discover New Workflows**

```bash
# Restart to discover the new workflow
ai-sidekick --stop
ai-sidekick --start

# Test in ADK Web interface at http://localhost:8087
```

### Template Development

#### **Creating Templates**

```bash
# Create a new template interactively
ai-sidekick --create-template

# Create template based on existing example
ai-sidekick --create-template --from-example simple_health_check

# Create template in specific directory
ai-sidekick --create-template --template-dir contrib/flows/my_flow
```

#### **Validating Templates and Workflows**

```bash
# Validate YAML template before use
ai-sidekick --validate-template my_template.yaml

# Validate workflow JSON file (advanced users)
ai-sidekick --validate-workflow my_workflow.json

# Validate with detailed information
ai-sidekick --validate-workflow my_workflow.json --verbose

# Validate with minimal output
ai-sidekick --validate-workflow my_workflow.json --quiet
```

### Code Quality Tools

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check --fix

# Type checking
uv run mypy src/

# Run tests
uv run pytest
```

## Project Structure

```
ai-sidekick-for-splunk/
├── src/ai_sidekick_for_splunk/     # Main package
│   ├── core/                      # Core agents and engine
│   │   ├── agents/               # Specialized agents
│   │   └── flows_engine/         # FlowPilot workflow engine
│   ├── contrib/                  # Community contributions
│   │   └── flows/               # Community workflow templates
│   └── cli/                     # Command-line interface
├── scripts/                     # Setup and utility scripts
├── docs/                       # Documentation
└── tests/                      # Test suite
```

## FlowPilot Workflow Development

### Understanding Workflow Templates

FlowPilot workflows are defined by JSON templates with:
- **Metadata**: Name, description, complexity, target audience
- **Phases**: Logical groupings of related tasks
- **Tasks**: Individual operations with tools and prompts
- **Dependencies**: Required agents (splunk_mcp, result_synthesizer)

### Creating Workflow Templates

#### **From Built-in Templates (Recommended)**

```bash
# Use curated, stable templates
ai-sidekick --create-flow-agent security_analysis --template security_audit
ai-sidekick --create-flow-agent health_monitor --template simple_health_check
ai-sidekick --create-flow-agent data_check --template data_quality_check
```

#### **From Custom Templates**

```bash
# Create your own YAML template first
ai-sidekick --create-template

# Then use it to create workflow
ai-sidekick --create-flow-agent my_workflow --template-file my_template.yaml
```

#### **Generic Template (Advanced)**

```bash
# Generate a generic workflow template (requires manual editing)
ai-sidekick --create-flow-agent security_analysis

# This creates:
# - contrib/flows/security_analysis/security_analysis.json
# - contrib/flows/security_analysis/README.md
```

#### **Validation**

```bash
# Validate your templates and workflows
ai-sidekick --validate-template my_template.yaml
ai-sidekick --validate-workflow security_analysis.json --verbose
```

### Workflow Discovery

The system automatically discovers workflows by:
1. Scanning `core/flows/` and `contrib/flows/` directories
2. Validating JSON templates against Pydantic schema
3. Creating FlowPilot agents for valid workflows
4. Registering agents as tools in the orchestrator

### Testing Workflows

```bash
# Restart to discover new workflows
uv run ai-sidekick --stop
uv run ai-sidekick --start

# Test via web interface at http://localhost:8087
# Or test programmatically:
uv run python -c "
from ai_sidekick_for_splunk.core.agents import get_all_agents
agents = get_all_agents()
print([agent.name for agent in agents])
"
```

## Contributing

### Development Guidelines

1. **Follow Conventional Commits**: Use `feat:`, `fix:`, `docs:`, etc.
2. **Test Your Changes**: Run tests and linting before submitting
3. **Update Documentation**: Keep docs in sync with code changes
4. **Use FlowPilot**: Prefer workflow templates over hardcoded agents

### Workflow Contribution Process

1. **Create Workflow**: Use `uv run ai-sidekick --create-flow-agent`
2. **Test Locally**: Verify workflow executes correctly
3. **Document**: Update README.md with workflow description
4. **Submit PR**: Include workflow template and documentation

### Code Contribution Process

1. **Fork Repository**: Create your own fork
2. **Create Branch**: Use descriptive branch names
3. **Make Changes**: Follow coding standards
4. **Test**: Run full test suite
5. **Submit PR**: Include clear description and tests

## Troubleshooting

### Common Issues

**Virtual Environment Issues:**
```bash
# Delete and recreate virtual environment
rm -rf .venv
./scripts/lab/check-prerequisites.sh  # macOS/Linux
# or
.\scripts\lab\check-prerequisites.ps1  # Windows
```

**Dependency Issues:**
```bash
# Force reinstall dependencies
uv sync --reinstall
```

**CLI Not Working:**
```bash
# Reinstall package in development mode
uv pip install -e .
```

**Web Interface Not Loading:**
```bash
# Check if port is in use
lsof -i :8087  # macOS/Linux
netstat -an | findstr :8087  # Windows

# Try different port
uv run ai-sidekick --start --port 8088
```

### Getting Help

1. **Check Logs**: Look for error messages in console output
2. **Verify Environment**: Ensure all prerequisites are installed
3. **Test Components**: Use individual CLI commands to isolate issues
4. **Community Support**: Open an issue on GitHub

## Next Steps

- **Explore Examples**: Check existing workflows in `core/flows/`
- **Create Workflows**: Build your own FlowPilot templates
- **Join Community**: Contribute to the open-source project
- **Deploy Production**: Set up for organizational use

For more detailed information, see the [project documentation](../README.md).