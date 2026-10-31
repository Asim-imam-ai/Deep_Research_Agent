"""Human-approved multi-agent research graph with parallel research fan-out."""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from research_assistant.agents.analyst.nodes import generate_analysts
from research_assistant.agents.report.graph import graph as report_graph
from research_assistant.agents.report.schemas import ReportOutput
from research_assistant.agents.research.graph import graph as single_research_graph
from research_assistant.agents.research.schemas import ResearchSection
from research_assistant.orchestration.routing import (
    dispatch_interviews,
    review_analysts,
    route_review,
)
from research_assistant.orchestration.workflows import ResearchWorkflowState


def conduct_research(state: dict) -> dict:
    """Run an analyst's research graph and return a serializable section."""
    result = single_research_graph.invoke(state)

    section = ResearchSection.model_validate(result["section"])

    return {
        "sections": [
            section.model_dump(mode="json"),
        ],
    }


def create_report(state: ResearchWorkflowState) -> dict:
    """Generate the final report from all completed research sections."""
    sections = [
        ResearchSection.model_validate(section).model_dump(mode="json")
        for section in state["sections"]
    ]

    result = report_graph.invoke(
        {
            "topic": state["topic"],
            "sections": sections,
        }
    )

    report = ReportOutput.model_validate(result["report"])

    return {
        "report": report.model_dump(mode="json"),
        "final_report": report.markdown,
    }


def build_research_workflow(checkpointer=None):
    """Compile the analyst-review, research, and reporting workflow."""
    builder = StateGraph(ResearchWorkflowState)

    builder.add_node(
        "generate_analysts",
        generate_analysts,
    )
    builder.add_node(
        "review_analysts",
        review_analysts,
    )
    builder.add_node(
        "dispatch",
        lambda state: {},
    )
    builder.add_node(
        "conduct_research",
        conduct_research,
    )
    builder.add_node(
        "create_report",
        create_report,
    )

    builder.add_edge(
        START,
        "generate_analysts",
    )
    builder.add_edge(
        "generate_analysts",
        "review_analysts",
    )

    builder.add_conditional_edges(
        "review_analysts",
        route_review,
    )

    builder.add_conditional_edges(
        "dispatch",
        dispatch_interviews,
        ["conduct_research"],
    )

    builder.add_edge(
        "conduct_research",
        "create_report",
    )
    builder.add_edge(
        "create_report",
        END,
    )

    return builder.compile(
        checkpointer=checkpointer,
    )


# Development-only checkpoint storage.
# Production uses the PostgreSQL checkpointer supplied by persistent_graph().
checkpointer = InMemorySaver()
graph = build_research_workflow(checkpointer)
