from langchain_core.messages import AIMessage, HumanMessage

from research_assistant.agents.interview import nodes
from research_assistant.agents.interview.graph import graph
from research_assistant.schemas.analyst import Analyst
from research_assistant.schemas.search import SearchQuery
from research_assistant.tools.web_search.schemas import SearchResponse, SearchResult


class FakeModel:
    def __init__(self):
        self.structured = False

    def with_structured_output(self, schema):
        self.structured = True
        assert schema is SearchQuery
        return self

    def invoke(self, messages):
        if self.structured:
            return SearchQuery(search_query="AI safety")
        if "research interviewer" in str(messages[0].content):
            return AIMessage(content="What is AI safety?")
        return AIMessage(content="AI safety concerns reliable systems [1].")


class FakeSearch:
    def search(self, query):
        return SearchResponse(
            query=query,
            results=[
                SearchResult(
                    title="Example", url="https://example.org/a", content="Reliable systems"
                )
            ],
        )


def test_interview_graph_two_turns(monkeypatch):
    monkeypatch.setattr(nodes, "create_chat_model", lambda: FakeModel())
    monkeypatch.setattr(nodes, "WebSearchService", lambda: FakeSearch())
    analyst = Analyst(
        name="Ada", role="Researcher", affiliation="Independent", description="Safety"
    )
    result = graph.invoke(
        {"analyst": analyst, "messages": [HumanMessage(content="Research AI")], "max_num_turns": 2}
    )
    assert result["turns_completed"] == 2
    assert result["interview"].count("AI safety concerns") == 2
    assert len(result["context"]) == 1
