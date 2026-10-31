"""Supported provider options (Phase 1 supports OpenAI)."""

from enum import StrEnum


class LLMProvider(StrEnum):
    OPENAI = "openai"
