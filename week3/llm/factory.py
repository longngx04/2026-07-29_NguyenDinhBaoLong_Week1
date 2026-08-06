"""
Factory for creating LLM providers based on AppConfig.
"""

from week3.config import AppConfig
from week3.llm.base import LLMProvider
from week3.llm.fake import FakeLLM
from week3.llm.openrouter import OpenRouterClient


def build_llm(config: AppConfig) -> LLMProvider:
    """Instantiate the appropriate LLM provider based on config.provider_type."""
    provider_type = (config.provider_type or "fake").lower()

    if provider_type == "openrouter":
        config.ensure_openrouter_ready()
        return OpenRouterClient(
            api_key=config.api_key,
            base_url=config.base_url,
            model=config.model_name,
            timeout_seconds=config.timeout,
            max_retries=config.max_retries
        )
    elif provider_type == "fake":
        return FakeLLM()
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {config.provider_type}")
