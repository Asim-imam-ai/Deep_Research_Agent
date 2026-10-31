"""API endpoints for retrieving completed research reports."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from research_assistant.api.dependencies.services import get_db
from research_assistant.api.schemas.responses import ReportResponse
from research_assistant.services.report_service import (
    ReportManagementService,
)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
)
def get_report(
    report_id: UUID,
    db: DatabaseSession,
) -> ReportResponse:
    """Retrieve a completed research report by its identifier."""

    report_service = ReportManagementService()

    report = report_service.get(
        db,
        report_id,
    )

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return ReportResponse(
        id=report.id,
        run_id=report.run_id,
        title=report.title,
        markdown=report.markdown,
        data=report.data,
    )
