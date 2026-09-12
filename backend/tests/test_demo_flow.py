"""End-to-End Hackathon Demo Flow Tests.

Verifies the complete RPG loop:
User Register -> Onboard -> Boss Creation -> Quest Linking ->
Quest Complete -> Boss Damage -> Attribute Gains -> Level / Evolution ->
Game Master Guidance -> Daily Chronicle Recording.
"""
import pytest
from app import create_app
from app.extensions import db
from app.models import User, Boss, Quest, BossQuest, XPLog, ChronicleEvent
from app.game_master_service import game_master
from app.chronicle_service import get_daily_chronicle


@pytest.fixture
def demo_client(app):
    """Test client for demo tests."""
    return app.test_client()


def test_full_hackathon_demo_flow(demo_client, app):
    """Execute the complete 2-minute hackathon demo loop seamlessly."""

    # 1. Register new adventurer
    reg_res = demo_client.post("/api/auth/register", json={
        "username": "hackathon_hero",
        "email": "hero@hackathon.com",
        "password": "demopassword123",
        "displayName": "Alex the Creator",
    })
    assert reg_res.status_code == 201
    token = reg_res.get_json()["token"]
    auth = {"Authorization": f"Bearer {token}"}

    # 2. Complete Onboarding with goals
    onboard_res = demo_client.post("/api/settings/complete-onboarding", headers=auth, json={
        "lifeGoals": ["Career", "Knowledge", "Discipline"],
    })
    assert onboard_res.status_code == 200

    # 3. Create Boss: "The Portfolio Beast" in Career (EPIC)
    boss_res = demo_client.post("/api/bosses", headers=auth, json={
        "title": "The Portfolio Beast",
        "description": "Launch full personal portfolio website with live demos.",
        "category": "Work",
        "difficulty": "EPIC",
        "deadline": "2026-10-01",
    })
    assert boss_res.status_code == 201
    boss_data = boss_res.get_json()
    boss_id = boss_data["id"]
    initial_hp = boss_data["maxHp"]
    assert initial_hp > 0
    assert boss_data["currentHp"] == initial_hp

    # 4. Create Linked Quest: "Build Homepage Component"
    quest_res = demo_client.post("/api/quests", headers=auth, json={
        "title": "Build Homepage Component",
        "category": "Work",
        "difficulty": "HARD",
        "attribute": "Creativity",
    })
    assert quest_res.status_code == 201
    quest_id = quest_res.get_json()["id"]

    # Link quest to boss
    link_res = demo_client.post(f"/api/bosses/{boss_id}/quests", headers=auth, json={
        "questId": quest_id,
    })
    assert link_res.status_code in [200, 201]

    # 5. Complete Quest -> Triggers Boss Damage & Progression
    comp_res = demo_client.patch(f"/api/quests/{quest_id}/complete", headers=auth)
    assert comp_res.status_code == 200
    comp_data = comp_res.get_json()

    assert comp_data["quest"]["status"] == "COMPLETED"

    # 6. Verify Boss was damaged
    boss_after_res = demo_client.get(f"/api/bosses/{boss_id}", headers=auth)
    assert boss_after_res.status_code == 200
    boss_after = boss_after_res.get_json()
    assert boss_after["currentHp"] < initial_hp
    damage_dealt = initial_hp - boss_after["currentHp"]
    assert damage_dealt > 0

    # 7. Verify Character sheet & Attributes gained
    char_res = demo_client.get("/api/character", headers=auth)
    assert char_res.status_code == 200
    char_data = char_res.get_json()
    assert char_data["user"]["xp"] > 0
    assert char_data["user"]["gold"] > 0
    assert "evolution" in char_data
    assert char_data["evolution"]["stage"] in ["novice", "adventurer", "hero", "elite", "legend"]

    # 8. Verify AI Game Master acknowledges active state & boss
    gm_res = demo_client.get("/api/game-master/advice", headers=auth)
    assert gm_res.status_code == 200
    gm_data = gm_res.get_json()
    assert "message" in gm_data
    assert gm_data["priority"] in ["high", "medium", "low"]
    assert "action_path" in gm_data

    # 9. Verify Daily Chronicle has recorded the quest and damage
    chronicle_res = demo_client.get("/api/chronicle/today", headers=auth)
    assert chronicle_res.status_code == 200
    chronicle_data = chronicle_res.get_json()
    assert chronicle_data["hasActivity"] is True
    assert chronicle_data["questsCompleted"] >= 1
    assert chronicle_data["xpGained"] > 0
    assert chronicle_data["bossDamage"] >= damage_dealt
