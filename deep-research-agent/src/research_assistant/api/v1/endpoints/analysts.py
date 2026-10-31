"""Retrieve analyst records for completed research runs.

Analysts generated during an interrupted workflow are stored
in the LangGraph checkpoint until the run is persisted.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from research_assistant.api.dependencies.services import get_db
from research_assistant.infrastructure.database.models import (
    AnalystRecord,
    ResearchRun,
)

router = APIRouter(
    prefix="/research",
    tags=["analysts"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("/{run_id}/analysts")
def get_analysts(
    run_id: UUID,
    db: DatabaseSession,
) -> list[dict]:
    """Return persisted analysts belonging to a research run."""

    research_run = db.get(ResearchRun, run_id)

    if research_run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research run not found",
        )

    statement = (
        select(AnalystRecord).where(AnalystRecord.run_id == run_id).order_by(AnalystRecord.position)
    )

    analysts = db.scalars(statement).all()

    return [analyst.data for analyst in analysts]
