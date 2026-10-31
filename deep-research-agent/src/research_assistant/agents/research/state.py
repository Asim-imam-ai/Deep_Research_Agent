"""State for one independent analyst interview and section-generation run."""

from typing import NotRequired, TypedDict

from research_assistant.agents.research.schemas import ResearchSection
from research_assistant.schemas.analyst import Analyst


class ResearchState(TypedDict):
    topic: str
    analyst: Analyst
    max_num_turns: NotRequired[int]
    interview: NotRequired[str]
    sources: NotRequired[list]
    section: NotRequired[ResearchSection]
