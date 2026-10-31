"""Validated analyst identities and structured LLM response."""

from pydantic import BaseModel, ConfigDict, Field


class Analyst(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    role: str = Field(min_length=1)
    affiliation: str = Field(min_length=1)
    description: str = Field(min_length=1)

    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nFocus: {self.description}"


class Perspectives(BaseModel):
    analysts: list[Analyst]
