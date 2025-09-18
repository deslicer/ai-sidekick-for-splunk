#!/usr/bin/env python3
"""
List available models for AI Sidekick for Splunk.

This command shows all available models based on the current configuration,
including which providers are configured and which agents prefer which models.
"""

import os
from typing import Any

from ..core.config import Config
from ..core.models import ModelFactory


def format_model_info(models: dict[str, dict[str, Any]], config: Config) -> str:
    """Format model information for display."""
    output = []

    # Group models by provider
    providers = {}
    for model_name, model_info in models.items():
        provider = model_info.get("provider", "unknown")
        if provider not in providers:
            providers[provider] = []
        providers[provider].append((model_name, model_info))

    # Display each provider section
    for provider, provider_models in providers.items():
        output.append(f"\n🔧 **{provider.upper()} Models**")
        for model_name, model_info in provider_models:
            status = "✅ Available" if model_info.get("available", False) else "❌ Not configured"
            model_type = model_info.get("type", "unknown")
            output.append(f"  • {model_name} ({model_type}) - {status}")

    return "\n".join(output)


def format_agent_preferences(config) -> str:
    """Format agent model preferences for display."""
    output = []

    if config.model_preferences:
        output.append("\n🤖 **Agent Model Preferences**")
        for agent_name, model_name in config.model_preferences.items():
            output.append(f"  • {agent_name}: {model_name}")
    else:
        output.append("\n🤖 **Agent Model Preferences**: None configured (all use default)")

    return "\n".join(output)


def format_configuration_info(config) -> str:
    """Format current configuration information."""
    output = []

    output.append("⚙️  **Current Configuration**")

    # Show if values are from .env or defaults
    env_file_exists = os.path.exists(".env")
    if env_file_exists:
        output.append("  📄 Source: .env file")
    else:
        output.append("  📄 Source: Default values (no .env file found)")

    output.append(f"  • Provider: {config.model_provider}")
    output.append(f"  • Default Model: {config.primary_model}")
    output.append(f"  • Fallback Model: {config.fallback_model}")

    # Show environment variable status
    env_vars_set = []
    if os.getenv("MODEL_PROVIDER"):
        env_vars_set.append("MODEL_PROVIDER")
    if os.getenv("BASE_MODEL"):
        env_vars_set.append("BASE_MODEL")
    if os.getenv("TUTOR_MODEL"):
        env_vars_set.append("TUTOR_MODEL")

    if env_vars_set:
        output.append(f"  • Environment Variables Set: {', '.join(env_vars_set)}")

    # Show which API keys are configured
    api_keys = []
    if config.google_api_key:
        api_keys.append("Google")
    if config.openai_api_key:
        api_keys.append("OpenAI")
    if config.anthropic_api_key:
        api_keys.append("Anthropic")
    if config.azure_api_key:
        api_keys.append("Azure")

    if api_keys:
        output.append(f"  • Configured APIs: {', '.join(api_keys)}")
    else:
        output.append("  • Configured APIs: None (only Google via environment)")

    return "\n".join(output)


def show_usage_examples() -> str:
    """Show usage examples for configuring models."""
    return """
📚 **Configuration Examples**

To use different models, set these environment variables in your .env file:

**Use GPT-4 as default:**
  MODEL_PROVIDER=litellm
  BASE_MODEL=gpt-4
  OPENAI_API_KEY=your_openai_key

**Use Claude for specific agents:**
  SEARCH_GURU_MODEL=claude-3-sonnet
  ANTHROPIC_API_KEY=your_anthropic_key

**Mix different models per agent:**
  ORCHESTRATOR_MODEL=gpt-4
  SEARCH_GURU_MODEL=claude-3-sonnet
  SPLUNK_MCP_MODEL=gemini-2.0-flash
  FLOW_PILOT_MODEL=gpt-4

**Auto-detect provider (recommended):**
  MODEL_PROVIDER=auto  # Uses Gemini for gemini-* models, LiteLLM for others

For more examples, see: examples/env.example
"""


def main():
    """Main function for listing available models."""
    print("🤖 AI Sidekick for Splunk - Available Models\n")

    try:
        # Load configuration
        config = Config()

        # Show current configuration
        print(format_configuration_info(config.model))

        # Get available models
        available_models = ModelFactory.list_available_models(config.model)

        if available_models:
            print(format_model_info(available_models, config.model))
        else:
            print("\n❌ **No models available** - Please configure API keys")

        # Show agent preferences
        print(format_agent_preferences(config.model))

        # Show usage examples
        print(show_usage_examples())

    except Exception as e:
        print(f"❌ Error loading model configuration: {e}")
        print("\nTip: Make sure your .env file is properly configured.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
