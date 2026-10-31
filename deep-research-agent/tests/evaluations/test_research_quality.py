import pytest

from research_assistant.guardrails.input_validation import validate_limits, validate_topic


def test_topic_bounds():
    assert validate_topic("  Agent research ") == "Agent research"
    with pytest.raises(ValueError):
        validate_topic(" ")


def test_research_limits():
    validate_limits(3, 2)
    with pytest.raises(ValueError):
        validate_limits(999, 2)
