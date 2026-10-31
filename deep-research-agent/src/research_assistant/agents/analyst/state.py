"""Minimal analyst graph state; feedback is supplied on invocation for Phase 1."""

from typing import NotRequired, TypedDict

from research_assistant.schemas.analyst import Analyst


class AnalystState(TypedDict):
    topic: str
    max_analysts: int
    human_analyst_feedback: NotRequired[str | None]
    analysts: NotRequired[list[Analyst]]
