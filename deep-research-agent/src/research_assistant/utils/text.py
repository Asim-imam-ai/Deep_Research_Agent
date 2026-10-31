"""Small text helpers (no agent-specific logic)."""


def nonempty_text(value: str, label: str = "text") -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{label} must not be empty")
    return value
