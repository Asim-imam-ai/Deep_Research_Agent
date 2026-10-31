from unittest.mock import patch

from research_assistant.agents.analyst.graph import graph
from research_assistant.schemas.analyst import Analyst, Perspectives


def test_analysts_generation():
    model = type("Model", (), {})()
    model.with_structured_output = lambda _: model
    model.invoke = lambda _: Perspectives(
        analysts=[Analyst(name="A", role="R", affiliation="X", description="D")]
    )
    with patch("research_assistant.agents.analyst.nodes.create_chat_model", return_value=model):
        state = graph.invoke({"topic": "AI", "max_analysts": 1})
    assert len(state["analysts"]) == 1
