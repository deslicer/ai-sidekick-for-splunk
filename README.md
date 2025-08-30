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

## 🚀 **Quick Start**

### **1. Prerequisites Check**

```bash
# Download and run prerequisites checker
curl -O https://raw.githubusercontent.com/your-org/ai-sidekick-for-splunk/main/scripts/check-prerequisites.py
python check-prerequisites.py
```

### **2. Installation**

```bash
# Minimal installation (recommended)
pip install ai-sidekick-for-splunk

# With web interface
pip install ai-sidekick-for-splunk[web]

# For development
pip install ai-sidekick-for-splunk[dev]

# From source
git clone https://github.com/your-org/ai-sidekick-for-splunk.git
cd ai-sidekick-for-splunk
uv venv && source .venv/bin/activate
uv pip install -e .
```

### **3. Configuration**

```bash
# Copy environment template
cp .env.example .env

# Edit with your settings
# GOOGLE_API_KEY=your_gemini_api_key
# SPLUNK_MCP_SERVER_URL=http://localhost:8003
```

### **4. Start AI Sidekick**

```bash
ai-sidekick
```

Open `http://localhost:8087` and start using your AI agents!

## 💡 **Usage Examples**

### **System Health Check**
```
User: "Run a comprehensive health check on my Splunk environment"

FlowPilot Agent:
├── Phase 1: System Information Gathering
├── Phase 2: Health Assessment
├── Phase 3: Performance Analysis
└── Phase 4: Summary Report (via Result Synthesizer)
```

### **Index Analysis**
```
User: "Analyze the performance of my main index"

FlowPilot Agent:
├── Gather index metadata
├── Analyze data ingestion patterns
├── Check storage utilization
└── Generate optimization recommendations
```

### **Custom Workflows**
Add your own workflows by creating JSON templates:

```json
{
  "workflow_name": "Security Audit",
  "workflow_id": "security.audit",
  "workflow_type": "security",
  "source": "contrib",
  "core_phases": {
    "scan": {
      "name": "Security Scan",
      "tasks": [
        {
          "task_id": "check_failed_logins",
          "title": "Check Failed Login Attempts",
          "tool": "search",
          "prompt": "Search for failed login attempts in the last 24 hours"
        }
      ]
    }
  }
}
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

### **Creating Custom Agents**

```bash
# Generate agent boilerplate
ai-sidekick-create-agent my_custom_agent

# Add implementation
ai-sidekick-add-agent my_custom_agent
```

### **Creating Workflow Templates**

```bash
# Generate workflow template
python src/ai_sidekick_for_splunk/scripts/generate_workflow_template.py

# Choose core or contrib
# Fill in workflow details
# Template automatically validated
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
