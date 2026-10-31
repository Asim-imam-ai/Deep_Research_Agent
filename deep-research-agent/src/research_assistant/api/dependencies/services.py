"""FastAPI dependencies."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from research_assistant.infrastructure.database.session import session_factory
from research_assistant.services.research_service import ResearchManagementService


def get_db() -> Generator[Session, None, None]:
    with session_factory()() as session:
        yield session


def get_research_manager() -> ResearchManagementService:
    return ResearchManagementService()
