def test_dashboard_stats(client, auth_headers):
    headers = auth_headers()

    stats = client.get("/api/dashboard/stats", headers=headers).get_json()
    assert stats["completedToday"] == 0
    assert stats["dailyGoal"] >= 1

    client.post("/api/quests", json={"title": "Today task", "category": "Work", "dueLabel": "Today"}, headers=headers)
    client.patch("/api/quests/1/complete", headers=headers)

    stats = client.get("/api/dashboard/stats", headers=headers).get_json()
    assert stats["completedToday"] == 1
    assert stats["totalCompleted"] == 1
