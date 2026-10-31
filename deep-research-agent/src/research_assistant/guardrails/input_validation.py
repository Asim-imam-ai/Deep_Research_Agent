"""Bounded public research input, not a substitute for authorization."""

import re

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def validate_topic(topic: str, max_length: int = 1000) -> str:
    """Validate and normalize a research topic."""
    if not isinstance(topic, str):
        raise TypeError("Topic must be a string")

    clean = _CONTROL.sub("", topic).strip()

    if not 3 <= len(clean) <= max_length:
        raise ValueError(f"Topic must contain 3 to {max_length} characters")

    return clean


def validate_limits(
    analysts: int,
    turns: int,
    *,
    max_analysts: int = 8,
    max_turns: int = 8,
) -> None:
    """Validate limits on research size and interview turns."""
    if not 1 <= analysts <= max_analysts or not 1 <= turns <= max_turns:
        raise ValueError("Research limits are outside allowed bounds")
