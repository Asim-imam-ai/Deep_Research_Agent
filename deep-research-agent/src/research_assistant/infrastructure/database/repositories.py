"""Persistence operations, with row locks on state transitions."""

from datetime import timedelta
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from research_assistant.infrastructure.database.models import (
    ResearchEvent,
    ResearchRun,
    RunStatus,
    now,
)


class RunRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, run_id: UUID, lock=False) -> ResearchRun | None:
        stmt = select(ResearchRun).where(ResearchRun.id == run_id)
        if lock:
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

    def create(self, topic: str, max_analysts: int, max_num_turns: int) -> ResearchRun:
        run = ResearchRun(topic=topic, max_analysts=max_analysts, max_num_turns=max_num_turns)
        self.db.add(run)
        self.db.flush()
        self.event(run.id, "research_queued", {"topic": topic})
        return run

    def event(self, run_id: UUID, kind: str, payload: dict | None = None):
        self.db.add(ResearchEvent(run_id=run_id, kind=kind, payload=payload or {}))

    def claim(self, worker_id: str, lease_seconds: int) -> ResearchRun | None:
        stamp = now()
        stmt = (
            select(ResearchRun)
            .where(
                or_(
                    ResearchRun.status == RunStatus.queued,
                    (ResearchRun.status == RunStatus.running) & (ResearchRun.lease_until < stamp),
                )
            )
            .order_by(ResearchRun.created_at)
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        run = self.db.scalar(stmt)
        if run:
            run.status = RunStatus.running
            run.worker_id = worker_id
            run.lease_until = stamp + timedelta(seconds=lease_seconds)
            run.attempts += 1
            self.event(run.id, "research_started" if run.attempts == 1 else "research_resumed")
        return run

    def heartbeat(self, run_id: UUID, worker_id: str, lease_seconds: int) -> bool:
        run = self.get(run_id, lock=True)
        if not run or run.worker_id != worker_id or run.status != RunStatus.running:
            return False
        run.lease_until = now() + timedelta(seconds=lease_seconds)
        return True

    def finish(self, run_id: UUID, status: RunStatus, worker_id: str):
        run = self.get(run_id, lock=True)
        if run is None or run.worker_id != worker_id:
            raise RuntimeError("Run lease lost")
        run.status = status
        run.worker_id = None
        run.lease_until = None
        return run
