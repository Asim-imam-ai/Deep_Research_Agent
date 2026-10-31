from research_assistant.infrastructure.database.models import RunStatus


def test_feedback_requires_paused_run(api):
    client, manager = api
    run_id = client.post("/api/v1/research", json={"topic": "Agentic AI research"}).json()["id"]
    assert (
        client.post(f"/api/v1/research/{run_id}/feedback", json={"approved": True}).status_code
        == 409
    )
    manager.run.status = RunStatus.awaiting_feedback
    resp = client.post(f"/api/v1/research/{run_id}/feedback", json={"approved": True})
    assert resp.status_code == 202
    assert resp.json()["status"] == "queued"


def test_rejection_requires_feedback(api):
    client, _ = api
    assert (
        client.post(
            "/api/v1/research/00000000-0000-0000-0000-000000000001/feedback",
            json={"approved": False},
        ).status_code
        == 422
    )
