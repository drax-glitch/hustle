"""Tests for complete Boss Battle integration lifecycle."""
import pytest
from app.extensions import db
from app.models import User, Boss, Quest, BossQuest


def test_complete_boss_battle_flow(app, client, auth_headers):
    headers = auth_headers("bosshero", "bosshero@example.com")
    
    # 1. Create a Boss Battle
    create_res = client.post("/api/bosses", json={
        "title": "The Portfolio Beast",
        "description": "Finalize personal site and deploy",
        "category": "Work",
        "difficulty": "EASY",  # 1000 HP
    }, headers=headers)
    assert create_res.status_code == 201
    boss = create_res.get_json()
    boss_id = boss["id"]
    assert boss["currentHp"] == 1000
    assert boss["maxHp"] == 1000
    assert boss["status"] == "active"
    assert boss["rewardClaimed"] is False
    
    # 2. Create Quests
    q1_res = client.post("/api/quests", json={
        "title": "Build Hero Section",
        "category": "Work",
        "xpReward": 400,
        "goldReward": 50,
        "attribute": "Creativity",
    }, headers=headers)
    assert q1_res.status_code == 201
    q1_id = q1_res.get_json()["id"]
    
    q2_res = client.post("/api/quests", json={
        "title": "Deploy to Vercel",
        "category": "Work",
        "xpReward": 400,
        "goldReward": 75,
        "attribute": "Discipline",
    }, headers=headers)
    assert q2_res.status_code == 201
    q2_id = q2_res.get_json()["id"]
    
    # 3. Link Quests to Boss
    link1 = client.post(f"/api/bosses/{boss_id}/quests", json={"questId": q1_id}, headers=headers)
    assert link1.status_code == 201
    
    link2 = client.post(f"/api/bosses/{boss_id}/quests", json={"questId": q2_id}, headers=headers)
    assert link2.status_code == 201
    
    # 4. Duplicate link should fail
    dup_link = client.post(f"/api/bosses/{boss_id}/quests", json={"questId": q1_id}, headers=headers)
    assert dup_link.status_code == 400
    
    # 5. Complete First Quest -> Deals Damage to Boss (400 * 1.5 = 600 damage)
    comp1 = client.patch(f"/api/quests/{q1_id}/complete", headers=headers)
    assert comp1.status_code == 200
    comp1_data = comp1.get_json()["events"]
    assert "bossDamage" in comp1_data
    assert comp1_data["bossDamage"] is not None
    assert comp1_data["bossDamage"]["damage"] == 600
    assert comp1_data["bossDamage"]["bossId"] == boss_id
    assert comp1_data["bossDamage"]["defeated"] is False
    
    # Check boss status
    boss_check = client.get(f"/api/bosses/{boss_id}", headers=headers).get_json()
    assert boss_check["currentHp"] == 400
    assert boss_check["status"] == "active"
    
    # 6. Complete Second Quest -> Defeats Boss (400 * 1.5 = 600 damage > 400 HP)
    comp2 = client.patch(f"/api/quests/{q2_id}/complete", headers=headers)
    assert comp2.status_code == 200
    comp2_data = comp2.get_json()["events"]
    assert comp2_data["bossDamage"]["defeated"] is True
    assert comp2_data["bossDamage"]["newHp"] == 0
    
    boss_check2 = client.get(f"/api/bosses/{boss_id}", headers=headers).get_json()
    assert boss_check2["status"] == "defeated"
    assert boss_check2["currentHp"] == 0
    assert boss_check2["rewardClaimed"] is False
    
    # 7. Claim Rewards
    claim_res = client.post(f"/api/bosses/{boss_id}/claim-rewards", headers=headers)
    assert claim_res.status_code == 200
    claim_data = claim_res.get_json()
    assert claim_data["xpReward"] == 1000
    assert claim_data["goldReward"] == 500
    assert claim_data["skillPointReward"] == 1
    
    # 8. Duplicate Reward Claim MUST FAIL
    dup_claim = client.post(f"/api/bosses/{boss_id}/claim-rewards", headers=headers)
    assert dup_claim.status_code == 400
    assert "already been claimed" in dup_claim.get_json()["error"]
