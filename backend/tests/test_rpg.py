"""Tests for Phase 2 RPG features."""
import pytest
from app import create_app
from app.extensions import db
from app.models import User, Attributes, Quest, Skill, UserSkill
from app.services import apply_quest_reward, calculate_attribute_gain
from app.rpg_utils import calculate_character_class, get_attribute_for_category, get_attribute_tier


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret",
        "JWT_SECRET_KEY": "test-jwt-secret",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed",
        display_name="Test User",
        title="Adventurer",
        level=5,
        xp=250,
        xp_to_next=500,
        gold=100,
        skill_points=3,
    )
    db.session.add(user)
    db.session.flush()
    db.session.add(Attributes(user_id=user.id))
    db.session.commit()
    return user


def test_category_to_attribute_mapping():
    """Test that categories map to correct attributes."""
    assert get_attribute_for_category("Work") == "Discipline"
    assert get_attribute_for_category("Learning") == "Intelligence"
    assert get_attribute_for_category("Health") == "Strength"
    assert get_attribute_for_category("Creative") == "Creativity"
    assert get_attribute_for_category("Wellness") == "Vitality"
    assert get_attribute_for_category("Unknown") == "Discipline"  # Default


def test_attribute_tier_calculation():
    """Test attribute tier thresholds."""
    assert get_attribute_tier(0) == "Novice"
    assert get_attribute_tier(15) == "Novice"
    assert get_attribute_tier(20) == "Apprentice"
    assert get_attribute_tier(40) == "Skilled"
    assert get_attribute_tier(60) == "Expert"
    assert get_attribute_tier(80) == "Master"
    assert get_attribute_tier(100) == "Legendary"


def test_character_class_warrior():
    """Test Warrior class calculation (high Strength + Vitality)."""
    attrs = {"strength": 85, "intelligence": 30, "discipline": 40, "creativity": 25, "vitality": 80}
    assert calculate_character_class(attrs) == "WARRIOR"


def test_character_class_scholar():
    """Test Scholar class calculation (high Intelligence)."""
    attrs = {"strength": 30, "intelligence": 90, "discipline": 40, "creativity": 35, "vitality": 35}
    assert calculate_character_class(attrs) == "SCHOLAR"


def test_character_class_creator():
    """Test Creator class calculation (high Creativity)."""
    attrs = {"strength": 30, "intelligence": 40, "discipline": 40, "creativity": 85, "vitality": 30}
    assert calculate_character_class(attrs) == "CREATOR"


def test_character_class_guardian():
    """Test Guardian class calculation (high Discipline + Vitality)."""
    attrs = {"strength": 40, "intelligence": 35, "discipline": 80, "creativity": 30, "vitality": 70}
    assert calculate_character_class(attrs) == "GUARDIAN"


def test_character_class_explorer():
    """Test Explorer class calculation (balanced/low stats)."""
    attrs = {"strength": 30, "intelligence": 35, "discipline": 30, "creativity": 30, "vitality": 30}
    assert calculate_character_class(attrs) == "EXPLORER"


def test_character_class_master_adventurer():
    """Test Master Adventurer class (high balanced stats)."""
    attrs = {"strength": 65, "intelligence": 65, "discipline": 65, "creativity": 65, "vitality": 65}
    assert calculate_character_class(attrs) == "MASTER_ADVENTURER"


def test_attribute_gain_calculation():
    """Test attribute point calculation based on XP."""
    # Easy quest (60 XP) = 3 points
    assert calculate_attribute_gain(60) == 3
    # Medium quest (130 XP) = 6 points
    assert calculate_attribute_gain(130) == 6
    # Hard quest (220 XP) = 11 points
    assert calculate_attribute_gain(220) == 11
    # Minimum 1 point
    assert calculate_attribute_gain(10) == 1


