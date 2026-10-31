"""Single-tenant API key authentication. Use a real identity provider before multi-tenant use."""

import hmac

from research_assistant.core.config import get_settings


def authenticate_api_key(candidate: str | None) -> bool:
    expected = get_settings().api_key.get_secret_value()
    return bool(expected) and bool(candidate) and hmac.compare_digest(candidate, expected)
