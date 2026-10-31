"""Simple structural exit; business branching stays in the main orchestrator."""

from typing import Literal

from research_assistant.agents.research.state import ResearchState


def route_after_interview(state: ResearchState) -> Literal["write_section"]:
    if not state.get("interview"):
        raise ValueError("Interview must complete before writing a section")
    return "write_section"