def test_attribute_gain_prevents_negative(app):
    """Test that attribute gain cannot be negative."""
    with app.app_context():
        user = User(
            username="test",
            email="test@example.com",
            password_hash="hash",
            display_name="Test",
        )
        db.session.add(user)
        db.session.flush()
        attrs = Attributes(user_id=user.id, strength=0)
        db.session.add(attrs)
        db.session.commit()
        
        # Try to bump negative (should stay at 0)
        attrs.bump("strength", amount=-5)
        assert attrs.strength == 0


def test_attribute_gain_prevents_overflow(app):
    """Test that attribute gain cannot exceed 100."""
    with app.app_context():
        user = User(
            username="test",
            email="test@example.com",
            password_hash="hash",
            display_name="Test",
        )
        db.session.add(user)
        db.session.flush()
        attrs = Attributes(user_id=user.id, strength=95)
        db.session.add(attrs)
        db.session.commit()
        
        # Try to bump beyond 100 (should cap at 100)
        attrs.bump("strength", amount=20)
        assert attrs.strength == 100


def test_quest_reward_includes_attribute_gains(user):
    """Test that quest rewards include attribute gains in events."""
    quest = Quest(
        user_id=user.id,
        title="Test Quest",
        category="Work",
        difficulty="EASY",
        attribute="Discipline",
        xp_reward=60,
        gold_reward=15,
        status="ACTIVE",
    )
    db.session.add(quest)
    db.session.commit()
    
    events = apply_quest_reward(user, quest)
    
    assert "attributeGains" in events
    assert "Discipline" in events["attributeGains"]
    assert events["attributeGains"]["Discipline"] > 0


def test_skill_points_awarded_on_level_up(user):
    """Test that skill points are awarded on level-up."""
    old_points = user.skill_points
    user.xp = 500  # Enough to level up from 5 to 6
    user.xp_to_next = 500
    
    from app.services import apply_xp
    levels_gained = apply_xp(user, 0)  # Already has XP
    
    assert user.skill_points == old_points + levels_gained


def test_multi_level_awards_multiple_skill_points(user):
    """Test that multi-level-up awards multiple skill points."""
    old_points = user.skill_points
    user.xp = 0  # Reset to 0
    user.xp_to_next = 500
    
    from app.services import apply_xp
    levels_gained = apply_xp(user, 1500)  # Add enough XP for multiple levels
    
    assert user.skill_points == old_points + levels_gained
    assert levels_gained >= 2


def test_onboarding_fields_in_user(app):
    """Test that onboarding fields exist in User model."""
    with app.app_context():
        user = User(
            username="test",
            email="test@example.com",
            password_hash="hash",
            display_name="Test",
        )
        db.session.add(user)
        db.session.commit()
        
        assert hasattr(user, "onboarding_completed")
        assert hasattr(user, "life_goals")
        assert user.onboarding_completed == False


def test_skill_model_exists(app):
    """Test that Skill model exists and has required fields."""
    with app.app_context():
        skill = Skill(
            name="Test Skill",
            description="Test description",
            attribute="Strength",
            cost=1,
            effect_type="xp_boost",
            effect_value=5,
            icon="✨",
        )
        db.session.add(skill)
        db.session.commit()
        
        assert skill.id is not None
        assert skill.name == "Test Skill"
        assert skill.cost == 1


def test_user_skill_model_exists(app):
    """Test that UserSkill model exists and links user to skill."""
    with app.app_context():
        user = User(
            username="test",
            email="test@example.com",
            password_hash="hash",
            display_name="Test",
        )
        db.session.add(user)
        db.session.flush()
        
        skill = Skill(
            name="Test Skill",
            description="Test",
            attribute="Strength",
            cost=1,
            effect_type="xp_boost",
            effect_value=5,
            icon="✨",
        )
        db.session.add(skill)
        db.session.flush()
        
        user_skill = UserSkill(user_id=user.id, skill_id=skill.id)
        db.session.add(user_skill)
        db.session.commit()
        
        assert user_skill.id is not None
        assert user_skill.user_id == user.id
        assert user_skill.skill_id == skill.id
