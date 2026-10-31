"""Tests for research API endpoints."""


def test_create_list_and_get(api):
    client, _ = api

    resp = client.post(
        "/api/v1/research",
        json={
            "topic": "Agentic AI research",
            "max_analysts": 2,
        },
    )

    assert resp.status_code == 202

    body = resp.json()
    run_id = body["id"]

    assert body["status"] == "queued"

    get_response = client.get(f"/api/v1/research/{run_id}")
    assert get_response.status_code == 200

    list_response = client.get("/api/v1/research")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_invalid_topic(api):
    client, _ = api

    response = client.post(
        "/api/v1/research",
        json={"topic": "a"},
    )

    assert response.status_code == 422
