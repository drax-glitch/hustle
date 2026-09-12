from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.utils import get_user_id, get_current_user, validation_error
from app.world_services import (
    get_world_data, get_region_detail, create_boss, link_quest_to_boss,
    unlink_quest_from_boss, grant_boss_rewards,
)
from app.models import Boss, BossQuest

world_bp = Blueprint("world", __name__, url_prefix="/api/world")


@world_bp.get("")
@jwt_required()
def get_world():
    """Get world data including regions and active bosses."""
    user_id = get_user_id()
    world_data = get_world_data(user_id)
    return jsonify(world_data)


@world_bp.get("/regions/<region_id>")
@jwt_required()
def get_region(region_id):
    """Get detailed information about a specific region."""
    user_id = get_user_id()
    try:
        region_data = get_region_detail(user_id, region_id)
        return jsonify(region_data)
    except ValueError as e:
        return validation_error(str(e))


bosses_bp = Blueprint("bosses", __name__, url_prefix="/api/bosses")


@bosses_bp.get("")
@jwt_required()
def list_bosses():
    """Get all bosses for the current user."""
    user_id = get_user_id()
    bosses = Boss.query.filter_by(user_id=user_id).all()
    return jsonify([boss.to_dict() for boss in bosses])


@bosses_bp.get("/<int:boss_id>")
@jwt_required()
def get_boss(boss_id):
    """Get detailed information about a specific boss."""
    user_id = get_user_id()
    boss = Boss.query.filter_by(id=boss_id, user_id=user_id).first()
    if not boss:
        return validation_error("Boss not found")
    
    # Get linked quests
    linked_quests = BossQuest.query.filter_by(boss_id=boss_id).all()
    quest_data = []
    for bq in linked_quests:
        if bq.quest:
            quest_data.append(bq.quest.to_dict())
    
    boss_dict = boss.to_dict()
    boss_dict["linkedQuests"] = quest_data
    
    return jsonify(boss_dict)


@bosses_bp.post("")
@jwt_required()
def create_boss_endpoint():
    """Create a new boss battle."""
    user = get_current_user()
    data = request.get_json() or {}
    
    title = data.get("title", "").strip()
    if not title or len(title) > 150:
        return validation_error("Title must be 1-150 characters")
    
    description = data.get("description", "").strip()
    if not description or len(description) > 500:
        return validation_error("Description must be 1-500 characters")
    
    category = data.get("category", "")
    if category not in ["Health", "Learning", "Work", "Creative", "Wellness"]:
        return validation_error("Invalid category")
    
    difficulty = data.get("difficulty", "MEDIUM")
    if difficulty not in ["EASY", "MEDIUM", "HARD", "EPIC"]:
        return validation_error("Invalid difficulty")
    
    deadline = data.get("deadline")  # Optional
    
    boss_data = {
        "title": title,
        "description": description,
        "category": category,
        "difficulty": difficulty,
        "deadline": deadline,
    }
    
    boss = create_boss(user.id, boss_data)
    return jsonify(boss.to_dict()), 201


@bosses_bp.post("/<int:boss_id>/quests")
@jwt_required()
def link_quest(boss_id):
    """Link a quest to a boss."""
    user_id = get_user_id()
    data = request.get_json() or {}
    quest_id = data.get("questId")
    
    if not quest_id:
        return validation_error("questId is required")
    
    try:
        boss_quest = link_quest_to_boss(boss_id, quest_id, user_id)
        return jsonify({"success": True}), 201
    except ValueError as e:
        return validation_error(str(e))


@bosses_bp.delete("/<int:boss_id>/quests/<int:quest_id>")
@jwt_required()
def unlink_quest(boss_id, quest_id):
    """Unlink a quest from a boss."""
    user_id = get_user_id()
    try:
        unlink_quest_from_boss(boss_id, quest_id, user_id)
        return jsonify({"success": True})
    except ValueError as e:
        return validation_error(str(e))


@bosses_bp.post("/<int:boss_id>/claim-rewards")
@jwt_required()
def claim_rewards(boss_id):
    """Claim rewards for a defeated boss."""
    user = get_current_user()
    boss = Boss.query.filter_by(id=boss_id, user_id=user.id).first()
    
    if not boss:
        return validation_error("Boss not found")
    
    if boss.status != "defeated":
        return validation_error("Boss must be defeated to claim rewards")
    
    if boss.reward_claimed:
        return validation_error("Rewards for this boss have already been claimed")
    
    rewards = grant_boss_rewards(boss, user)
    
    return jsonify(rewards)
