"""Research lifecycle API and replayable Server-Sent Events."""

import asyncio
import json
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Query,
    Request,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from research_assistant.api.dependencies.services import (
    get_db,
    get_research_manager,
)
from research_assistant.api.schemas.requests import (
    FeedbackRequest,
    StartResearchRequest,
)
from research_assistant.api.schemas.responses import (
    FeedbackResponse,
    RunResponse,
)
from research_assistant.infrastructure.database.models import RunStatus
from research_assistant.infrastructure.database.session import (
    session_factory,
)
from research_assistant.services.research_service import (
    ResearchManagementService,
)

router = APIRouter(
    prefix="/research",
    tags=["research"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]

ResearchManager = Annotated[
    ResearchManagementService,
    Depends(get_research_manager),
]


@router.post(
    "",
    response_model=RunResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_research(
    data: StartResearchRequest,
    db: DatabaseSession,
    manager: ResearchManager,
) -> RunResponse:
    """Create and enqueue a new research run."""

    return manager.create(
        db,
        data.topic,
        data.max_analysts,
        data.max_num_turns,
    )


@router.get(
    "",
    response_model=list[RunResponse],
)
def list_research(
    db: DatabaseSession,
    manager: ResearchManager,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[RunResponse]:
    """Return paginated research runs."""

    return manager.list(
        db,
        offset,
        limit,
    )


@router.get(
    "/{run_id}",
    response_model=RunResponse,
)
def get_research(
    run_id: UUID,
    db: DatabaseSession,
    manager: ResearchManager,
) -> RunResponse:
    """Retrieve one research run by its identifier."""

    run = manager.get(
        db,
        run_id,
    )

    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research run not found",
        )

    return run


@router.post(
    "/{run_id}/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def submit_feedback(
    run_id: UUID,
    data: FeedbackRequest,
    db: DatabaseSession,
    manager: ResearchManager,
) -> FeedbackResponse:
    """Approve generated analysts or request regeneration."""

    try:
        run = manager.feedback(
            db,
            run_id,
            data.approved,
            data.feedback,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research run not found",
        )

    return FeedbackResponse(
        run_id=run.id,
        status=run.status,
    )


@router.get("/{run_id}/stream")
async def stream_research(
    run_id: UUID,
    request: Request,
    last_event_id: Annotated[
        str | None,
        Header(alias="Last-Event-ID"),
    ] = None,
    after: Annotated[
        int,
        Query(ge=0),
    ] = 0,
) -> StreamingResponse:
    """Stream research events using Server-Sent Events."""

    # Validate research run before beginning the stream.
    with session_factory()() as db:
        manager = ResearchManagementService()

        research_run = manager.get(db, run_id)

        if research_run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research run not found",
            )

    # Restore the cursor for reconnecting SSE clients.
    try:
        cursor = int(last_event_id) if last_event_id is not None else after

        if cursor < 0:
            raise ValueError("Event cursor must be nonnegative")

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Last-Event-ID must be a nonnegative integer",
        ) from exc

    async def event_generator():
        nonlocal cursor

        while not await request.is_disconnected():
            # The session closes before the next polling interval.
            with session_factory()() as db:
                manager = ResearchManagementService()

                batch = manager.events(
                    db,
                    run_id,
                    cursor,
                )

                research_run = manager.get(
                    db,
                    run_id,
                )

                terminal = research_run is not None and research_run.status in (
                    RunStatus.completed,
                    RunStatus.failed,
                )

                records = [
                    (
                        event.id,
                        event.kind,
                        event.payload,
                    )
                    for event in batch
                ]

            for event_id, kind, payload in records:
                cursor = event_id

                event_data = json.dumps(
                    payload,
                    default=str,
                )

                yield (f"id: {event_id}\nevent: {kind}\ndata: {event_data}\n\n")

            if terminal and not records:
                break

            if not records:
                yield ": heartbeat\n\n"

                await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
