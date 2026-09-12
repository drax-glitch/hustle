"""Tests for Phase 4 features: Game Master, Character Evolution, and Chronicle."""
import json
import pytest
from app import create_app
from app.extensions import db
from app.models import User, Quest, XPLog, Boss, ChronicleEvent, UserSkill, Skill, Achievement, UserAchievement
from app.game_master_service import game_master, GameMasterService
from app.chronicle_service import get_daily_chronicle, get_chronicle_history, log_chronicle_event, _utc_today
from app.rpg_utils import (
    get_evolution_stage,
    get_evolution_stage_display,
    get_evolution_title,
    get_next_evolution_stage,
    get_evolution_requirements,
    build_evolution_payload,
    get_evolution_cosmetics,
    get_evolution_progress,
    CHARACTER_CLASSES,
)


@pytest.fixture
def auth_header(client):
    """Create a test user and return auth headers."""
    client.post("/api/auth/register", json={
        "username": "phase4user",
        "email": "phase4@example.com",
        "password": "password123",
        "displayName": "Phase 4 User",
    })
    res = client.post("/api/auth/login", json={"username": "phase4user", "password": "password123"})
    token = res.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def phase4_user(app):
    """Create a test user in the database."""
    with app.app_context():
        user = User(
            username="p4_user_obj",
            email="p4_user_obj@example.com",
            display_name="P4 User Obj",
            password_hash="hashed_password",
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    return user_id


class TestGameMaster:
    """Tests for Game Master service."""

    def test_game_master_fallback_mode(self):
        """Test that Game Master returns fallback advice when AI is unavailable."""
        user_state = {
            "level": 5,
            "class": "Warrior",
            "attributes": {"Strength": 50, "Intelligence": 30, "Discipline": 40, "Creativity": 20, "Vitality": 35},
            "skill_points": 2,
            "streak": 3,
            "region_progress": {"health": 20, "knowledge": 50, "career": 40, "creativity": 30, "discipline": 25},
            "world_progress": 33,
            "active_boss": None,
            "unfinished_quests": [],
        }

        advice = game_master.generate_advice(user_state)

        assert advice is not None
        assert "message" in advice
        assert "priority" in advice
        assert advice["priority"] in ["high", "medium", "low"]

    def test_game_master_with_active_boss(self):
        """Test Game Master advice with active boss near defeat."""
        user_state = {
            "level": 10,
            "class": "Warrior",
            "attributes": {"Strength": 60, "Intelligence": 40, "Discipline": 50, "Creativity": 30, "Vitality": 45},
            "skill_points": 0,
            "streak": 5,
            "region_progress": {"health": 50, "knowledge": 60, "career": 70, "creativity": 40, "discipline": 55},
            "world_progress": 55,
            "active_boss": {"id": 1, "title": "Test Boss", "category": "Career", "hp_percent": 25},
            "unfinished_quests": [],
        }

        advice = game_master.generate_advice(user_state)

        assert advice is not None
        assert advice["priority"] == "high"
        assert "boss" in advice["message"].lower() or "boss" in advice.get("reason", "").lower()

    def test_game_master_with_skill_points(self):
        """Test Game Master advice when user has unused skill points."""
        user_state = {
            "level": 8,
            "class": "Scholar",
            "attributes": {"Strength": 30, "Intelligence": 55, "Discipline": 40, "Creativity": 35, "Vitality": 30},
            "skill_points": 3,
            "streak": 2,
            "region_progress": {"health": 30, "knowledge": 65, "career": 35, "creativity": 40, "discipline": 30},
            "world_progress": 40,
            "active_boss": None,
            "unfinished_quests": [],
        }

        advice = game_master.generate_advice(user_state)

        assert advice is not None
        assert "skill" in advice["message"].lower() or "points" in advice["message"].lower()

    def test_game_master_validation_rejects_hallucinations(self):
        """Test that validate_advice cleans invalid IDs returned by AI."""
        user_state = {
            "level": 3,
            "class": "Warrior",
            "active_boss": {"id": 42, "title": "Real Boss"},
            "unfinished_quests": [{"id": 101, "title": "Real Quest"}],
        }
        # Fake hallucinated payload
        fake_ai_output = {
            "message": "Attack the imaginary boss!",
            "priority": "invalid_priority",
            "boss_id": 99999,  # Doesn't exist in user state
            "quest_id": 88888, # Doesn't exist in user state
            "recommended_action": "Attack Phantom",
        }
        validated = game_master.validate_advice(fake_ai_output, user_state)
        assert validated["priority"] == "medium"  # Normalized
        assert validated["boss_id"] is None  # Sanitized
        assert validated["quest_id"] is None  # Sanitized

    def test_game_master_state_immutability(self, app, phase4_user):
        """Test that invoking Game Master does NOT mutate user level, xp, gold, or stats."""
        with app.app_context():
            user = User.query.get(phase4_user)
            user.level = 7
            user.xp = 450
            user.gold = 300
            db.session.commit()

            initial_level = user.level
            initial_xp = user.xp
            initial_gold = user.gold

            # Compute advice via fallback / service
            from app.routes.game_master import _gather_user_state
            state = _gather_user_state(user)
            advice = game_master.generate_advice(state)
            assert advice is not None

            # Re-fetch and assert unmodified
            user_after = User.query.get(phase4_user)
            assert user_after.level == initial_level
            assert user_after.xp == initial_xp
            assert user_after.gold == initial_gold

    def test_game_master_api_endpoint(self, client, auth_header):
        """Test Game Master API endpoint."""
        response = client.get("/api/game-master/advice", headers=auth_header)
        assert response.status_code == 200
        data = response.json
        assert "message" in data
        assert "priority" in data
        assert "action_path" in data

    def test_game_master_briefing_api(self, client, auth_header):
        """Test Game Master Daily Briefing endpoint."""
        response = client.get("/api/game-master/briefing", headers=auth_header)
        assert response.status_code == 200
        data = response.json
        assert "greeting" in data
        assert "bonus_objective" in data
        assert "action_path" in data

    def test_game_master_unauthenticated_fails(self, client):
        """Test that unauthenticated requests to Game Master are rejected."""
        response = client.get("/api/game-master/advice")
        assert response.status_code == 401


class TestCharacterEvolution:
    """Tests for Character Evolution system."""

    def test_evolution_stage_calculation(self):
        """Test evolution stage calculation by level."""
        assert get_evolution_stage(1) == "novice"
        assert get_evolution_stage(4) == "novice"
        assert get_evolution_stage(5) == "adventurer"
        assert get_evolution_stage(9) == "adventurer"
        assert get_evolution_stage(10) == "hero"
        assert get_evolution_stage(19) == "hero"
        assert get_evolution_stage(20) == "elite"
        assert get_evolution_stage(29) == "elite"
        assert get_evolution_stage(30) == "legend"
        assert get_evolution_stage(50) == "legend"

    def test_evolution_stage_display(self):
        """Test evolution stage display names."""
        assert get_evolution_stage_display("novice") == "🌱 Novice"
        assert get_evolution_stage_display("adventurer") == "⚔️ Adventurer"
        assert get_evolution_stage_display("hero") == "🛡️ Hero"
        assert get_evolution_stage_display("elite") == "🔥 Elite"
        assert get_evolution_stage_display("legend") == "👑 Legend"

    def test_evolution_title_all_classes(self):
        """Test class-specific evolution titles across all 6 classes."""
        classes = ["WARRIOR", "SCHOLAR", "CREATOR", "GUARDIAN", "EXPLORER", "MASTER_ADVENTURER"]
        stages = ["novice", "adventurer", "hero", "elite", "legend"]
        for cls in classes:
            for stage in stages:
                title = get_evolution_title(cls, stage)
                assert title is not None
                assert len(title) > 0

        assert get_evolution_title("WARRIOR", "hero") == "Warlord"
        assert get_evolution_title("SCHOLAR", "hero") == "Sage"
        assert get_evolution_title("CREATOR", "hero") == "Master Creator"
        assert get_evolution_title("GUARDIAN", "hero") == "Sentinel"
        assert get_evolution_title("EXPLORER", "legend") == "Living Legend"

    def test_next_evolution_stage(self):
        """Test next evolution stage calculation."""
        assert get_next_evolution_stage("novice") == "adventurer"
        assert get_next_evolution_stage("adventurer") == "hero"
        assert get_next_evolution_stage("hero") == "elite"
        assert get_next_evolution_stage("elite") == "legend"
        assert get_next_evolution_stage("legend") is None

    def test_evolution_requirements(self):
        """Test evolution level requirements."""
        assert get_evolution_requirements("novice") == 1
        assert get_evolution_requirements("adventurer") == 5
        assert get_evolution_requirements("hero") == 10
        assert get_evolution_requirements("elite") == 20
        assert get_evolution_requirements("legend") == 30

    def test_evolution_info_payload(self):
        """Test full evolution info generation including cosmetic unlocks."""
        info = build_evolution_payload(level=12, character_class="WARRIOR")
        assert info["stage"] == "hero"
        assert info["title"] == "Warlord"
        assert info["nextStage"] == "elite"
        assert info["nextRequirement"] == 20
        assert info["cosmetics"]["frame"] == "silver"
        assert "unlocked" in info["cosmetics"]


class TestCharacterEvolutionAPI:
    """Tests for Character Evolution API integration."""

    def test_character_includes_evolution(self, client, auth_header):
        """Test that character API includes evolution data."""
        response = client.get("/api/character", headers=auth_header)
        assert response.status_code == 200
        data = response.json
        assert "evolution" in data
        evolution = data["evolution"]
        assert "stage" in evolution
        assert "display" in evolution
        assert "title" in evolution
        assert "level" in evolution

    def test_evolution_endpoint_and_ack(self, client, auth_header):
        """Test evolution retrieval and acknowledgment endpoint."""
        res = client.get("/api/character/evolution", headers=auth_header)
        assert res.status_code == 200
        assert "stage" in res.json

        # Acknowledge stage
        ack_res = client.post(
            "/api/character/evolution/ack",
            headers=auth_header,
            json={"stage": "novice"},
        )
        assert ack_res.status_code == 200
        assert ack_res.json["stage"] == "novice"
        assert ack_res.json["justEvolved"] is False


class TestChronicle:
    """Tests for Daily Chronicle system."""

    def test_chronicle_returns_data(self, app, phase4_user):
        """Test that chronicle returns data structure."""
        with app.app_context():
            chronicle = get_daily_chronicle(phase4_user)
            assert chronicle is not None
            assert "date" in chronicle
            assert "title" in chronicle
            assert "stats" in chronicle
            assert "quests" in chronicle
            assert "bossActivity" in chronicle

    def test_chronicle_stats_structure(self, app, phase4_user):
        """Test chronicle stats structure."""
        with app.app_context():
            chronicle = get_daily_chronicle(phase4_user)
            stats = chronicle["stats"]
            assert "questsCompleted" in stats
            assert "xpGained" in stats
            assert "goldGained" in stats
            assert "bossDefeated" in stats
            assert "attributeGains" in stats

    def test_chronicle_history(self, app, phase4_user):
        """Test chronicle history retrieval."""
        with app.app_context():
            history = get_chronicle_history(phase4_user, days=7)
            assert isinstance(history, list)
            assert len(history) == 7
            for entry in history:
                assert "date" in entry
                assert "title" in entry

    def test_chronicle_event_logging_and_aggregation(self, app, phase4_user):
        """Test that logged chronicle events correctly populate daily stats."""
        with app.app_context():
            log_chronicle_event(phase4_user, "boss_damage", {"damage": 150, "bossTitle": "Shadow Beast"})
            log_chronicle_event(phase4_user, "level_up", {"level": 5})
            log_chronicle_event(phase4_user, "attribute_gain", {"strength": 2, "vitality": 1})
            db.session.commit()

            chronicle = get_daily_chronicle(phase4_user)
            assert chronicle["stats"]["bossDamage"] == 150
            assert chronicle["stats"]["levelUps"] == 1
            assert chronicle["stats"]["attributeGains"]["strength"] == 2
            assert chronicle["stats"]["attributeGains"]["vitality"] == 1
            assert chronicle["title"] == "The Day of Ascension"

    def test_chronicle_user_isolation(self, app, phase4_user):
        """Test that one user's chronicle events are not visible to another user."""
        with app.app_context():
            user2 = User(
                username="p4_user_isolation",
                email="p4_user_isolation@example.com",
                display_name="User Isolation",
                password_hash="hashed_password",
            )
            db.session.add(user2)
            db.session.commit()
            user2_id = user2.id

            log_chronicle_event(phase4_user, "boss_damage", {"damage": 500, "bossTitle": "Titan"})
            db.session.commit()

            chronicle1 = get_daily_chronicle(phase4_user)
            chronicle2 = get_daily_chronicle(user2_id)

            assert chronicle1["stats"]["bossDamage"] == 500
            assert chronicle2["stats"]["bossDamage"] == 0

    def test_chronicle_api_endpoint(self, client, auth_header):
        """Test Chronicle API endpoint."""
        response = client.get("/api/chronicle/today", headers=auth_header)
        assert response.status_code == 200
        data = response.json
        assert "date" in data
        assert "hasActivity" in data

    def test_chronicle_history_api(self, client, auth_header):
        """Test Chronicle history API endpoint."""
        response = client.get("/api/chronicle/history?days=7", headers=auth_header)
        assert response.status_code == 200
        data = response.json
        assert isinstance(data, list)
        assert len(data) == 7

