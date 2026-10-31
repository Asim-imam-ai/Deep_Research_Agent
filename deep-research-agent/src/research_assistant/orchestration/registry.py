"""Central graph registry without re-compiling per request."""

from research_assistant.agents.analyst.graph import graph as analyst_graph
from research_assistant.agents.interview.graph import graph as interview_graph
from research_assistant.agents.report.graph import graph as report_graph
from research_assistant.agents.research.graph import graph as research_graph

GRAPHS = {
    "analyst": analyst_graph,
    "interview": interview_graph,
    "research": research_graph,
    "report": report_graph,
}


def get_graph(name: str):
    try:
        return GRAPHS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown graph: {name}") from exc
