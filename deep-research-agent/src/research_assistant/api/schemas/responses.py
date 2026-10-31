from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from research_assistant.api.schemas.common import Status


class RunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    topic: str
    status: Status
    max_analysts: int
    max_num_turns: int
    created_at: datetime
    updated_at: datetime
    error: str | None = None


class ReportResponse(BaseModel):
    id: UUID
    run_id: UUID
    title: str
    markdown: str
    data: dict


class FeedbackResponse(BaseModel):
    run_id: UUID
    status: Status
