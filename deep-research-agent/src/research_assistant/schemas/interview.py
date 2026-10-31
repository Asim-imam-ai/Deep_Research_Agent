"""Interview DTOs and optional exported transcript."""

from pydantic import BaseModel, Field


class InterviewTranscript(BaseModel):
    analyst_name: str = Field(min_length=1)
    transcript: str
    completed_turns: int = Field(ge=0)
