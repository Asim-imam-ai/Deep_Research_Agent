"""Requires TEST_DATABASE_URL (separate disposable Postgres database)."""

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from research_assistant.infrastructure.database.models import Base, ResearchRun, RunStatus
from research_assistant.infrastructure.database.repositories import RunRepository


@pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="Set TEST_DATABASE_URL to run database integration tests",
)
def test_repository_creates_run():
    engine = create_engine(os.environ["TEST_DATABASE_URL"])
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as db:
            run = RunRepository(db).create("Test research topic", 2, 2)
            db.commit()
            assert db.get(ResearchRun, run.id).status == RunStatus.queued
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()
