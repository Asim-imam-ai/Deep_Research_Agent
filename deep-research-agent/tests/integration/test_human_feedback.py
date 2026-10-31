from unittest.mock import patch

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from research_assistant.orchestration.graph import build_research_workflow
from research_assistant.schemas.analyst import Analyst


def test_reject_then_approve_regenerates():
    counter = {"calls": 0}

    def fake_gen(state):
        counter["calls"] += 1
        return {"analysts": [Analyst(name="A", role="R", affiliation="X", description="D")]}

    def fake_research(state):
        return {"sections": ["section"]}

    def fake_report(state):
        return {"final_report": "done"}

    with (
        patch("research_assistant.orchestration.graph.generate_analysts", fake_gen),
        patch("research_assistant.orchestration.graph.conduct_research", fake_research),
        patch("research_assistant.orchestration.graph.create_report", fake_report),
    ):
        graph = build_research_workflow(InMemorySaver())
        config = {"configurable": {"thread_id": "feedback-test"}}
        state = graph.invoke({"topic": "AI", "max_analysts": 1, "sections": []}, config=config)
        assert "__interrupt__" in state
        state = graph.invoke(Command(resume="Change the perspective"), config=config)
        assert "__interrupt__" in state
        state = graph.invoke(Command(resume="approve"), config=config)
        assert counter["calls"] == 2
        assert state["final_report"] == "done"
