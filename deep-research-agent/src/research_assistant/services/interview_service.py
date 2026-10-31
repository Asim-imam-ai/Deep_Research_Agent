"""Application-level interface."""

from langchain_core.messages import HumanMessage

from research_assistant.agents.interview.graph import graph
from research_assistant.schemas.analyst import Analyst


def interview(analyst: Analyst, topic: str, max_num_turns: int = 2):
    return graph.invoke(
        {
            "analyst": analyst,
            "messages": [HumanMessage(content=topic)],
            "max_num_turns": max_num_turns,
        }
    )
