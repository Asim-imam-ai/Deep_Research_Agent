"""Unique identifiers for research thread IDs."""

from uuid import uuid4


def new_run_id() -> str:
    return str(uuid4())
