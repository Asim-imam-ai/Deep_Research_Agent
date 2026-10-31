"""Human-in-the-loop approval and Send-based parallel analyst dispatch."""

from typing import Literal

from langgraph.types import Send, interrupt

from research_assistant.orchestration.workflows import ResearchWorkflowState
from research_assistant.schemas.analyst import Analyst

APPROVAL_WORDS = {"approve", "approved", "yes", "continue", "perfect"}


def review_analysts(state: ResearchWorkflowState) -> dict:
    # Must run with a checkpointer and a stable thread_id to enable Command(resume=...).
    response = interrupt(
        {
            "question": "Approve these research analysts? Reply approve or provide revision feedback.",
            "analysts": [Analyst.model_validate(x).model_dump() for x in state["analysts"]],
        }
    )
    if isinstance(response, dict):
        feedback = str(response.get("feedback") or "").strip()
        approved = response.get("approved") is True
        if not approved and not feedback:
            raise ValueError("Rejection requires nonempty feedback")
    elif isinstance(response, str):
        feedback = response.strip()
        approved = feedback.lower() in APPROVAL_WORDS
        if not feedback:
            approved = True
    elif response is None:
        feedback, approved = "", True
    else:
        raise ValueError("Approval response must be a string, dictionary, or null")
    return {"approved": approved, "human_analyst_feedback": None if approved else feedback}


def route_review(state: ResearchWorkflowState) -> Literal["generate_analysts", "dispatch"]:
    return "dispatch" if state.get("approved") else "generate_analysts"


def dispatch_interviews(state: ResearchWorkflowState):
    analysts = [Analyst.model_validate(x) for x in state.get("analysts", [])]
    if not analysts:
        raise ValueError("No approved analysts available")
    return [
        Send(
            "conduct_research",
            {
                "topic": state["topic"],
                "analyst": analyst,
                "max_num_turns": state.get("max_num_turns", 2),
            },
        )
        for analyst in analysts
    ]
