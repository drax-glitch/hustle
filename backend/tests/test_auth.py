def test_register_and_login(client):
    res = client.post("/api/auth/register", json={
        "username": "hero1",
        "email": "hero1@test.com",
        "password": "password123",
        "displayName": "Hero",
    })
    assert res.status_code == 201
    data = res.get_json()
    assert "token" in data
    assert data["user"]["displayName"] == "Hero"
    assert data["user"]["avatar"] == "🧙"

    res = client.post("/api/auth/login", json={"username": "hero1", "password": "password123"})
    assert res.status_code == 200
    assert "token" in res.get_json()


def test_register_short_password(client):
    res = client.post("/api/auth/register", json={
        "username": "bad",
        "email": "bad@test.com",
        "password": "short",
    })
    assert res.status_code == 400


def test_me_requires_auth(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401
