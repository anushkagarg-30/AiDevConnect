import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_register_login_and_match_flow(client):
    user_a = {
        "email": "alice@test.com",
        "username": "alice",
        "password": "password123",
    }
    user_b = {
        "email": "bob@test.com",
        "username": "bob",
        "password": "password123",
    }

    for user in (user_a, user_b):
        response = await client.post("/api/v1/auth/register", json=user)
        assert response.status_code == 201

    login_a = await client.post("/api/v1/auth/login/json", json={
        "email": user_a["email"],
        "password": user_a["password"],
    })
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    login_b = await client.post("/api/v1/auth/login/json", json={
        "email": user_b["email"],
        "password": user_b["password"],
    })
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    project_a = await client.post(
        "/api/v1/projects",
        headers=headers_a,
        json={
            "title": "ML Recipe App",
            "description": "An AI-powered recipe generator using transformers and React frontend.",
            "skills_needed": "Python, React",
        },
    )
    assert project_a.status_code == 201
    project_a_id = project_a.json()["id"]

    project_b = await client.post(
        "/api/v1/projects",
        headers=headers_b,
        json={
            "title": "Smart Cooking Assistant",
            "description": "Semantic search over recipes with embeddings and a modern web UI.",
            "skills_needed": "TypeScript, FastAPI",
        },
    )
    assert project_b.status_code == 201
    project_b_id = project_b.json()["id"]

    matches = await client.get(
        f"/api/v1/projects/{project_a_id}/matches",
        headers=headers_a,
    )
    assert matches.status_code == 200
    results = matches.json()
    assert len(results) >= 1
    assert results[0]["project"]["id"] == project_b_id
    assert results[0]["similarity"] > 0

    match_request = await client.post(
        "/api/v1/matches",
        headers=headers_a,
        json={
            "project_id": project_b_id,
            "requester_project_id": project_a_id,
        },
    )
    assert match_request.status_code == 201
    match_id = match_request.json()["id"]

    matches_after = await client.get(
        f"/api/v1/projects/{project_a_id}/matches",
        headers=headers_a,
    )
    assert matches_after.status_code == 200
    assert not any(item["project"]["id"] == project_b_id for item in matches_after.json())

    duplicate = await client.post(
        "/api/v1/matches",
        headers=headers_a,
        json={
            "project_id": project_b_id,
            "requester_project_id": project_a_id,
        },
    )
    assert duplicate.status_code == 400

    received = await client.get("/api/v1/matches/received", headers=headers_b)
    assert received.status_code == 200
    assert any(item["id"] == match_id for item in received.json())

    accepted = await client.post(f"/api/v1/matches/{match_id}/accept", headers=headers_b)
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = await client.post(
        "/api/v1/auth/login/json",
        json={"email": "nobody@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health_includes_database(client):
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"
