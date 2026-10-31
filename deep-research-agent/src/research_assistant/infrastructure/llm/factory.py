"""LLM instance factory, created on demand to simplify offline testing."""

from langchain_openai import ChatOpenAI

from research_assistant.core.config import Settings, get_settings
from research_assistant.core.exceptions import ConfigurationError
from research_assistant.infrastructure.llm.providers import LLMProvider


def create_chat_model(
    settings: Settings | None = None, *, provider: LLMProvider = LLMProvider.OPENAI
) -> ChatOpenAI:
    if provider != LLMProvider.OPENAI:
        raise ConfigurationError(f"Unsupported LLM provider: {provider}")
    config = settings or get_settings()
    if not config.openai_api_key.strip():
        raise ConfigurationError("OPENAI_API_KEY is required to call the OpenAI model")
    return ChatOpenAI(
        model=config.openai_model,
        api_key=config.openai_api_key,
        temperature=config.llm_temperature,
        timeout=config.llm_timeout_seconds,
        max_retries=config.llm_max_retries,
    )
