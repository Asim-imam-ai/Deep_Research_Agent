"""Question generation, web search, grounded answers, and transcript nodes."""

import logging
from functools import lru_cache
from importlib.resources import files

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.messages.utils import get_buffer_string

from research_assistant.agents.interview.state import InterviewState
from research_assistant.core.exceptions import AgentExecutionError
from research_assistant.guardrails.source_validation import validate_source_url
from research_assistant.infrastructure.llm.factory import create_chat_model
from research_assistant.schemas.analyst import Analyst
from research_assistant.schemas.search import SearchQuery
from research_assistant.tools.web_search.schemas import SearchResult
from research_assistant.tools.web_search.service import WebSearchService

logger = logging.getLogger(__name__)


@lru_cache(maxsize=4)
def _prompt(relative: str) -> str:
    """Load and cache an agent prompt."""
    return files("research_assistant").joinpath("prompts", relative).read_text(encoding="utf-8")


def _analyst(state: InterviewState) -> Analyst:
    """Return the analyst as a validated Pydantic model."""
    item = state["analyst"]

    if isinstance(item, Analyst):
        return item

    return Analyst.model_validate(item)


def generate_question(state: InterviewState) -> dict:
    """Generate the next analyst interview question."""
    analyst = _analyst(state)

    prompt = _prompt("interview/question.md").format(persona=analyst.persona)

    response = create_chat_model().invoke(
        [
            SystemMessage(content=prompt),
            *state["messages"],
        ]
    )

    if not isinstance(response.content, str) or not response.content.strip():
        raise AgentExecutionError("Question generation returned empty content")

    logger.info(
        "Generated question for analyst=%s",
        analyst.name,
    )

    return {
        "messages": [response],
    }


def generate_search_query(state: InterviewState) -> dict:
    """Create a structured search query for external research."""
    prompt = _prompt("research/search.md")

    response = (
        create_chat_model()
        .with_structured_output(SearchQuery)
        .invoke(
            [
                SystemMessage(content=prompt),
                *state["messages"],
            ]
        )
    )

    if not isinstance(response, SearchQuery):
        raise AgentExecutionError("Search query model returned invalid output")

    query = response.search_query.strip()

    if not query:
        raise AgentExecutionError("Search query generation returned an empty query")

    logger.info(
        "Generated search query: %s",
        query,
    )

    return {
        "search_query": query,
    }


def search_web(state: InterviewState) -> dict:
    """Retrieve, validate, and accumulate serializable web sources."""
    query = state.get("search_query", "").strip()

    if not query:
        raise AgentExecutionError("Cannot search without a valid query")

    logger.info(
        "Searching for external evidence: %s",
        query,
    )

    try:
        response = WebSearchService().search(query)
    except Exception as exc:
        logger.exception(
            "Web search failed for query=%r",
            query,
        )
        raise AgentExecutionError("External web search failed") from exc

    valid_results: list[SearchResult] = []

    for item in response.results:
        source = SearchResult.model_validate(item)

        if validate_source_url(str(source.url)):
            valid_results.append(source)

    logger.info(
        "Web search returned %d results; %d passed URL validation",
        len(response.results),
        len(valid_results),
    )

    existing_sources = state.get("all_sources", [])

    unique_sources: list[SearchResult] = []
    seen_urls: set[str] = set()

    for item in [*existing_sources, *valid_results]:
        source = SearchResult.model_validate(item)
        url = str(source.url)

        if not validate_source_url(url):
            continue

        canonical_url = url.rstrip("/").lower()

        if canonical_url in seen_urls:
            continue

        seen_urls.add(canonical_url)
        unique_sources.append(source)

    logger.info(
        "Interview accumulated %d unique sources",
        len(unique_sources),
    )

    if not unique_sources:
        logger.warning(
            "No valid external sources collected for query=%r",
            query,
        )

    # Convert Pydantic models to JSON-compatible dictionaries
    # BEFORE returning data to LangGraph.
    return {
        "context": [source.model_dump(mode="json") for source in valid_results],
        "all_sources": [source.model_dump(mode="json") for source in unique_sources],
    }


def generate_answer(state: InterviewState) -> dict:
    """Generate an answer grounded in the current search results."""
    sources = [SearchResult.model_validate(item) for item in state.get("context", [])]

    if not sources:
        logger.warning(
            "No evidence available for analyst=%s",
            _analyst(state).name,
        )

        return {
            "messages": [
                AIMessage(
                    content=(
                        "I could not retrieve reliable external sources "
                        "for this question. I cannot provide a "
                        "source-grounded answer."
                    ),
                    name="expert",
                )
            ],
            "turns_completed": (state.get("turns_completed", 0) + 1),
        }

    context = "\n\n".join(
        (f"[{index}] {source.title}\nURL: {source.url}\nExcerpt: {source.content}")
        for index, source in enumerate(sources, start=1)
    )

    prompt = _prompt("interview/answer.md").format(
        persona=_analyst(state).persona,
        context=context,
    )

    response = create_chat_model().invoke(
        [
            SystemMessage(content=prompt),
            *state["messages"],
        ]
    )

    if not isinstance(response.content, str) or not response.content.strip():
        raise AgentExecutionError("Answer generation returned empty content")

    logger.info(
        "Generated answer using %d sources",
        len(sources),
    )

    return {
        "messages": [
            AIMessage(
                content=response.content,
                name="expert",
            )
        ],
        "turns_completed": (state.get("turns_completed", 0) + 1),
    }


def save_interview(state: InterviewState) -> dict:
    """Save the analyst interview as a readable transcript."""
    messages = state.get("messages", [])

    transcript = get_buffer_string(messages) if messages else ""

    logger.info(
        "Interview completed for analyst=%s; transcript_length=%d",
        _analyst(state).name,
        len(transcript),
    )

    return {
        "interview": transcript,
    }
