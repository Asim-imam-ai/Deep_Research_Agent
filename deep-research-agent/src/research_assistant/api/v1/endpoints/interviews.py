"""Retrieve persisted interview transcripts for research runs."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from research_assistant.api.dependencies.services import get_db
from research_assistant.infrastructure.database.models import (
    InterviewRecord,
    ResearchRun,
)

router = APIRouter(
    prefix="/research",
    tags=["interviews"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("/{run_id}/interviews")
def get_interviews(
    run_id: UUID,
    db: DatabaseSession,
) -> list[dict[str, str]]:
    """Return stored interview transcripts for a research run."""

    research_run = db.get(ResearchRun, run_id)

    if research_run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research run not found",
        )

    statement = select(InterviewRecord).where(InterviewRecord.run_id == run_id)

    interviews = db.scalars(statement).all()

    return [
        {
            "analyst_name": interview.analyst_name,
            "transcript": interview.transcript,
        }
        for interview in interviews
    ]
