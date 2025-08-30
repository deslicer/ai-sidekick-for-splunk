# AI Sidekick for Splunk

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-1.11+-green.svg)](https://google.github.io/adk-docs/)

**AI Sidekick for Splunk** is a powerful multi-agent system that brings AI-powered assistance to Splunk operations. Built on Google's Agent Development Kit (ADK), it provides intelligent automation for Splunk administration, troubleshooting, and data analysis.

## 🚀 Features

### **Multi-Agent Architecture**
- **FlowPilot Agents**: Template-driven workflow execution for systematic operations
- **Specialized Agents**: Purpose-built agents for specific Splunk tasks
- **Result Synthesizer**: Converts technical results into actionable business insights
- **Dynamic Discovery**: Automatically discovers and registers new workflows

### **Workflow-Driven Operations**
- **System Health Checks**: Comprehensive Splunk environment monitoring
- **Index Analysis**: Deep-dive analysis of data ingestion and performance
- **Performance Monitoring**: Real-time system performance insights
- **Extensible Framework**: Easy addition of custom workflows via JSON templates

### **Enterprise-Ready**
- **Scalable Architecture**: Supports both community and enterprise workflows
- **MCP Integration**: Model Context Protocol for seamless tool integration
- **Web Interface**: Modern web UI powered by Google ADK
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 📋 Prerequisites

- **Python 3.11+**
- **Google API Key** (for Gemini models)
- **Splunk Environment** (for MCP server connectivity)
- **uv** (Fast Python package manager)

## 🛠️ Quick Start

### 1. **Check Prerequisites**

```bash
# Download and run the prerequisites checker
curl -O https://raw.githubusercontent.com/your-org/ai-sidekick-for-splunk/main/scripts/check-prerequisites.py
python check-prerequisites.py
```

### 2. **Install AI Sidekick**

```bash
# Install from PyPI (when available)
pip install ai-sidekick-for-splunk

# Or install from source
git clone https://github.com/your-org/ai-sidekick-for-splunk.git
cd ai-sidekick-for-splunk
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### 3. **Set Up Environment**

```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with your Google API key and Splunk MCP server URL
```

### 4. **Start AI Sidekick**

```bash
ai-sidekick
```

Open your browser to `http://localhost:8087` and start interacting with your AI agents!

## 🎯 Usage Examples

### **System Health Check**
```
Ask: "Run a comprehensive health check on my Splunk environment"
```
The FlowPilot agent will execute a systematic health check workflow, analyzing:
- System information and version details
- Index status and data flow
- Performance metrics
- Actionable recommendations

### **Index Analysis**
```
Ask: "Analyze the performance of my main index"
```
Get detailed insights into:
- Data ingestion rates
- Storage utilization
- Search performance
- Optimization suggestions

### **Custom Workflows**
Create your own workflows by adding JSON templates to the `src/core/flows/` or `src/contrib/flows/` directories.

## 🏗️ Architecture

```
AI Sidekick for Splunk
├── Core Agents
│   ├── FlowPilot (Universal workflow executor)
│   ├── Result Synthesizer (Business insights)
│   └── Splunk MCP (Splunk operations)
├── Workflow Engine
│   ├── Dynamic Discovery
│   ├── Template Validation
│   └── Execution Orchestration
└── Extensible Framework
    ├── Core Workflows (Built-in)
    └── Contrib Workflows (Community)
```

## 🔧 Development

### **Adding Custom Agents**

```bash
# Create a new agent
ai-sidekick-create-agent my_custom_agent

# Add implementation
ai-sidekick-add-agent my_custom_agent
```

### **Creating Workflow Templates**

```bash
# Generate a workflow template
python src/scripts/generate_workflow_template.py
```

### **Running Tests**

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/
```

## 📚 Documentation

- **[Getting Started Guide](docs/getting-started/)**
- **[Agent Development](docs/development/)**
- **[Workflow Templates](docs/workflows/)**
- **[API Reference](docs/api/)**

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### **Quick Contribution Steps**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google ADK Team** - For the powerful Agent Development Kit
- **Splunk Community** - For inspiration and feedback
- **Contributors** - For making this project better

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/ai-sidekick-for-splunk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/ai-sidekick-for-splunk/discussions)
- **Documentation**: [Project Wiki](https://github.com/your-org/ai-sidekick-for-splunk/wiki)

---

**Made with ❤️ for the Splunk Community**
