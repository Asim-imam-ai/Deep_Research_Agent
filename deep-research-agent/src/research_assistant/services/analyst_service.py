"""Application-level interface."""

from research_assistant.agents.analyst.graph import graph


def generate(topic: str, max_analysts: int = 3, feedback: str | None = None):
    return graph.invoke(
        {"topic": topic, "max_analysts": max_analysts, "human_analyst_feedback": feedback}
    )
