"""Parallel report body/intro/conclusion followed by a LangGraph fan-in barrier."""

from langgraph.graph import END, START, StateGraph

from research_assistant.agents.report.nodes import (
    finalize_report,
    write_body,
    write_conclusion,
    write_introduction,
)
from research_assistant.agents.report.state import ReportState


def build_report_graph():
    builder = StateGraph(ReportState)
    builder.add_node("write_body", write_body)
    builder.add_node("write_introduction", write_introduction)
    builder.add_node("write_conclusion", write_conclusion)
    builder.add_node("finalize_report", finalize_report)
    for name in ("write_body", "write_introduction", "write_conclusion"):
        builder.add_edge(START, name)
    builder.add_edge(["write_body", "write_introduction", "write_conclusion"], "finalize_report")
    builder.add_edge("finalize_report", END)
    return builder.compile()


graph = build_report_graph()
