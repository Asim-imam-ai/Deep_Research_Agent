"""Typed final report record."""

from pydantic import BaseModel, Field

from research_assistant.agents.research.schemas import ResearchSection


class ReportOutput(BaseModel):
    topic: str = Field(min_length=1)
    title: str = Field(min_length=1)
    introduction: str
    findings: str
    conclusion: str
    sections: list[ResearchSection]
    sources: list[str]
    markdown: str
