"""Report writing and deterministic Markdown assembly with source deduplication."""

import logging
from functools import lru_cache
from importlib.resources import files

from langchain_core.messages import HumanMessage, SystemMessage

from research_assistant.agents.report.schemas import ReportOutput
from research_assistant.agents.report.state import ReportState
from research_assistant.agents.research.schemas import ResearchSection
from research_assistant.infrastructure.llm.factory import create_chat_model

logger = logging.getLogger(__name__)


@lru_cache(maxsize=4)
def _prompt(filename: str) -> str:
    """Read and cache a report-generation prompt."""
    return (
        files("research_assistant")
        .joinpath("prompts", "report", filename)
        .read_text(encoding="utf-8")
    )


def _sections(state: ReportState) -> list[ResearchSection]:
    """Validate research sections from JSON-compatible graph state."""
    sections = [ResearchSection.model_validate(item) for item in state["sections"]]

    if not sections:
        raise ValueError("Cannot write report without research sections")

    return sections


def _invoke(filename: str, state: ReportState) -> str:
    """Generate a report component using the collected research."""
    sections = _sections(state)

    context = "\n\n".join(
        (f"## {section.analyst.role}: {section.analyst.description}\n{section.content}")
        for section in sections
    )

    prompt = _prompt(filename).format(
        topic=state["topic"],
        sections=context,
    )

    logger.info(
        "Generating report component %s using %d sections",
        filename,
        len(sections),
    )

    result = create_chat_model().invoke(
        [
            SystemMessage(content=prompt),
            HumanMessage(content="Write only the requested report component."),
        ]
    )

    if not isinstance(result.content, str) or not result.content.strip():
        raise ValueError(f"{filename} returned no content")

    return result.content.strip()


def write_body(state: ReportState) -> dict:
    """Generate the main research findings."""
    return {
        "findings": _invoke("report_writer.md", state),
    }


def write_introduction(state: ReportState) -> dict:
    """Generate the report introduction."""
    return {
        "introduction": _invoke("introduction.md", state),
    }


def write_conclusion(state: ReportState) -> dict:
    """Generate the report conclusion."""
    return {
        "conclusion": _invoke("conclusion.md", state),
    }


def finalize_report(state: ReportState) -> dict:
    """Assemble a final report with numbered, deduplicated sources."""
    sections = _sections(state)

    source_urls: list[str] = []
    seen_urls: set[str] = set()

    for section in sections:
        for source in section.sources:
            url = str(source.url).strip()
            canonical_url = url.rstrip("/")

            if canonical_url in seen_urls:
                continue

            seen_urls.add(canonical_url)
            source_urls.append(url)

    title = f"Research Report: {state['topic'].strip()}"

    sources_markdown = (
        "\n".join(f"{index}. {url}" for index, url in enumerate(source_urls, start=1))
        or "No verified external sources collected."
    )

    introduction = state["introduction"]
    findings = state["findings"]
    conclusion = state["conclusion"]

    markdown = (
        f"# {title}\n\n"
        f"## Introduction\n\n{introduction}\n\n"
        f"## Findings\n\n{findings}\n\n"
        f"## Conclusion\n\n{conclusion}\n\n"
        f"## Sources\n\n{sources_markdown}\n"
    )

    report = ReportOutput(
        topic=state["topic"],
        title=title,
        introduction=introduction,
        findings=findings,
        conclusion=conclusion,
        sections=sections,
        sources=source_urls,
        markdown=markdown,
    )

    logger.info(
        "Finalized research report with %d sections and %d sources",
        len(sections),
        len(source_urls),
    )

    # LangGraph checkpoints must not receive a ReportOutput object.
    return {
        "report": report.model_dump(mode="json"),
    }
