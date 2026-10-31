"""Workflow state and reducer for parallel research sections."""

import operator
from typing import Annotated, NotRequired, TypedDict


class ResearchWorkflowState(TypedDict):
    """State shared by the complete research workflow."""

    topic: str
    max_analysts: int

    max_num_turns: NotRequired[int]
    human_analyst_feedback: NotRequired[str | None]

    # Keep analyst information JSON-compatible where possible.
    analysts: NotRequired[list[dict]]

    approved: NotRequired[bool]

    # Parallel analyst branches append individual section dictionaries.
    sections: Annotated[list[dict], operator.add]

    # Final report is persisted as a dictionary, not a Pydantic object.
    report: NotRequired[dict]

    final_report: NotRequired[str]
