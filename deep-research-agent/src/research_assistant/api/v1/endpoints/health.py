"""Database readiness endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from research_assistant.api.dependencies.services import get_db

router = APIRouter(tags=["health"])

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("/health")
def health(db: DatabaseSession):
    """Check whether the application database is reachable."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        ) from exc

    return {"status": "healthy"}
