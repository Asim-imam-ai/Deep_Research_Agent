"""Normalized external web source, independent of search provider."""

from pydantic import BaseModel, Field, HttpUrl


class SearchResult(BaseModel):
    title: str = "Untitled source"
    url: HttpUrl
    content: str = ""
    score: float | None = None


class SearchResponse(BaseModel):
    query: str = Field(min_length=1)
    results: list[SearchResult]
