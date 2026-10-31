"""Deterministic citation checks; not semantic fact verification."""

import re

from research_assistant.agents.report.schemas import ReportOutput
from research_assistant.guardrails.source_validation import unique_valid_sources

_LINK = re.compile(r"\[(\d+)\]")


class ReportValidationError(ValueError):
    """Raised when a research report fails deterministic validation."""


def validate_report(
    report: ReportOutput,
    *,
    require_sources: bool = True,
) -> ReportOutput:
    """Validate report content, source URLs, and numbered citations.

    This validates citation structure, not whether each factual claim
    is genuinely supported by its cited source.
    """
    try:
        report = ReportOutput.model_validate(report)
    except ValueError as exc:
        raise ReportValidationError("Research report does not match the required schema") from exc

    if not report.markdown.strip() or not report.sections:
        raise ReportValidationError("Report must include content and research sections")

    valid_sources = unique_valid_sources(report.sources)

    if require_sources and not valid_sources:
        raise ReportValidationError("Research report has no valid external sources")

    if len(valid_sources) != len(report.sources):
        raise ReportValidationError("Research report includes invalid or duplicated source URLs")

    # Validate only citations appearing before the sources section.
    body = report.markdown.split("\n## Sources", 1)[0]
    references = [int(value) for value in _LINK.findall(body)]

    if any(citation < 1 or citation > len(valid_sources) for citation in references):
        raise ReportValidationError("Report refers to a nonexistent citation number")

    return report
