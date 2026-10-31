"""Integration tests for research report generation and serialization."""

from unittest.mock import patch

from langchain_core.messages import AIMessage
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from research_assistant.agents.report.graph import graph
from research_assistant.agents.report.schemas import ReportOutput
from research_assistant.agents.research.schemas import ResearchSection
from research_assistant.schemas.analyst import Analyst
from research_assistant.tools.web_search.schemas import SearchResult


class FakeModel:
    """Fake language model for deterministic report generation tests."""

    def invoke(self, messages):
        """Return a predictable response without calling an LLM."""
        return AIMessage(content="Verified synthesis (https://example.com/study)")


def test_report_merges_sources_once():
    """Verify that duplicate sources appear only once in the final report."""

    analyst = Analyst(
        name="A",
        role="R",
        affiliation="X",
        description="D",
    )

    source = SearchResult(
        title="Study",
        url="https://example.com/study",
        content="Evidence",
    )

    sections = [
        ResearchSection(
            analyst=analyst,
            content="Evidence",
            sources=[source],
        ),
        ResearchSection(
            analyst=analyst,
            content="Further evidence",
            sources=[source],
        ),
    ]

    with patch(
        "research_assistant.agents.report.nodes.create_chat_model",
        return_value=FakeModel(),
    ):
        result = graph.invoke(
            {
                "topic": "AI",
                "sections": [section.model_dump(mode="json") for section in sections],
            }
        )

    # Report graph returns a checkpoint-compatible dictionary.
    report_data = result["report"]

    assert isinstance(report_data, dict)

    # Reconstruct the Pydantic model for schema validation.
    output = ReportOutput.model_validate(report_data)

    # Both sections use the same URL; it must appear once in sources.
    assert len(output.sources) == 1
    assert str(output.sources[0]) == "https://example.com/study"

    # Verify the assembled Markdown report.
    assert output.markdown.count("## Sources") == 1
    assert "https://example.com/study" in output.markdown

    # Both research sections must be retained.
    assert len(output.sections) == 2


def test_report_is_langgraph_serializable():
    """Verify final report dictionaries can be serialized by LangGraph."""

    analyst = Analyst(
        name="A",
        role="Researcher",
        affiliation="X",
        description="Research expert",
    )

    source = SearchResult(
        title="Study",
        url="https://example.com/study",
        content="Verified evidence",
    )

    section = ResearchSection(
        analyst=analyst,
        content="Evidence-backed findings",
        sources=[source],
    )

    with patch(
        "research_assistant.agents.report.nodes.create_chat_model",
        return_value=FakeModel(),
    ):
        result = graph.invoke(
            {
                "topic": "AI",
                "sections": [section.model_dump(mode="json")],
            }
        )

    report_data = result["report"]

    # This must not contain a custom ReportOutput object.
    assert isinstance(report_data, dict)

    # Verify the actual checkpoint serializer accepts the result.
    serializer = JsonPlusSerializer()
    serializer.dumps_typed(report_data)

    # Confirm the serialized representation still matches the schema.
    output = ReportOutput.model_validate(report_data)

    assert output.topic == "AI"
    assert len(output.sections) == 1
    assert len(output.sources) == 1
    assert "## Sources" in output.markdown
