# Release Notes - AI Sidekick for Splunk

This document contains detailed release notes for AI Sidekick for Splunk.

## How We Release

We use [Release Please](https://github.com/googleapis/release-please) for automated releases based on [Conventional Commits](https://www.conventionalcommits.org/).

### Commit Types
- `feat:` - New features (minor version bump)
- `fix:` - Bug fixes (patch version bump)
- `feat!:` or `fix!:` - Breaking changes (major version bump)

## Released Versions

### v0.1.0 (Initial Release) - TBD

🎉 **First public release of AI Sidekick for Splunk!**

#### 🌟 Major Features
- **FlowPilot System**: Template-driven workflow execution engine
- **Auto-Discovery**: Automatic agent discovery and registration
- **Multi-Agent Architecture**: Core and community agent support
- **Web Interface**: ADK-powered web interface for agent interaction

#### 📦 Installation
```bash
pip install ai-sidekick-for-splunk
```

#### 🚀 Quick Start
```bash
# Set up environment
cp .env.example .env
# Edit .env with your Google API key

# Start AI Sidekick
ai-sidekick
```
