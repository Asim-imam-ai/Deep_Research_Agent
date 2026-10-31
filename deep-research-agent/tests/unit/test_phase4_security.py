import pytest

from research_assistant.guardrails.input_validation import validate_limits, validate_topic
from research_assistant.guardrails.source_validation import validate_source_url


def test_input_validation():
    assert validate_topic("  research  ") == "research"
    with pytest.raises(ValueError):
        validate_limits(9, 1)


def test_public_source_scheme():
    assert validate_source_url("https://example.org/report")
    assert not validate_source_url("ftp://example.org/report")
