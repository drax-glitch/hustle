"""Tests for Today statistics and Streak calculation accuracy."""
import pytest
from datetime import date, timedelta
from app.extensions import db
from app.models import User, Quest, XPLog
from app.services import apply_quest_reward, _utc_today, count_completed_today


def test_today_stats_and_streak(app, client, auth_headers):
    headers = auth_headers("streakuser", "streak@example.com")
    
    with app.app_context():
        user = User.query.filter_by(username="streakuser").first()
        user_id = user.id
        
        # Check initial stats
        res = client.get("/api/dashboard/stats", headers=headers)
        assert res.status_code == 200
        stats = res.get_json()
        assert stats["completedToday"] == 0
        assert stats["todayXp"] == 0
        assert stats["todayGold"] == 0
        
        # Create an active quest
        quest_res = client.post("/api/quests", json={
            "title": "Morning Routine",
            "category": "Wellness",
            "xp": 50,
            "gold": 25,
            "stat": "Vitality",
            "dueLabel": "Today",
        }, headers=headers)
        assert quest_res.status_code == 201
        quest_data = quest_res.get_json()
        quest_id = quest_data["id"]
        
        # Complete the quest
        comp_res = client.patch(f"/api/quests/{quest_id}/complete", headers=headers)
        assert comp_res.status_code == 200
        comp_data = comp_res.get_json()["events"]
        assert comp_data["xpGained"] == 60
        assert comp_data["goldGained"] == 15
        assert comp_data["streak"] == 1
        
        # Re-check dashboard stats
        res2 = client.get("/api/dashboard/stats", headers=headers)
        stats2 = res2.get_json()
        assert stats2["completedToday"] == 1
        assert stats2["todayXp"] == 60
        assert stats2["todayGold"] == 15
        
        # Check progress endpoint
        prog_res = client.get("/api/progress", headers=headers)
        assert prog_res.status_code == 200
        prog_data = prog_res.get_json()
        assert prog_data["todayXp"] == 60
        assert prog_data["todayGold"] == 15
        assert prog_data["todayQuests"] == 1
        assert prog_data["currentStreak"] == 1


def test_streak_continuation_and_break(app):
    with app.app_context():
        user = User(
            username="streaktest",
            email="streaktest@example.com",
            display_name="Streak Tester",
            password_hash="hash",
            streak=3,
            best_streak=3,
            last_active_date=_utc_today() - timedelta(days=1),
        )
        db.session.add(user)
        db.session.flush()
        quest = Quest(
            user_id=user.id,
            title="Yesterday to Today",
            category="Work",
            xp_reward=40,
            gold_reward=20,
            attribute="Discipline",
        )
        db.session.add(quest)
        db.session.commit()
        
        # Completing quest today should continue streak
        events = apply_quest_reward(user, quest)
        assert user.streak == 4
        assert user.best_streak == 4
        assert events["streak"] == 4
        
        # Simulate broken streak: last active 3 days ago
        user.last_active_date = _utc_today() - timedelta(days=3)
        user.streak = 4
        db.session.commit()
        
        quest2 = Quest(
            user_id=user.id,
            title="After Break",
            category="Work",
            xp_reward=40,
            gold_reward=20,
            attribute="Discipline",
        )
        db.session.add(quest2)
        db.session.commit()
        
        events2 = apply_quest_reward(user, quest2)
        assert user.streak == 1
        assert user.best_streak == 4  # Best streak preserved!
        assert events2["streak"] == 1
