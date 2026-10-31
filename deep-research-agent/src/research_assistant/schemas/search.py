"""Models shared between search query generation and research tools."""

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    search_query: str = Field(min_length=2, description="Concise query for a web search engine")
