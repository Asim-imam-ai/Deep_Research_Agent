"""Single-analyst research subgraph."""

from langgraph.graph import END, START, StateGraph

from research_assistant.agents.research.edges import route_after_interview
from research_assistant.agents.research.nodes import conduct_interview, write_section
from research_assistant.agents.research.state import ResearchState


def build_research_graph():
    builder = StateGraph(ResearchState)
    builder.add_node("conduct_interview", conduct_interview)
    builder.add_node("write_section", write_section)
    builder.add_edge(START, "conduct_interview")
    builder.add_conditional_edges("conduct_interview", route_after_interview)
    builder.add_edge("write_section", END)
    return builder.compile()


graph = build_research_graph()
