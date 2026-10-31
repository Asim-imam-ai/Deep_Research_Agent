"""Compile the Phase 2 graph against PostgreSQL checkpoints."""

from research_assistant.orchestration.graph import build_research_workflow


def persistent_graph(checkpointer):
    return build_research_workflow(checkpointer=checkpointer)
