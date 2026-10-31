"""Compile the standalone analyst generation graph."""

from langgraph.graph import END, START, StateGraph

from research_assistant.agents.analyst.nodes import generate_analysts
from research_assistant.agents.analyst.state import AnalystState


def build_analyst_graph():
    builder = StateGraph(AnalystState)
    builder.add_node("generate_analysts", generate_analysts)
    builder.add_edge(START, "generate_analysts")
    builder.add_edge("generate_analysts", END)
    return builder.compile()


graph = build_analyst_graph()
