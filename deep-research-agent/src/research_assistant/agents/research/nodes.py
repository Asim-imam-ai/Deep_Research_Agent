"""Execute analyst interviews and write evidence-backed research sections."""

import logging
from functools import lru_cache
from importlib.resources import files

from langchain_core.messages import HumanMessage, SystemMessage

from research_assistant.agents.interview.graph import graph as interview_graph
from research_assistant.agents.research.schemas import ResearchSection
from research_assistant.agents.research.state import ResearchState
from research_assistant.core.exceptions import AgentExecutionError
from research_assistant.guardrails.source_validation import validate_source_url
from research_assistant.infrastructure.llm.factory import create_chat_model
from research_assistant.schemas.analyst import Analyst
from research_assistant.tools.web_search.schemas import SearchResult

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _section_prompt() -> str:
    """Load and cache the research section writer prompt."""
    return (
        files("research_assistant")
        .joinpath("prompts", "report", "section_writer.md")
        .read_text(encoding="utf-8")
    )


def _normalize_sources(items: list) -> list[SearchResult]:
    """Validate and deduplicate sources from models or dictionaries."""
    sources: list[SearchResult] = []
    seen_urls: set[str] = set()

    for item in items:
        source = SearchResult.model_validate(item)
        url = str(source.url)

        if not validate_source_url(url):
            logger.warning(
                "Discarding invalid source URL: %s",
                url,
            )
            continue

        canonical_url = url.rstrip("/").lower()

        if canonical_url in seen_urls:
            continue

        seen_urls.add(canonical_url)
        sources.append(source)

    return sources


def conduct_interview(state: ResearchState) -> dict:
    """Run one analyst interview and collect serializable evidence."""
    analyst = Analyst.model_validate(state["analyst"])
    topic = state["topic"]
    max_turns = state.get("max_num_turns", 2)

    logger.info(
        "Starting interview for analyst=%s, topic=%s",
        analyst.name,
        topic,
    )

    try:
        result = interview_graph.invoke(
            {
                "analyst": analyst.model_dump(mode="json"),
                "messages": [
                    HumanMessage(content=(f"Research topic: {topic}. Begin the interview."))
                ],
                "max_num_turns": max_turns,
            }
        )
    except Exception as exc:
        logger.exception(
            "Interview failed for analyst=%s",
            analyst.name,
        )
        raise AgentExecutionError(f"Research interview failed for analyst {analyst.name}") from exc

    transcript = result.get("interview", "")

    raw_sources = result.get("all_sources") or result.get("context", [])
    sources = _normalize_sources(raw_sources)

    logger.info(
        "Analyst %s collected %d valid sources",
        analyst.name,
        len(sources),
    )

    if not sources:
        logger.warning(
            "Analyst %s completed without external evidence",
            analyst.name,
        )

    # Never return custom SearchResult objects in checkpoint state.
    return {
        "interview": transcript,
        "sources": [source.model_dump(mode="json") for source in sources],
    }


def write_section(state: ResearchState) -> dict:
    """Write a section based on retrieved external evidence."""
    analyst = Analyst.model_validate(state["analyst"])
    topic = state["topic"]
    transcript = state.get("interview", "")

    sources = _normalize_sources(state.get("sources", []))

    if not sources:
        raise AgentExecutionError(
            f"Cannot write a grounded research section for "
            f"analyst {analyst.name}: no external sources were collected"
        )

    evidence = "\n\n".join(
        (f"[{index}] {source.title}\nURL: {source.url}\nExcerpt: {source.content}")
        for index, source in enumerate(sources, start=1)
    )

    prompt = _section_prompt().format(
        topic=topic,
        persona=analyst.persona,
        transcript=transcript,
        evidence=evidence,
    )

    logger.info(
        "Writing section for analyst=%s using %d sources",
        analyst.name,
        len(sources),
    )

    try:
        response = create_chat_model().invoke(
            [
                SystemMessage(content=prompt),
                HumanMessage(content=("Write the research section using the supplied evidence.")),
            ]
        )
    except Exception as exc:
        logger.exception(
            "Section generation failed for analyst=%s",
            analyst.name,
        )
        raise AgentExecutionError(f"Section generation failed for analyst {analyst.name}") from exc

    if not isinstance(response.content, str) or not response.content.strip():
        raise AgentExecutionError("Section writer returned empty content")

    section = ResearchSection(
        analyst=analyst,
        content=response.content,
        sources=sources,
        transcript=transcript,
    )

    logger.info(
        "Research section generated for analyst=%s",
        analyst.name,
    )

    # The parent graph can reconstruct this with
    # ResearchSection.model_validate(state["section"]).
    return {
        "section": section.model_dump(mode="json"),
    }
