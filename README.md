# AI Sidekick for Splunk

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-1.11+-green.svg)](https://google.github.io/adk-docs/)

**AI Sidekick for Splunk** is a revolutionary multi-agent system that transforms complex Splunk operations into simple, accessible workflows. Built on Google's Agent Development Kit (ADK), it features a sophisticated architecture combining universal workflow agents with specialized intelligent agents.

## 🏗️ **Modern Architecture**

### **FlowPilot System - Universal Workflow Execution**

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Sidekick for Splunk                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   FlowPilot     │  │  Specialized    │  │ Auto-Discovery│ │
│  │   Agents        │  │    Agents       │  │    System    │ │
│  │                 │  │                 │  │              │ │
│  │ • Universal     │  │ • Result        │  │ • Workflow   │ │
│  │ • Template-     │  │   Synthesizer   │  │   Scanner    │ │
│  │   Driven        │  │ • Splunk MCP    │  │ • Validation │ │
│  │ • JSON Config   │  │ • Researcher    │  │ • Dynamic    │ │
│  │ • Scalable      │  │ • Custom Agents │  │   Factory    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Workflow Engine                         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ • Dynamic Discovery  • Pydantic Validation             │ │
│  │ • Template Engine    • Parallel Execution              │ │
│  │ • Agent Coordination • Result Synthesis                │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **Core Components**

1. **🚀 FlowPilot Agents**: Universal agents that execute any JSON-defined workflow
2. **🎯 Specialized Agents**: Purpose-built agents for complex operations
3. **🔍 Auto-Discovery**: Automatically finds and registers workflows from `core/` and `contrib/`
4. **⚡ Workflow Engine**: Orchestrates multi-agent workflows with parallel execution

### **Active Agents**

- **🔍 SplunkMCP**: Core agent for Splunk search operations and data retrieval
- **🎯 SearchGuru**: Advanced search query optimization and analysis
- **📊 ResultSynthesizer**: Intelligent result aggregation and business insights
- **⚡ FlowPilot**: Universal workflow execution engine for JSON-defined workflows

> **Note**: Additional experimental agents can be enabled/disabled via the `disabled` flag in agent metadata for safe experimentation.

## ✨ **Key Features**

### **Template-Driven Workflows**
- **JSON Configuration**: Define workflows without code changes
- **Dynamic Discovery**: Automatically discovers workflows in `core/flows/` and `contrib/flows/`
- **Pydantic Validation**: Robust schema validation for workflow templates
- **Hot Reload**: Add new workflows without restarting the system

### **Multi-Agent Orchestration**
- **FlowPilot Factory**: Dynamically creates agents from workflow templates
- **Agent Dependencies**: Declare required agents (e.g., `splunk_mcp`, `result_synthesizer`)
- **Parallel Execution**: Execute multiple tasks simultaneously
- **Result Synthesis**: Convert technical results into business insights

### **Enterprise-Ready Architecture**
- **Hybrid Model**: Core workflows (stable) + Community workflows (experimental)
- **Scalable Naming**: Generic task-based execution patterns
- **MCP Integration**: Model Context Protocol for seamless tool integration
- **Web Interface**: Web UI powered by Google ADK

### **Multi-Model Support**
- **Multiple Providers**: Google Gemini, OpenAI GPT, Anthropic Claude, Azure OpenAI
- **Agent-Specific Models**: Different models for different agents (e.g., Claude for code analysis, GPT-4 for reasoning)
- **Cost Optimization**: Use cheaper models for simple tasks, premium models for complex analysis
- **Auto-Detection**: Automatically routes to appropriate provider based on model name
- **Easy Configuration**: Simple environment variables to configure models per agent

## 🚀 **Quick Start**

### **1. Clone Repository**

```bash
git clone https://github.com/deslicer/ai-sidekick-for-splunk.git
cd ai-sidekick-for-splunk
```

### **2. Install Prerequisites**

**macOS/Linux:**
```bash
./scripts/smart-install.sh
```

**Windows:**
```powershell
.\scripts\smart-install.ps1
```

**Cross-Platform (Python):**
```bash
python scripts/smart-install.py
```

This will:
- ✅ Install `uv` (fast Python package manager) - handles Python automatically
- ✅ Create virtual environment and install dependencies using `uv sync`
- ✅ Verify Git installation and install if needed
- ✅ Complete environment setup in one step

### **3. Start AI Sidekick**

> **💡 Great news!** The prerequisite scripts have already created your virtual environment and installed all dependencies. You can start immediately!

```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Configure environment (copy and edit examples/env.example)
cp examples/env.example .env
# Edit .env with your API keys and model preferences
```

```bash
# Start the system
uv run ai-sidekick --start
```

Open `http://localhost:8087` and start using your AI agents!

## ⚙️ **Multi-Model Configuration**

AI Sidekick supports multiple LLM providers for optimal performance and cost efficiency:

### **Basic Setup (Gemini Only)**
```bash
# Simplest configuration - just add your Google API key
GOOGLE_API_KEY=your_gemini_api_key_here
```

### **OpenAI GPT Models**
```bash
# Use GPT-4 for all agents
MODEL_PROVIDER=litellm
BASE_MODEL=gpt-4
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### **Anthropic Claude Models**
```bash
# Use Claude for all agents
MODEL_PROVIDER=litellm
BASE_MODEL=claude-3-sonnet
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
```

### **Azure OpenAI**
```bash
# Use Azure-hosted GPT models
MODEL_PROVIDER=litellm
BASE_MODEL=gpt-4
AZURE_API_KEY=your-azure-api-key
AZURE_API_BASE=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2023-12-01-preview
```

### **Mixed Models (Recommended)**
```bash
# Optimize each agent with the best model for its task
BASE_MODEL=gemini-2.0-flash          # Fast default
ORCHESTRATOR_MODEL=gpt-4             # Best coordination
SEARCH_GURU_MODEL=claude-3-sonnet    # Best code analysis
FLOW_PILOT_MODEL=gpt-4               # Best workflows
SPLUNK_MCP_MODEL=gemini-2.0-flash    # Fast tool execution

# Add required API keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
```

### **Check Available Models**
```bash
# See which models are configured and available
uv run ai-sidekick --list-models
```

## 💡 **Usage Examples**

### **🚀 Quick Start - Using Built-in Templates**

Create workflow agents using curated, stable templates:

```bash
# Health monitoring workflow
ai-sidekick --create-flow-agent health_monitor --template simple_health_check

# Security analysis workflow  
ai-sidekick --create-flow-agent security_check --template security_audit

# Data quality assessment workflow
ai-sidekick --create-flow-agent data_quality --template data_quality_check
```

### **🎯 Advanced - Using Custom Templates**

Create workflows from your own YAML templates:

```bash
# Use your custom template file
ai-sidekick --create-flow-agent my_workflow --template-file my_custom_template.yaml

# Use template from specific path
ai-sidekick --create-flow-agent analysis --template-file /path/to/custom_workflow.yaml
```

### **🚨 FlowPilot Requirements**

**All FlowPilot workflows require:**
- ✅ **Minimum 2 searches** (for micro agent creation)
- ✅ **Parallel execution** (sequential not supported)  
- ✅ **Automatic agent assignment** (`"agent": "splunk_mcp"`)

**Templates automatically enforce these requirements and show helpful error messages if violated.**

### **🛠️ Template Creation & Validation**

Create and validate your own templates:

```bash
# Create a new template interactively
ai-sidekick --create-template

# Create template based on existing example
ai-sidekick --create-template --from-example simple_health_check

# Validate your YAML template before use
ai-sidekick --validate-template my_template.yaml

# Validate workflow JSON files (for advanced users)
ai-sidekick --validate-workflow my_workflow.json --verbose
```

### **🔧 System Management**

```bash
# Start the AI Sidekick system
ai-sidekick --start

# Stop the system
ai-sidekick --stop
```

### **📋 Workflow Examples in Action**

Once your agents are created and the system is running, interact through the web interface:

#### **System Health Check**
```
User: "Run a comprehensive health check on my Splunk environment"

FlowPilot Agent:
├── Phase 1: System Information Gathering
├── Phase 2: Health Assessment  
├── Phase 3: Performance Analysis
└── Phase 4: Summary Report (via Result Synthesizer)
```

#### **Data Quality Analysis**
```
User: "Check data quality issues in my environment"

FlowPilot Agent:
├── Analyze data ingestion patterns
├── Check for missing data sources
├── Validate data consistency
└── Generate quality improvement recommendations
```

## 🏗️ **Architecture Deep Dive**

### **Workflow Discovery System**
```python
# Automatic discovery from:
src/ai_sidekick_for_splunk/
├── core/flows/           # Stable, production workflows
│   ├── health_check/
│   ├── index_analysis/
│   └── system_info/
└── contrib/flows/        # Community, experimental workflows
    ├── security/
    ├── performance/
    └── custom/
```

### **FlowPilot Agent Factory**
```python
# Dynamic agent creation
discovery = WorkflowDiscovery()
workflows = discovery.discover_workflows()

factory = DynamicFlowPilotFactory()
agents = factory.create_all_flow_pilot_agents()
# Creates: System Health Check, Index Analysis, etc.
```

### **Agent Dependencies**
```json
{
  "agent_dependencies": {
    "splunk_mcp": {
      "agent_id": "splunk_mcp",
      "required": true,
      "description": "Splunk MCP server for data operations"
    },
    "result_synthesizer": {
      "agent_id": "result_synthesizer",
      "required": false,
      "description": "Converts technical results to business insights"
    }
  }
}
```

## 🛠️ **Development**

### **Creating Workflow Agents**

```bash
# Create a new FlowPilot workflow agent (generic)
ai-sidekick --create-flow-agent my_custom_workflow

# Create using built-in template
ai-sidekick --create-flow-agent health_check --template simple_health_check

# Create from custom template file
ai-sidekick --create-flow-agent my_workflow --template-file custom.yaml

# Restart to discover new workflow
ai-sidekick --stop
ai-sidekick --start

# Test your workflow in ADK Web interface
# Visit: http://localhost:8087
```

### **Template Development**

```bash
# Create new template interactively
ai-sidekick --create-template

# Validate template before use
ai-sidekick --validate-template my_template.yaml

# Validate workflow JSON (advanced)
ai-sidekick --validate-workflow workflow.json --verbose
```

### **Testing & Quality**

```bash
# Run tests
pytest

# Code quality
ruff check src/
ruff format src/

# Type checking
mypy src/
```

## 📁 **Project Structure**

```
src/ai_sidekick_for_splunk/
├── core/
│   ├── agents/              # Core agents
│   │   ├── flow_pilot/      # Universal workflow agent
│   │   ├── result_synthesizer/
│   │   └── splunk_mcp/
│   ├── flows/               # Core workflow templates
│   │   ├── health_check/
│   │   ├── index_analysis/
│   │   └── system_info/
│   └── flows_engine/        # Workflow execution engine
├── contrib/
│   ├── agents/              # Community agents
│   └── flows/               # Community workflows
├── cli/                     # Command-line interface
└── services/                # Supporting services
```

## 🌟 **Why AI Sidekick for Splunk?**

### **For Splunk Administrators**
- **Instant Expertise**: Access to best-practice workflows
- **Reduced Complexity**: Complex operations simplified to conversations
- **Consistent Results**: Standardized, repeatable processes
- **Time Savings**: Automated routine tasks

### **For Developers**
- **Template-Driven**: Add workflows without coding
- **Extensible Architecture**: Build on solid foundations
- **Community Driven**: Share and benefit from collective knowledge
- **Modern Stack**: Built on Google ADK with latest AI capabilities

### **For Organizations**
- **Scalable Operations**: Handle growing Splunk environments
- **Knowledge Preservation**: Capture expertise in reusable workflows
- **Compliance Ready**: Consistent, auditable processes
- **Cost Effective**: Reduce manual operations overhead

## 🤝 **Contributing**

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### **Quick Contribution**
1. Fork the repository
2. Create a workflow template in `contrib/flows/`
3. Test with the workflow generator
4. Submit a Pull Request

## 📚 **Documentation**

- **[Architecture Guide](docs/architecture/)** - Deep dive into system design
- **[Workflow Templates](docs/workflows/)** - Template creation guide
- **[Agent Development](docs/development/)** - Custom agent development

## 🔗 **Related Projects**

- **[MCP Server for Splunk](https://github.com/deslicer/mcp-for-splunk)** - Splunk MCP integration
- **[Google ADK](https://google.github.io/adk-docs/)** - Agent Development Kit

## 📄 **License**

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

**Transform your Splunk operations with AI-powered workflows** 🚀
