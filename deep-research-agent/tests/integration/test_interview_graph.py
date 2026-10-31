from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage

from research_assistant.agents.interview.graph import graph
from research_assistant.schemas.analyst import Analyst
from research_assistant.schemas.search import SearchQuery
from research_assistant.tools.web_search.schemas import SearchResponse


class FakeModel:
    def __init__(self, structured=False):
        self.structured = structured

    def with_structured_output(self, schema):
        return FakeModel(structured=True)

    def invoke(self, messages):
        if self.structured:
            return SearchQuery(search_query="agent AI")

        return AIMessage(content="Answer from research")


def test_interview_runs_one_turn():
    analyst = Analyst(name="A", role="R", affiliation="X", description="D")
    from research_assistant.agents.interview import nodes

    with (
        patch.object(nodes, "create_chat_model", return_value=FakeModel()),
        patch.object(
            nodes.WebSearchService,
            "search",
            return_value=SearchResponse(query="agent AI", results=[]),
        ),
    ):
        result = graph.invoke(
            {"analyst": analyst, "messages": [HumanMessage(content="Topic")], "max_num_turns": 1}
        )
    assert result["turns_completed"] == 1
    assert result["interview"]
