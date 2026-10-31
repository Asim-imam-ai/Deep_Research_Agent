"""State of one interview; message history is append-only by reducer."""

from typing import Annotated, NotRequired, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from research_assistant.schemas.analyst import Analyst
from research_assistant.tools.web_search.schemas import SearchResult


class InterviewState(TypedDict):
    analyst: Analyst
    messages: Annotated[list[AnyMessage], add_messages]
    max_num_turns: NotRequired[int]
    turns_completed: NotRequired[int]
    search_query: NotRequired[str]
    context: NotRequired[list[SearchResult]]
    all_sources: NotRequired[list[SearchResult]]
    interview: NotRequired[str]
