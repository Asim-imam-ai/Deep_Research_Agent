import pytest

from research_assistant.core.config import Settings
from research_assistant.core.exceptions import SearchError
from research_assistant.tools.web_search.service import WebSearchService
from research_assistant.tools.web_search.tavily import TavilyClient


class StubClient:
    def search(self, query):
        return {
            "results": [
                {"title": "One", "url": "https://example.com/", "content": "Data"},
                {"title": "Duplicate", "url": "https://example.com/", "content": "More"},
                {"title": "Invalid", "url": "not-a-url", "content": "Bad"},
            ]
        }


def test_normalizes_and_deduplicates():
    result = WebSearchService(client=StubClient()).search(" topic ")
    assert result.query == "topic"
    assert len(result.results) == 1
    assert result.results[0].title == "One"


def test_blank_query():
    with pytest.raises(ValueError):
        WebSearchService(client=StubClient()).search(" ")


def test_tavily_error_is_wrapped():
    class FailingTool:
        def invoke(self, args):
            raise RuntimeError("failure")

    client = TavilyClient(Settings(), tool=FailingTool())
    with pytest.raises(SearchError):
        client.search("topic")
