# Contributing to AI Sidekick for Splunk

Welcome to the AI Sidekick for Splunk project! 🎉 We're excited to have you contribute to our open-source community of AI agents for Splunk operations.

## 🚀 Getting Started for Contributors

**Want to create an AI agent quickly?** Here's the streamlined process:

```bash
# 1. Fork and clone
git clone https://github.com/your-username/ai-sidekick-for-splunk.git
cd ai-sidekick-for-splunk

# 2. Set up development environment
./scripts/smart-install.sh  # Checks prerequisites and installs if needed
./scripts/lab/setup-env.sh           # Interactive setup with API keys
./scripts/lab/start-lab-setup.sh     # Start the lab environment

# 3. Create your agent (3-step process)
./scripts/agent/create-agent.sh my_awesome_agent "Analyzes awesome data patterns"
./scripts/agent/add-agent.sh my_awesome_agent
./scripts/agent/integrate-agent.sh my_awesome_agent

# 4. Test your agent
./scripts/lab/restart-lab-setup.sh   # Restart to load your agent
# Visit http://localhost:8087 to test your agent

# 5. Add tests and documentation
# Add unit tests for your agent
# Update documentation with usage examples

# 6. Submit PR
git checkout -b feature/my-awesome-agent
git add . && git commit -m "feat: add awesome data pattern analysis agent"
git push origin feature/my-awesome-agent
```

**🎯 Result**: You'll have a fully functional, discoverable AI agent integrated with the orchestrator in minutes!

## 📋 Essential Information

### Prerequisites
- **Python 3.11+** (required for Google ADK)
- **Git** for version control
- **At least one AI API key** (Google AI Studio recommended for beginners)

### Getting AI API Keys
**🥇 Google AI Studio (Recommended)**
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in → "Get API Key" → "Create API Key"
3. Add to your `.env`: `GOOGLE_API_KEY=your_key_here`

**Other Options**: OpenAI, Anthropic Claude, or local LLMs (Ollama)

### Agent Development Workflow
1. **Generate Structure**: `./scripts/agent/create-agent.sh agent_name "description"`
2. **Add Implementation**: `./scripts/agent/add-agent.sh agent_name`
3. **Integrate**: `./scripts/agent/integrate-agent.sh agent_name`

### Testing Your Agent
```bash
# 1. Verify discovery
uv run python main.py  # Look for "Discovered agent: your_agent"

# 2. Test via web interface
./scripts/lab/start-lab-setup.sh
# Visit http://localhost:8087

# 3. Test with sample queries
"analyze index=pas"
"optimize this SPL query"
```

## 📚 Detailed Documentation

For comprehensive guides, architecture details, and advanced topics, see our **[Documentation](docs/README.md)**:

- **[Getting Started Guide](docs/getting-started/README.md)** - Detailed setup and first agent
- **[Agent Development Guide](docs/development/README.md)** - Advanced patterns and best practices
- **[Architecture Overview](docs/architecture/README.md)** - System design and patterns
- **[Examples](docs/examples/README.md)** - Working code samples
- **[API Reference](docs/reference/api.md)** - Complete API documentation

## 🎯 What to Contribute

### 🔥 High-Priority Needs
- **Security & Compliance Agents** (threat hunting, compliance monitoring)
- **Performance & Cost Optimization** (license optimization, search tuning)
- **Data Quality & Governance** (validation, parsing optimization)
- **Operational Intelligence** (monitoring, capacity planning)

### 🌱 Good First Contributions
- **Log Pattern Analyzer** - Identify common error patterns
- **Field Analyzer** - Analyze field usage patterns
- **Dashboard Helper** - Suggest dashboard panels
- **Error Categorizer** - Categorize and count error types

## 🚀 Submitting Changes

### Pull Request Process
1. **Create feature branch**: `git checkout -b feature/descriptive-name`
2. **Test thoroughly**: Ensure agent discovery and functionality work
3. **Use conventional commits**: `feat:`, `fix:`, `docs:`, `perf:`
4. **Update documentation**: Add usage examples and any new requirements
5. **Create PR**: Use our [Pull Request Template](.github/pull_request_template.md) for consistency

### PR Checklist
- [ ] Agent discovered successfully during startup
- [ ] Agent responds correctly to test queries
- [ ] Agent integrates properly with orchestrator
- [ ] Web interface shows agent in list
- [ ] **Tests added** for new functionality
- [ ] **Documentation updated** with usage examples
- [ ] Code follows project standards and passes linting

## 🤝 Community Guidelines

We are committed to providing a welcoming and inclusive environment for all contributors. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

### Core Values
- **Be respectful**: Treat everyone with kindness and respect
- **Be constructive**: Provide helpful feedback and suggestions
- **Be collaborative**: Work together towards common goals
- **Be patient**: Remember that everyone is learning
- **Be inclusive**: Welcome contributors from all backgrounds and experience levels

## 💬 Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community chat
- **Documentation**: Check [docs/](docs/README.md) for comprehensive guides
- **Examples**: Look at existing agents for patterns and inspiration

## 🐛 Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use our issue templates** for consistent reporting:
   - [🐛 Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) - Report a bug or problem
   - [✨ Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) - Suggest a new feature
3. **Provide complete information** as requested in the templates
4. **Security issues**: Please report security vulnerabilities privately to security@deslicer.com (see [Security Policy](SECURITY.md))

## 🏛️ Project Governance

This project follows open-source governance principles. For details on decision-making processes, maintainer responsibilities, and community roles, see our [Project Governance Guide](GOVERNANCE.md).

---

## 🎉 Ready to Contribute?

### New Contributors
Start with a **Log Pattern Analyzer** or **Field Analyzer** agent to learn the patterns and get familiar with the codebase.

### Experienced Developers
Jump into **Security** or **Performance** agents based on your expertise, or tackle **Advanced Challenges** if you have ML experience.

### Domain Experts
Bring your **industry knowledge** (healthcare, finance, e-commerce) and create **specialized agents** for your domain.

---

**Thank you for making AI Sidekick for Splunk better!** 🚀

Your contributions help Splunk community to work more efficiently and make better data-driven decisions.

**Questions?** Check our [Documentation](docs/README.md) or ask in [GitHub Discussions](https://github.com/deslicer/ai-sidekick-for-splunk/discussions)!
