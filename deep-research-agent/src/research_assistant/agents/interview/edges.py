"""Deterministic interview loop termination."""

from typing import Literal

from research_assistant.agents.interview.state import InterviewState
from research_assistant.core.config import get_settings


def route_after_answer(state: InterviewState) -> Literal["ask_question", "save_interview"]:
    maximum = state.get("max_num_turns", get_settings().interview_max_turns)
    if maximum < 1:
        raise ValueError("max_num_turns must be >= 1")
    if state.get("turns_completed", 0) >= maximum:
        return "save_interview"
    # Additional interviews only when more turns are allowed; no brittle phrase checks.
    return "ask_question"
