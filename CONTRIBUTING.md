# Contributing to AI Sidekick for Splunk

Thank you for your interest in contributing to AI Sidekick for Splunk! We welcome contributions from the community and are excited to see what you'll build.

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- uv (Fast Python package manager)
- Git
- Google API Key (for testing)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/ai-sidekick-for-splunk.git
   cd ai-sidekick-for-splunk
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install in development mode
   uv pip install -e ".[dev]"
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your development settings
   ```

4. **Verify Setup**
   ```bash
   # Run tests
   pytest
   
   # Check code quality
   ruff check src/
   
   # Start development server
   ai-sidekick
   ```

## 📋 How to Contribute

### 🐛 Reporting Bugs

1. **Check Existing Issues**: Search [existing issues](https://github.com/your-org/ai-sidekick-for-splunk/issues) first
2. **Create Detailed Report**: Include:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Error messages and logs

### 💡 Suggesting Features

1. **Check Discussions**: Look at [GitHub Discussions](https://github.com/your-org/ai-sidekick-for-splunk/discussions)
2. **Create Feature Request**: Include:
   - Clear description of the feature
   - Use case and motivation
   - Proposed implementation (if any)
   - Examples of similar features

### 🔧 Code Contributions

#### **Types of Contributions**

1. **Bug Fixes**: Fix existing issues
2. **New Agents**: Add specialized agents for specific tasks
3. **Workflow Templates**: Create new workflow definitions
4. **Documentation**: Improve guides, examples, and API docs
5. **Tests**: Add or improve test coverage
6. **Performance**: Optimize existing functionality

#### **Development Workflow**

1. **Create Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make Changes**
   - Follow our coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run all tests
   pytest
   
   # Run specific tests
   pytest tests/test_your_feature.py
   
   # Check code quality
   ruff check src/
   ruff format src/
   
   # Type checking
   mypy src/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## 📝 Coding Standards

### **Code Style**

- **Formatter**: Use `ruff format` for consistent formatting
- **Linter**: Use `ruff check` for code quality
- **Type Hints**: Add type hints to all functions and methods
- **Docstrings**: Use Google-style docstrings

### **Commit Messages**

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new workflow template for security analysis
fix: resolve issue with agent discovery
docs: update installation guide
test: add tests for workflow validation
refactor: improve error handling in flow engine
```

### **Code Organization**

```
src/
├── core/                 # Core system components
│   ├── agents/          # Built-in agents
│   ├── flows/           # Core workflow definitions
│   └── flows_engine/    # Workflow execution engine
├── contrib/             # Community contributions
│   ├── agents/          # Community agents
│   └── flows/           # Community workflows
├── cli/                 # Command-line interface
└── services/            # Supporting services
```

### **Testing Guidelines**

- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete workflows
- **Coverage**: Aim for >80% test coverage

```bash
# Test structure
tests/
├── unit/               # Unit tests
├── integration/        # Integration tests
├── e2e/               # End-to-end tests
└── fixtures/          # Test data and fixtures
```

## 🤖 Adding New Agents

### **Creating a New Agent**

1. **Use the Generator**
   ```bash
   ai-sidekick-create-agent my_awesome_agent
   ```

2. **Implement the Agent**
   ```python
   # src/contrib/agents/my_awesome_agent/agent.py
   from google.adk.agents import LlmAgent
   
   def create_my_awesome_agent() -> LlmAgent:
       return LlmAgent(
           name="my_awesome_agent",
           instructions="You are an awesome agent that...",
           # Add your implementation
       )
   ```

3. **Add Tests**
   ```python
   # tests/unit/test_my_awesome_agent.py
   def test_my_awesome_agent():
       agent = create_my_awesome_agent()
       assert agent.name == "my_awesome_agent"
   ```

4. **Update Documentation**
   - Add agent description to README
   - Create usage examples
   - Document any special requirements

### **Agent Best Practices**

- **Clear Purpose**: Each agent should have a specific, well-defined purpose
- **Good Instructions**: Provide clear, detailed instructions to the LLM
- **Error Handling**: Handle errors gracefully and provide helpful messages
- **Documentation**: Include docstrings and usage examples
- **Testing**: Add comprehensive tests

## 📊 Creating Workflow Templates

### **Workflow Structure**

```json
{
  "workflow_name": "My Custom Workflow",
  "workflow_id": "custom.my_workflow",
  "workflow_type": "analysis",
  "workflow_category": "custom",
  "source": "contrib",
  "maintainer": "community",
  "stability": "experimental",
  "complexity_level": "beginner",
  "estimated_duration": "2-5 minutes",
  "version": "1.0.0",
  "description": "Description of what this workflow does",
  "workflow_instructions": {
    "system_prompt": "You are a helpful assistant...",
    "execution_style": "sequential"
  },
  "agent_dependencies": {
    "splunk_mcp": {
      "agent_id": "splunk_mcp",
      "required": true,
      "description": "Splunk MCP server for data operations"
    }
  },
  "core_phases": {
    "analysis": {
      "name": "Analysis Phase",
      "tasks": [
        {
          "task_id": "analyze_data",
          "title": "Analyze Data",
          "tool": "search",
          "prompt": "Analyze the data and provide insights"
        }
      ]
    }
  }
}
```

### **Workflow Best Practices**

- **Modular Design**: Break complex workflows into logical phases
- **Clear Naming**: Use descriptive names for phases and tasks
- **Error Recovery**: Handle failures gracefully
- **Documentation**: Include README.md with usage examples
- **Validation**: Test workflows thoroughly before submitting

## 📚 Documentation

### **Types of Documentation**

1. **API Documentation**: Docstrings in code
2. **User Guides**: Step-by-step instructions
3. **Developer Guides**: Technical implementation details
4. **Examples**: Real-world usage scenarios

### **Documentation Standards**

- **Clear Language**: Use simple, clear language
- **Code Examples**: Include working code examples
- **Screenshots**: Add screenshots for UI features
- **Keep Updated**: Update docs when code changes

## 🔍 Review Process

### **Pull Request Guidelines**

1. **Clear Description**: Explain what your PR does and why
2. **Link Issues**: Reference related issues or discussions
3. **Test Coverage**: Include tests for new functionality
4. **Documentation**: Update relevant documentation
5. **Small Changes**: Keep PRs focused and reasonably sized

### **Review Criteria**

- **Functionality**: Does it work as intended?
- **Code Quality**: Is it well-written and maintainable?
- **Tests**: Are there adequate tests?
- **Documentation**: Is it properly documented?
- **Performance**: Does it impact performance?
- **Security**: Are there any security concerns?

## 🏆 Recognition

We appreciate all contributions! Contributors will be:

- **Listed in Contributors**: Added to our contributors list
- **Mentioned in Releases**: Credited in release notes
- **Community Recognition**: Highlighted in community updates

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Discord/Slack**: [Community chat] (if available)
- **Email**: [maintainer email] (for sensitive issues)

## 📄 License

By contributing to AI Sidekick for Splunk, you agree that your contributions will be licensed under the Apache License 2.0.

---

**Thank you for contributing to AI Sidekick for Splunk! 🎉**
