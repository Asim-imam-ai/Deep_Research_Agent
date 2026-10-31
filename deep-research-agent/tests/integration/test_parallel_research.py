"""Tests for parallel analyst research and section aggregation."""

from unittest.mock import patch

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command, Send

from research_assistant.agents.research.schemas import ResearchSection
from research_assistant.orchestration.graph import build_research_workflow
from research_assistant.orchestration.routing import dispatch_interviews
from research_assistant.schemas.analyst import Analyst


def sample_analysts() -> list[Analyst]:
    return [
        Analyst(
            name=str(i),
            role="Researcher",
            affiliation="Lab",
            description="Focus",
        )
        for i in range(3)
    ]


def test_fanout_creates_independent_jobs():
    jobs = dispatch_interviews(
        {
            "topic": "AI",
            "analysts": sample_analysts(),
            "max_num_turns": 2,
        }
    )

    assert len(jobs) == 3
    assert all(isinstance(job, Send) for job in jobs)


def test_parallel_sections_are_merged():
    analyst_list = sample_analysts()

    def fake_gen(state):
        return {"analysts": analyst_list}

    def fake_research(state):
        analyst = state["analyst"]

        return {
            "sections": [
                ResearchSection(
                    analyst=analyst,
                    content="Section",
                    sources=[],
                )
            ]
        }

    def fake_report(state):
        assert len(state["sections"]) == 3
        return {"final_report": "OK"}

    # Patch the node functions before compiling the graph.
    with (
        patch(
            "research_assistant.orchestration.graph.generate_analysts",
            fake_gen,
        ),
        patch(
            "research_assistant.orchestration.graph.conduct_research",
            fake_research,
        ),
        patch(
            "research_assistant.orchestration.graph.create_report",
            fake_report,
        ),
    ):
        compiled = build_research_workflow(InMemorySaver())

        config = {
            "configurable": {
                "thread_id": "parallel-example",
            }
        }

        initial = compiled.invoke(
            {
                "topic": "AI",
                "max_analysts": 3,
                "sections": [],
            },
            config=config,
        )

        assert "__interrupt__" in initial

        result = compiled.invoke(
            Command(resume="approve"),
            config=config,
        )

        assert len(result["sections"]) == 3
        assert result["final_report"] == "OK"
