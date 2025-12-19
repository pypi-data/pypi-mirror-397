import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from AIFoundationKit.base.exception.custom_exception import ModelException
from AIFoundationKit.base.logger.custom_logger import logger as log
from dotenv import load_dotenv

# Load dotenv if not production
if os.getenv("ENV", "local").lower() != "production":
    load_dotenv()


class ApiKeyManager:
    """
    Manages loading and retrieving API keys from environment variables or a JSON string.
    """

    REQUIRED_KEYS = ["GROQ_API_KEY", "GOOGLE_API_KEY"]

    def __init__(self, check_keys: bool = True):
        self.api_keys: Dict[str, str] = {}
        raw = os.getenv("API_KEYS")

        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    self.api_keys = parsed
                    log.info("Loaded API_KEYS from ECS secret structure")
            except Exception as e:
                log.warning(f"Failed to parse API_KEYS as JSON: {e}")

        for key in self.REQUIRED_KEYS:
            if not self.api_keys.get(key):
                env_val = os.getenv(key)
                if env_val:
                    self.api_keys[key] = env_val

        if check_keys:
            self.validate_keys()

        # Log keys present (safely)
        log.info(
            "API Key Manager initialized",
            extra={"keys_loaded": list(self.api_keys.keys())},
        )

    def validate_keys(self, required_keys: Optional[list] = None):
        keys_to_check = required_keys or self.REQUIRED_KEYS
        missing = [k for k in keys_to_check if not self.api_keys.get(k)]
        if missing:
            log.error(f"Missing required API keys: {missing}")
            raise ModelException(f"Missing API keys: {missing}")

    def get(self, key: str) -> str:
        val = self.api_keys.get(key)
        if not val:
            val = os.getenv(key)
            if not val:
                raise KeyError(f"API key for {key} is missing")
        return val


class BaseProvider(ABC):
    """
    Abstract Base Class for Model Providers.
    Any new model provider must inherit from this class.
    """

    @abstractmethod
    def load_llm(self, api_key_mgr: ApiKeyManager, config: Dict[str, Any], **kwargs):
        """
        Load and return the LLM object.
        """
        pass

    @abstractmethod
    def load_embedding(
        self, api_key_mgr: ApiKeyManager, config: Dict[str, Any], **kwargs
    ):
        """
        Load and return the Embedding object.
        """
        pass
