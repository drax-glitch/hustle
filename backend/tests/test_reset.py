def test_reset_character(client, auth_headers):
    headers = auth_headers()

    client.post("/api/quests", json={"title": "Task", "category": "Work"}, headers=headers)
    client.patch("/api/quests/1/complete", headers=headers)

    res = client.post("/api/settings/reset-character", headers=headers)
    assert res.status_code == 200
    user = res.get_json()
    assert user["level"] == 1
    assert user["xp"] == 0
    assert user["questsDone"] == 0
    assert user["streak"] == 0

    quests = client.get("/api/quests", headers=headers).get_json()
    assert len(quests) == 0
