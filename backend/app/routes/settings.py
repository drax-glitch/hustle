from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import User, Attributes, Quest, UserAchievement, UserInventory, XPLog
from app.utils import get_user_id, get_current_user, validation_error
from app.rpg_utils import get_attribute_for_category

settings_bp = Blueprint("settings", __name__, url_prefix="/api/settings")

PROFILE_FIELDS = {"displayName": "display_name", "title": "title", "dailyGoal": "daily_goal"}
NOTIF_FIELDS = {
    "questReminders": "quest_reminders",
    "streakAlerts": "streak_alerts",
    "levelUpCelebrations": "levelup_celebrations",
    "achievementUnlocks": "achievement_unlocks",
}

STARTER_QUESTS = {
    "Health": [
        {"title": "Take a 20-minute walk", "difficulty": "EASY"},
        {"title": "Drink 8 glasses of water", "difficulty": "EASY"},
    ],
    "Knowledge": [
        {"title": "Read for 20 minutes", "difficulty": "EASY"},
        {"title": "Watch an educational video", "difficulty": "EASY"},
    ],
    "Career": [
        {"title": "Plan tomorrow's tasks", "difficulty": "EASY"},
        {"title": "Reply to important emails", "difficulty": "EASY"},
    ],
    "Discipline": [
        {"title": "Meditate for 10 minutes", "difficulty": "EASY"},
        {"title": "Review your goals", "difficulty": "EASY"},
    ],
    "Creativity": [
        {"title": "Write down 3 ideas", "difficulty": "EASY"},
        {"title": "Sketch or doodle something", "difficulty": "EASY"},
    ],
}


@settings_bp.patch("")
@jwt_required()
def update_settings():
    user = get_current_user()
    data = request.get_json() or {}

    if "displayName" in data:
        name = str(data["displayName"]).strip()
        if not name or len(name) > 80:
            return validation_error("displayName must be 1-80 characters")
        user.display_name = name

    if "title" in data:
        title = str(data["title"]).strip()
        if not title or len(title) > 80:
            return validation_error("title must be 1-80 characters")
        user.title = title

    if "dailyGoal" in data:
        goal = int(data["dailyGoal"])
        if goal < 1 or goal > 50:
            return validation_error("dailyGoal must be between 1 and 50")
        user.daily_goal = goal

    for incoming, column in NOTIF_FIELDS.items():
        if incoming in data:
            setattr(user, column, bool(data[incoming]))

    db.session.commit()
    return jsonify(user.to_dict())


@settings_bp.post("/reset-streak")
@jwt_required()
def reset_streak():
    user = get_current_user()
    user.streak = 0
    user.last_active_date = None
    db.session.commit()
    return jsonify({"streak": user.streak, "bestStreak": user.best_streak})


@settings_bp.post("/reset-character")
@jwt_required()
def reset_character():
    user_id = get_user_id()
    user = get_current_user()

    try:
        user.level = 1
        user.xp = 0
        user.xp_to_next = 500
        user.gold = 100
        user.streak = 0
        user.best_streak = 0
        user.skill_points = 0
        user.last_active_date = None
        user.daily_goal_bonus_date = None
        user.avatar = "🧙"
        user.title = "Adventurer"

        if user.attributes:
            user.attributes.strength = 0
            user.attributes.intelligence = 0
            user.attributes.discipline = 0
            user.attributes.creativity = 0
            user.attributes.vitality = 0

        Quest.query.filter_by(user_id=user_id).delete()
        UserAchievement.query.filter_by(user_id=user_id).delete()
        UserInventory.query.filter_by(user_id=user_id).delete()
        XPLog.query.filter_by(user_id=user_id).delete()

        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "reset failed"}), 500

    return jsonify(user.to_dict(quests_done=0))


@settings_bp.post("/complete-onboarding")
@jwt_required()
def complete_onboarding():
    """Complete onboarding by saving life goals and creating starter quests."""
    user = get_current_user()
    data = request.get_json() or {}
    
    life_goals = data.get("lifeGoals", [])
    if not isinstance(life_goals, list):
        return validation_error("lifeGoals must be an array")
    
    # Save life goals
    user.life_goals = ",".join(life_goals)
    user.onboarding_completed = True
    
    # Create starter quests based on selected goals
    created_quests = []
    for goal in life_goals:
        if goal in STARTER_QUESTS:
            for quest_data in STARTER_QUESTS[goal]:
                category_map = {
                    "Health": "Wellness",
                    "Knowledge": "Learning",
                    "Career": "Work",
                    "Discipline": "Work",
                    "Creativity": "Creative",
                }
                category = category_map.get(goal, "Work")
                
                quest = Quest(
                    user_id=user.id,
                    title=quest_data["title"],
                    category=category,
                    difficulty=quest_data["difficulty"],
                    attribute=get_attribute_for_category(category),
                    xp_reward=60,  # EASY reward
                    gold_reward=15,  # EASY reward
                    due_label="Today",
                    status="ACTIVE",
                )
                db.session.add(quest)
                created_quests.append(quest.to_dict())
    
    db.session.commit()
    
    return jsonify({
        "user": user.to_dict(),
        "starterQuests": created_quests,
    })
