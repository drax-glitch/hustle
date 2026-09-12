def test_quest_crud_and_complete(client, auth_headers):
    headers = auth_headers()

    res = client.post("/api/quests", json={"title": "Read book", "category": "Learning"}, headers=headers)
    assert res.status_code == 201
    quest_id = res.get_json()["id"]

    res = client.patch(f"/api/quests/{quest_id}", json={"title": "Read 30 pages"}, headers=headers)
    assert res.status_code == 200
    assert res.get_json()["title"] == "Read 30 pages"

    me_before = client.get("/api/auth/me", headers=headers).get_json()
    old_level = me_before["level"]

    res = client.patch(f"/api/quests/{quest_id}/complete", headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["quest"]["status"] == "COMPLETED"
    assert data["user"]["xp"] > 0 or data["user"]["level"] > old_level
    assert data["events"]["oldLevel"] == old_level

    res = client.patch(f"/api/quests/{quest_id}/complete", headers=headers)
    assert res.status_code == 400

    res = client.delete(f"/api/quests/{quest_id}", headers=headers)
    assert res.status_code == 200


def test_unauthorized_quest_access(client, auth_headers):
    headers_a = auth_headers("usera", "a@test.com", "password123")
    headers_b = auth_headers("userb", "b@test.com", "password123")

    res = client.post("/api/quests", json={"title": "Private quest"}, headers=headers_a)
    quest_id = res.get_json()["id"]

    res = client.patch(f"/api/quests/{quest_id}/complete", headers=headers_b)
    assert res.status_code == 404
