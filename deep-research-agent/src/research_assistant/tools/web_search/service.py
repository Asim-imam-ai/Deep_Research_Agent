"""Deduplicate and validate Tavily web results."""

from typing import Any

from pydantic import ValidationError

from research_assistant.core.exceptions import SearchError
from research_assistant.tools.web_search.schemas import SearchResponse, SearchResult
from research_assistant.tools.web_search.tavily import TavilyClient


class WebSearchService:
    def __init__(self, client: TavilyClient | Any | None = None):
        self.client = client or TavilyClient()

    def search(self, query: str) -> SearchResponse:
        query = query.strip()
        if not query:
            raise ValueError("Search query must not be empty")
        data = self.client.search(query)
        items = data.get("results", []) if isinstance(data, dict) else data
        if not isinstance(items, list):
            raise SearchError("Search results must be a list")
        results: list[SearchResult] = []
        seen: set[str] = set()
        for item in items:
            if not isinstance(item, dict) or not item.get("url"):
                continue
            try:
                candidate = SearchResult(
                    title=str(item.get("title") or "Untitled source"),
                    url=item["url"],
                    content=str(item.get("content") or ""),
                    score=item.get("score"),
                )
            except (ValidationError, ValueError, TypeError):
                continue
            key = str(candidate.url).rstrip("/")
            if key not in seen:
                seen.add(key)
                results.append(candidate)
        return SearchResponse(query=query, results=results)
