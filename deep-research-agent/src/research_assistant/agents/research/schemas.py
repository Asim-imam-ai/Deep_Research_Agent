"""Evidence-backed research section produced by one analyst."""

from pydantic import BaseModel, Field

from research_assistant.schemas.analyst import Analyst
from research_assistant.tools.web_search.schemas import SearchResult


class ResearchSection(BaseModel):
    analyst: Analyst
    content: str = Field(min_length=1)
    sources: list[SearchResult] = Field(default_factory=list)
    transcript: str = ""
