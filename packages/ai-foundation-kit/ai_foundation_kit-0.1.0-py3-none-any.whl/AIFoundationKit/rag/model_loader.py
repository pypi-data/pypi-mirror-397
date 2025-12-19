import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Conditional imports
try:
    from langchain_google_genai import (
        ChatGoogleGenerativeAI,
        GoogleGenerativeAIEmbeddings,
    )
    from langchain_groq import ChatGroq
except ImportError:
    pass

from AIFoundationKit.base.exception.custom_exception import ModelException
from AIFoundationKit.base.logger.custom_logger import logger as log
from AIFoundationKit.base.utils import load_config


from AIFoundationKit.base.model import ApiKeyManager, BaseProvider


class GoogleProvider(BaseProvider):
    def load_llm(self, api_key_mgr: ApiKeyManager, config: Dict[str, Any], **kwargs):
        model_name = (
            kwargs.get("model_name") or config.get("model_name") or "gemini-pro"
        )
        temperature = kwargs.get("temperature", config.get("temperature", 0.2))
        max_tokens = kwargs.get("max_tokens", config.get("max_output_tokens", 2048))

        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key_mgr.get("GOOGLE_API_KEY"),
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

    def load_embedding(
        self, api_key_mgr: ApiKeyManager, config: Dict[str, Any], **kwargs
    ):
        model_name = (
            kwargs.get("model_name")
            or config.get("model_name")
            or "models/embedding-001"
        )
        return GoogleGenerativeAIEmbeddings(
            model=model_name, google_api_key=api_key_mgr.get("GOOGLE_API_KEY")
        )


class GroqProvider(BaseProvider):
    def load_llm(self, api_key_mgr: ApiKeyManager, config: Dict[str, Any], **kwargs):
        model_name = (
            kwargs.get("model_name")
            or config.get("model_name")
            or "llama-3.3-70b-versatile"
        )
        temperature = kwargs.get("temperature", config.get("temperature", 0.5))

        return ChatGroq(
            model=model_name,
            api_key=api_key_mgr.get("GROQ_API_KEY"),
            temperature=temperature,
        )

    def load_embedding(
        self, api_key_mgr: ApiKeyManager, config: Dict[str, Any], **kwargs
    ):
        raise ModelException(
            "Groq does not currently support embeddings in this provider "
            "implementation."
        )


class ModelLoader:
    """
    Registry-based Model Loader.
    Allows dynamic registration of new providers.
    """

    def __init__(
        self, config_path: Optional[str] = None, config_dict: Optional[Dict] = None
    ):
        if os.getenv("ENV", "local").lower() != "production":
            load_dotenv()

        self.api_key_mgr = ApiKeyManager(check_keys=False)

        if config_dict:
            self.config = config_dict
        elif config_path:
            self.config = load_config(config_path)
            log.info(f"YAML config loaded from {config_path}")
        else:
            self.config = {}

        # Provider Registry
        self._providers: Dict[str, BaseProvider] = {}

        # Register default providers
        self.register_provider("google", GoogleProvider())
        self.register_provider("groq", GroqProvider())

    def register_provider(self, name: str, provider: BaseProvider):
        """
        Register a new provider.
        """
        self._providers[name.lower()] = provider
        log.info(f"Registered provider: {name}")

    def _get_provider(self, provider_name: str) -> BaseProvider:
        provider = self._providers.get(provider_name.lower())
        if not provider:
            raise ModelException(
                f"Provider '{provider_name}' not registered. \
Available: {list(self._providers.keys())}"
            )
        return provider

    def _resolve_provider_name(
        self, provider_arg: Optional[str], config_section: str
    ) -> str:
        # 1. Explicit Argument
        if provider_arg:
            return provider_arg

        # 2. Config Default
        if "default_provider" in self.config.get(config_section, {}):
            return self.config[config_section]["default_provider"]

        # 3. Environment Variable (fallback)
        env_prov = os.getenv("LLM_PROVIDER")
        if env_prov:
            return env_prov

        return "google"  # Final default

    def load_llm(self, provider: Optional[str] = None, **kwargs):
        """
        Load LLM from the specified or configured provider.
        """
        provider_name = self._resolve_provider_name(provider, "llm")
        log.info(f"Loading LLM using provider: {provider_name}")

        prov_instance = self._get_provider(provider_name)

        # Get provider specific config
        provider_config = self.config.get("llm", {}).get(provider_name, {})

        try:
            return prov_instance.load_llm(self.api_key_mgr, provider_config, **kwargs)
        except Exception as e:
            log.error(f"Failed to load LLM with {provider_name}: {e}")
            raise ModelException(f"Failed to load LLM ({provider_name}): {e}")

    def load_embeddings(self, provider: Optional[str] = None, **kwargs):
        """
        Load Embeddings from the specified or configured provider.
        """
        # Logic for embedding provider resolution might differ slightly or reuse same
        # logic. Here we assume if not passed, we look at embedding_model config or
        # default to google

        if not provider:
            # check config for embedding specific provider key?
            # Or just assume 'google' if not set in a specific 'embedding' block
            provider = "google"
            if "embedding_model" in self.config:
                # If embedding_model has a 'provider' key, we could use it.
                # Current config structure was {embedding_model: {model_name: ...}}
                # Let's support an optional 'provider' key there too
                provider = self.config["embedding_model"].get("provider", "google")

        log.info(f"Loading Embeddings using provider: {provider}")
        prov_instance = self._get_provider(provider)

        # Get provider specific config (generalized)
        # We might pass the whole embedding block
        emb_config = self.config.get("embedding_model", {})

        try:
            return prov_instance.load_embedding(self.api_key_mgr, emb_config, **kwargs)
        except Exception as e:
            log.error(f"Failed to load Embeddings with {provider}: {e}")
            raise ModelException(f"Failed to load Embeddings ({provider}): {e}")
