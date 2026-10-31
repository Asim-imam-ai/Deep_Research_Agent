"""Trace metadata; LangSmith tracing is enabled through LANGSMITH_TRACING env configuration."""

import os
from uuid import UUID

from research_assistant.core.config import get_settings


def configure_tracing() -> bool:
    settings = get_settings()
    enabled = settings.langsmith_tracing and bool(settings.langsmith_api_key)
    os.environ["LANGSMITH_TRACING"] = "true" if enabled else "false"
    if enabled:
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    return enabled


def trace_config(run_id: UUID | str, *, model: str | None = None) -> dict:
    settings = get_settings()
    return {
        "tags": ["research", "phase4", f"model:{model or settings.openai_model}"],
        "metadata": {"research_run_id": str(run_id), "prompt_version": settings.prompt_version},
    }
