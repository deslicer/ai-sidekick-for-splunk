# Getting Started with AI Sidekick for Splunk

This guide will help you set up AI Sidekick for Splunk for development or contribution.

## Prerequisites

- Python 3.11 or higher
- Git
- Google API key (Gemini) or OpenAI API key

## Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/ai-sidekick-for-splunk.git
cd ai-sidekick-for-splunk
```

### 2. Install uv (Python Package Manager)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Create and Activate Python Virtual Environment

```bash
# Create virtual environment using uv
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scriptsctivate
```

### 4. Install Dependencies

```bash
# Install all dependencies including development tools
uv sync --dev

# Or install minimal dependencies only
uv sync
```

### 5. Set Up Environment Variables

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

### 6. Verify Installation

```bash
# Test CLI installation
uv run ai-sidekick --help
uv run ai-sidekick-create-agent --help

# Test Python package import
uv run python -c "import ai_sidekick_for_splunk; print('✅ Package imported successfully')"
```

## Development Workflow

### Starting the AI Sidekick

```bash
# Start the AI Sidekick (web interface + agents)
uv run ai-sidekick

# The web interface will be available at:
# http://localhost:8087
```

### Stopping the AI Sidekick

```bash
# Stop the AI Sidekick
uv run ai-sidekick-stop

# Or use Ctrl+C if running in foreground
```

### Creating a New Agent

```bash
# Generate agent boilerplate
uv run ai-sidekick-create-agent my_new_agent

# Add implementation (follow prompts)
uv run ai-sidekick-add-agent my_new_agent
```

### Code Quality Tools

```bash
# Format code
uv run ruff format src/

# Lint code
uv run ruff check src/

# Fix linting issues automatically
uv run ruff check src/ --fix

# Type checking
uv run mypy src/

# Run tests
uv run pytest
```

If all checks pass, you're ready to develop! 🚀
