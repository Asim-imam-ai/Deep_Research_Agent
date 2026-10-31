import pytest

from research_assistant.agents.report.schemas import ReportOutput
from research_assistant.agents.research.schemas import ResearchSection
from research_assistant.guardrails.output_validation import validate_report
from research_assistant.schemas.analyst import Analyst


def test_no_external_sources_fails_closed():
    analyst = Analyst(name="Ada", role="Researcher", affiliation="Lab", description="Testing")
    section = ResearchSection(analyst=analyst, content="Evidence was reviewed.", sources=[])
    report = ReportOutput(
        topic="Testing",
        title="Testing",
        introduction="Intro",
        findings="Finding [1]",
        conclusion="Conclusion",
        sections=[section],
        sources=[],
        markdown="# Testing\n\nFinding [1]",
    )
    with pytest.raises(ValueError):
        validate_report(report)
