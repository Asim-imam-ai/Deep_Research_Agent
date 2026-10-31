"""Regression test for Pydantic URL conversion during report persistence."""

from unittest.mock import MagicMock
from uuid import uuid4

from research_assistant.agents.report.schemas import ReportOutput
from research_assistant.agents.research.schemas import ResearchSection
from research_assistant.infrastructure.database.models import SourceRecord
from research_assistant.infrastructure.persistence.report_repository import ReportRepository
from research_assistant.schemas.analyst import Analyst
from research_assistant.tools.web_search.schemas import SearchResult


def test_report_repository_converts_http_urls_to_strings():
    """SourceRecord URLs must be plain strings for psycopg."""

    analyst = Analyst(
        name="Researcher",
        role="Analyst",
        affiliation="Research Lab",
        description="Research specialist",
    )

    source = SearchResult(
        title="Research study",
        url="https://example.com/study",
        content="Verified evidence",
    )

    section = ResearchSection(
        analyst=analyst,
        content="Research findings",
        sources=[source],
        transcript="Research interview",
    )

    report = ReportOutput(
        topic="AI Research",
        title="Research Report: AI Research",
        introduction="Introduction",
        findings="Findings",
        conclusion="Conclusion",
        sections=[section],
        sources=["https://example.com/study"],
        markdown="# Research Report\n\n## Sources\n\n1. https://example.com/study",
    )

    db = MagicMock()
    db.scalar.return_value = None

    repository = ReportRepository(db)
    repository.save(uuid4(), report)

    saved_objects = [call.args[0] for call in db.add.call_args_list]

    saved_sources = [item for item in saved_objects if isinstance(item, SourceRecord)]

    assert len(saved_sources) == 1
    assert isinstance(saved_sources[0].url, str)
    assert saved_sources[0].url == "https://example.com/study"
    db.flush.assert_called_once()
