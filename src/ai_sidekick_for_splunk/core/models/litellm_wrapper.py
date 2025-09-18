"""
LiteLLM wrapper for non-Gemini models in AI Sidekick for Splunk.

This module provides a wrapper around LiteLLM to enable support for
multiple model providers (OpenAI, Anthropic, Azure, etc.) while
maintaining compatibility with Google ADK's LlmAgent interface.
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class LiteLlmWrapper:
    """
    Wrapper for LiteLLM models to integrate with Google ADK.

    This wrapper creates a LiteLLM instance configured for the specified model
    and provider, handling authentication and parameter configuration automatically.
    """

    def __init__(self, model_name: str, config: Any):
        """
        Initialize the LiteLLM wrapper.

        Args:
            model_name: Name of the model (e.g., "gpt-4", "claude-3-sonnet")
            config: ModelConfig instance with provider settings
        """
        self.model_name = model_name
        self.config = config
        self._litellm_instance = None

        logger.info(f"Initializing LiteLLM wrapper for model: {model_name}")

    def get_adk_model(self) -> Any:
        """
        Get the ADK-compatible LiteLLM model instance.

        Returns:
            LiteLLM instance configured for the specified model
        """
        if self._litellm_instance is None:
            self._litellm_instance = self._create_litellm_instance()

        return self._litellm_instance

    def _create_litellm_instance(self) -> Any:
        """
        Create and configure the LiteLLM instance.

        Returns:
            Configured LiteLLM instance
        """
        try:
            # Feature-check for LiteLlm in ADK to avoid runtime import errors
            from importlib import import_module
            try:
                adk_litellm_module = import_module("google.adk.models.lite_llm")
            except Exception as import_error:
                raise ImportError(
                    f"ADK LiteLLM module not available: {import_error}"
                ) from import_error

            try:
                LiteLlm = getattr(adk_litellm_module, "LiteLlm")
            except AttributeError as attr_error:
                raise ImportError(
                    f"ADK LiteLLM support missing 'LiteLlm' symbol: {attr_error}"
                ) from attr_error

            # Prepare LiteLLM configuration
            litellm_config = {
                "model": self.model_name,
            }

            # Add optional parameters if configured
            if hasattr(self.config, "temperature") and self.config.temperature is not None:
                litellm_config["temperature"] = self.config.temperature

            if hasattr(self.config, "max_tokens") and self.config.max_tokens is not None:
                litellm_config["max_tokens"] = self.config.max_tokens

            # Add API base if specified
            if self.config.litellm_api_base:
                litellm_config["api_base"] = self.config.litellm_api_base

            # Add API key if specified (LiteLLM will also check environment variables)
            if self.config.litellm_api_key:
                litellm_config["api_key"] = self.config.litellm_api_key

            # Set provider-specific environment variables for LiteLLM auto-detection
            self._set_provider_environment_variables()

            logger.debug(f"Creating LiteLLM instance with config: {litellm_config}")

            # Create LiteLLM instance
            litellm_instance = LiteLlm(**litellm_config)

            logger.info(f"Successfully created LiteLLM instance for {self.model_name}")
            return litellm_instance

        except ImportError as e:
            logger.error(f"LiteLLM not available in Google ADK: {e}")
            raise RuntimeError(
                f"LiteLLM support not available in Google ADK for model {self.model_name}. "
                "Please install or upgrade google-adk to a version that includes LiteLLM support."
            ) from e
        except Exception as e:
            logger.error(f"Failed to create LiteLLM instance for {self.model_name}: {e}")
            raise RuntimeError(
                f"Failed to initialize LiteLLM for model {self.model_name}: {e}"
            ) from e

    def _set_provider_environment_variables(self) -> None:
        """
        Set provider-specific environment variables for LiteLLM auto-detection.

        LiteLLM automatically detects the provider based on model name and
        looks for corresponding API keys in environment variables.
        """
        # Set OpenAI API key if available
        if self.config.openai_api_key and not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = self.config.openai_api_key
            logger.debug("Set OPENAI_API_KEY from config")

        # Set Anthropic API key if available
        if self.config.anthropic_api_key and not os.getenv("ANTHROPIC_API_KEY"):
            os.environ["ANTHROPIC_API_KEY"] = self.config.anthropic_api_key
            logger.debug("Set ANTHROPIC_API_KEY from config")

        # Set Azure API configuration if available
        if self.config.azure_api_key and not os.getenv("AZURE_API_KEY"):
            os.environ["AZURE_API_KEY"] = self.config.azure_api_key
            logger.debug("Set AZURE_API_KEY from config")

        if self.config.azure_api_base and not os.getenv("AZURE_API_BASE"):
            os.environ["AZURE_API_BASE"] = self.config.azure_api_base
            logger.debug("Set AZURE_API_BASE from config")

        if self.config.azure_api_version and not os.getenv("AZURE_API_VERSION"):
            os.environ["AZURE_API_VERSION"] = self.config.azure_api_version
            logger.debug("Set AZURE_API_VERSION from config")

    def __str__(self) -> str:
        """String representation of the wrapper."""
        return f"LiteLlmWrapper(model={self.model_name})"

    def __repr__(self) -> str:
        """Detailed string representation of the wrapper."""
        return f"LiteLlmWrapper(model_name='{self.model_name}', config={self.config})"
