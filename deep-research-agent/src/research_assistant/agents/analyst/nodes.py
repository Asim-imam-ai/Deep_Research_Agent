"""Analyst generation node."""

from functools import lru_cache
from importlib.resources import files

from langchain_core.messages import HumanMessage, SystemMessage

from research_assistant.agents.analyst.state import AnalystState
from research_assistant.core.exceptions import AgentExecutionError
from research_assistant.infrastructure.llm.factory import create_chat_model
from research_assistant.schemas.analyst import Perspectives


@lru_cache(maxsize=1)
def _prompt() -> str:
    return (
        files("research_assistant")
        .joinpath("prompts/analyst/generation.md")
        .read_text(encoding="utf-8")
    )


def generate_analysts(state: AnalystState) -> dict:
    topic = state["topic"].strip()
    count = state["max_analysts"]
    if not topic or not 1 <= count <= 10:
        raise ValueError("Nonempty topic and max_analysts between 1 and 10 required")
    prompt = _prompt().format(
        topic=topic,
        max_analysts=count,
        human_analyst_feedback=state.get("human_analyst_feedback") or "None",
    )
    result = (
        create_chat_model()
        .with_structured_output(Perspectives)
        .invoke(
            [
                SystemMessage(content=prompt),
                HumanMessage(content="Generate distinct analyst personas."),
            ]
        )
    )
    if not isinstance(result, Perspectives) or len(result.analysts) != count:
        raise AgentExecutionError(f"Expected exactly {count} validated analysts")
    return {"analysts": result.analysts}
