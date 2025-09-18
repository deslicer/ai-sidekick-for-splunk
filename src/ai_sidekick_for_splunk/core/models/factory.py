"""
LLM Model factory for AI Sidekick for Splunk.

This module provides a factory pattern for creating appropriate model instances
based on the model name and provider configuration, enabling seamless switching
between Gemini models (direct ADK integration) and other providers (via LiteLLM).
"""

import logging
from typing import Any, Union

from ..config import ModelConfig
from .litellm_wrapper import LiteLlmWrapper

logger = logging.getLogger(__name__)


class ModelFactory:
    """
    Factory for creating model instances based on provider and configuration.

    This factory automatically determines whether to use direct Gemini integration
    or LiteLLM wrapper based on the model name and configuration.
    """

    @staticmethod
    def create_model(model_name: str, config: ModelConfig) -> Union[str, Any]:
        """
        Create appropriate model instance based on provider and model name.

        Args:
            model_name: Name of the model to create
            config: ModelConfig instance with provider settings

        Returns:
            Either a string (for Gemini models) or LiteLlmWrapper instance (for others)
        """
        logger.debug(f"Creating model instance for: {model_name}")

        # Determine if this is a Gemini model
        is_gemini = config.is_gemini_model(model_name)

        # Check provider preference
        if config.model_provider == "google" or (config.model_provider == "auto" and is_gemini):
            logger.info(f"Using direct Gemini integration for model: {model_name}")
            return model_name  # Direct string for ADK Gemini integration

        elif config.model_provider == "litellm" or (
            config.model_provider == "auto" and not is_gemini
        ):
            logger.info(f"Using LiteLLM integration for model: {model_name}")
            wrapper = LiteLlmWrapper(model_name, config)
            return wrapper.get_adk_model()

        else:
            # Fallback to auto-detection
            if is_gemini:
                logger.info(f"Auto-detected Gemini model, using direct integration: {model_name}")
                return model_name
            else:
                logger.info(f"Auto-detected non-Gemini model, using LiteLLM: {model_name}")
                wrapper = LiteLlmWrapper(model_name, config)
                return wrapper.get_adk_model()

    @staticmethod
    def get_model_for_agent(agent_name: str, config: ModelConfig) -> Union[str, Any]:
        """
        Get the appropriate model instance for a specific agent.

        Args:
            agent_name: Name of the agent requesting a model
            config: ModelConfig instance with preferences and settings

        Returns:
            Model instance (string for Gemini, LiteLLM instance for others)
        """
        # Get the preferred model name for this agent
        model_name = config.get_model_for_agent(agent_name)

        logger.debug(f"Agent '{agent_name}' requesting model: {model_name}")

        # Create and return the appropriate model instance
        return ModelFactory.create_model(model_name, config)

    @staticmethod
    def is_model_available(model_name: str, config: ModelConfig) -> bool:
        """
        Check if a model is available with current configuration.

        Args:
            model_name: Name of the model to check
            config: ModelConfig instance with API keys and settings

        Returns:
            True if model appears to be available, False otherwise
        """
        try:
            # For Gemini models, check if Google API key or Vertex AI is configured
            if config.is_gemini_model(model_name):
                has_google_key = bool(config.google_api_key)
                has_vertex_config = bool(config.google_cloud_project and config.use_vertex_ai)
                return has_google_key or has_vertex_config

            # For other models, check if appropriate API keys are available
            else:
                # Check for model-specific API keys based on model name patterns
                if model_name.startswith(("gpt-", "text-", "davinci", "curie", "babbage", "ada")):
                    return bool(config.openai_api_key)
                elif model_name.startswith(("claude-", "anthropic")):
                    return bool(config.anthropic_api_key)
                elif "azure" in model_name.lower():
                    return bool(config.azure_api_key and config.azure_api_base)
                else:
                    # For other models, assume available if any LiteLLM key is configured
                    return bool(
                        config.litellm_api_key
                        or config.openai_api_key
                        or config.anthropic_api_key
                        or config.azure_api_key
                    )

        except Exception as e:
            logger.warning(f"Error checking availability for model {model_name}: {e}")
            return False

    @staticmethod
    def list_available_models(config: ModelConfig) -> dict[str, dict[str, Any]]:
        """
        List all available models based on current configuration.

        Args:
            config: ModelConfig instance with API keys and settings

        Returns:
            Dictionary mapping model names to their metadata
        """
        available_models = {}

        # Common Gemini models
        gemini_models = [
            "gemini-2.5",
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-pro",
            "gemini-pro-vision",
        ]

        for model in gemini_models:
            if ModelFactory.is_model_available(model, config):
                available_models[model] = {
                    "provider": "google",
                    "type": "gemini",
                    "available": True,
                }

        # Common OpenAI models (if API key available)
        if config.openai_api_key:
            openai_models = ["gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"]
            for model in openai_models:
                available_models[model] = {"provider": "openai", "type": "gpt", "available": True}

        # Common Anthropic models (if API key available)
        if config.anthropic_api_key:
            anthropic_models = [
                "claude-3-opus",
                "claude-3-sonnet",
                "claude-3-haiku",
                "claude-3-5-sonnet",
                "claude-3-5-haiku",
            ]
            for model in anthropic_models:
                available_models[model] = {
                    "provider": "anthropic",
                    "type": "claude",
                    "available": True,
                }

        logger.info(f"Found {len(available_models)} available models")
        return available_models
