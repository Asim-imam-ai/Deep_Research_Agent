"""API tests isolate database services, not LLM calls."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from research_assistant.api.dependencies.auth import require_api_key
from research_assistant.api.dependencies.services import get_db, get_research_manager
from research_assistant.api.main import create_app
from research_assistant.infrastructure.database.models import RunStatus


class FakeRun:
    def __init__(self, status=RunStatus.queued):
        self.id = uuid4()
        self.topic = "Agentic AI research"
        self.max_analysts = 2
        self.max_num_turns = 2
        self.status = status
        self.created_at = datetime.now(UTC)
        self.updated_at = self.created_at
        self.error = None


class FakeManager:
    def __init__(self):
        self.run = None

    def create(self, db, topic, max_analysts, max_num_turns):
        self.run = FakeRun()
        self.run.topic = topic
        self.run.max_analysts = max_analysts
        self.run.max_num_turns = max_num_turns
        return self.run

    def get(self, db, run_id):
        return self.run if self.run and self.run.id == run_id else None

    def list(self, db, offset=0, limit=50):
        return [self.run] if self.run else []

    def feedback(self, db, run_id, approved, feedback):
        run = self.get(db, run_id)
        if run and run.status != RunStatus.awaiting_feedback:
            raise ValueError("This run is not awaiting feedback")
        if run:
            run.status = RunStatus.queued
        return run

    def events(self, db, run_id, after=0, limit=100):
        return []


@pytest.fixture
def api():
    app = create_app()
    manager = FakeManager()

    app.dependency_overrides[get_db] = lambda: None
    app.dependency_overrides[get_research_manager] = lambda: manager

    # Bypass API-key authentication ONLY in these tests.
    app.dependency_overrides[require_api_key] = lambda: None

    with TestClient(app) as client:
        yield client, manager

    app.dependency_overrides.clear()
