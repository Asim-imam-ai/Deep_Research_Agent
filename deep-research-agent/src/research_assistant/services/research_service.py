"""Phase 2 synchronous functions remain available; Phase 3 adds durable management."""

from uuid import UUID, uuid4

from langgraph.types import Command
from sqlalchemy import select
from sqlalchemy.orm import Session

from research_assistant.guardrails.input_validation import validate_limits, validate_topic
from research_assistant.infrastructure.database.models import ResearchEvent, ResearchRun, RunStatus
from research_assistant.infrastructure.database.repositories import RunRepository
from research_assistant.orchestration.graph import graph


def start_research(
    topic: str, max_analysts: int = 3, max_num_turns: int = 2, thread_id: str | None = None
):
    thread_id = thread_id or str(uuid4())
    result = graph.invoke(
        {
            "topic": topic,
            "max_analysts": max_analysts,
            "max_num_turns": max_num_turns,
            "sections": [],
        },
        config={"configurable": {"thread_id": thread_id}},
    )
    return thread_id, result


def resume_research(thread_id: str, feedback: str | dict | None = "approve"):
    return graph.invoke(Command(resume=feedback), config={"configurable": {"thread_id": thread_id}})


class ResearchManagementService:
    def create(self, db: Session, topic: str, max_analysts: int, max_num_turns: int):
        topic = validate_topic(topic)
        validate_limits(max_analysts, max_num_turns)
        run = RunRepository(db).create(topic, max_analysts, max_num_turns)
        db.commit()
        db.refresh(run)
        return run

    def get(self, db: Session, run_id: UUID):
        return RunRepository(db).get(run_id)

    def list(self, db: Session, offset: int = 0, limit: int = 50):
        return list(
            db.scalars(
                select(ResearchRun)
                .order_by(ResearchRun.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
        )

    def feedback(self, db: Session, run_id: UUID, approved: bool, feedback: str):
        repo = RunRepository(db)
        run = repo.get(run_id, lock=True)
        if run is None:
            return None
        if run.status != RunStatus.awaiting_feedback:
            raise ValueError("This run is not awaiting feedback")
        run.pending_feedback = {"approved": approved, "feedback": feedback}
        run.status = RunStatus.queued
        repo.event(run.id, "feedback_received", {"approved": approved})
        db.commit()
        db.refresh(run)
        return run

    def events(self, db: Session, run_id: UUID, after: int = 0, limit: int = 100):
        return list(
            db.scalars(
                select(ResearchEvent)
                .where(ResearchEvent.run_id == run_id, ResearchEvent.id > after)
                .order_by(ResearchEvent.id)
                .limit(limit)
            )
        )
