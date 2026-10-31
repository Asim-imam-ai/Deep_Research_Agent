from research_assistant.agents.analyst import nodes
from research_assistant.agents.analyst.graph import graph
from research_assistant.schemas.analyst import Analyst, Perspectives


class FakeModel:
    def with_structured_output(self, schema):
        assert schema is Perspectives
        return self

    def invoke(self, messages):
        return Perspectives(
            analysts=[
                Analyst(
                    name="Ada", role="Researcher", affiliation="Independent", description="Safety"
                )
            ]
        )


def test_analyst_graph(monkeypatch):
    monkeypatch.setattr(nodes, "create_chat_model", lambda: FakeModel())
    result = graph.invoke({"topic": "Agent safety", "max_analysts": 1})
    assert result["analysts"][0].name == "Ada"


def test_invalid_analyst_count():
    import pytest

    with pytest.raises(ValueError):
        nodes.generate_analysts({"topic": "AI", "max_analysts": 0})
