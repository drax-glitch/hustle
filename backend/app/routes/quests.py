from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import Quest, User
from app.services import apply_quest_reward
from app.world_services import get_world_data
from app.rpg_utils import get_attribute_for_category
from app.utils import get_user_id, get_current_user, validate_quest_title, validation_error

quests_bp = Blueprint("quests", __name__, url_prefix="/api/quests")

DIFFICULTY_XP = {"EASY": 60, "MEDIUM": 130, "HARD": 220}
DIFFICULTY_GOLD = {"EASY": 15, "MEDIUM": 30, "HARD": 50}
VALID_CATEGORIES = {"Work", "Learning", "Health", "Creative", "Wellness"}
VALID_ATTRIBUTES = {"Strength", "Intelligence", "Discipline", "Creativity", "Vitality"}


def _user_summary(user):
    quests_done = Quest.query.filter_by(user_id=user.id, status="COMPLETED").count()
    return user.to_dict(quests_done)


@quests_bp.get("")
@jwt_required()
def list_quests():
    user_id = get_user_id()
    status = request.args.get("status")
    category = request.args.get("category")

    query = Quest.query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)
    if category and category != "All":
        query = query.filter_by(category=category)

    quests = query.order_by(Quest.created_at.desc()).all()
    return jsonify([q.to_dict() for q in quests])


@quests_bp.post("")
@jwt_required()
def create_quest():
    user_id = get_user_id()
    data = request.get_json() or {}

    title_error = validate_quest_title(data.get("title"))
    if title_error:
        return validation_error(title_error)

    difficulty = (data.get("difficulty") or "EASY").upper()
    if difficulty not in DIFFICULTY_XP:
        difficulty = "EASY"

    category = data.get("category", "Work")
    if category not in VALID_CATEGORIES:
        return validation_error("invalid category")

    # Use centralized category to attribute mapping
    attribute = get_attribute_for_category(category)
    if attribute not in VALID_ATTRIBUTES:
        return validation_error("invalid attribute")

    quest = Quest(
        user_id=user_id,
        title=data["title"].strip(),
        category=category,
        difficulty=difficulty,
        attribute=attribute,
        xp_reward=data.get("xpReward") or DIFFICULTY_XP[difficulty],
        gold_reward=data.get("goldReward") or DIFFICULTY_GOLD[difficulty],
        due_label=data.get("dueLabel", "Today")[:30],
    )
    db.session.add(quest)
    db.session.commit()
    return jsonify(quest.to_dict()), 201


@quests_bp.patch("/<int:quest_id>")
@jwt_required()
def update_quest(quest_id):
    user_id = get_user_id()
    quest = Quest.query.filter_by(id=quest_id, user_id=user_id).first_or_404()
    data = request.get_json() or {}

    if quest.status == "COMPLETED":
        return validation_error("completed quests cannot be edited")

    if "title" in data:
        title_error = validate_quest_title(data["title"])
        if title_error:
            return validation_error(title_error)
        quest.title = data["title"].strip()

    if "category" in data:
        if data["category"] not in VALID_CATEGORIES:
            return validation_error("invalid category")
        quest.category = data["category"]

    if "difficulty" in data:
        difficulty = data["difficulty"].upper()
        if difficulty not in DIFFICULTY_XP:
            return validation_error("invalid difficulty")
        quest.difficulty = difficulty
        if "xpReward" not in data:
            quest.xp_reward = DIFFICULTY_XP[difficulty]
        if "goldReward" not in data:
            quest.gold_reward = DIFFICULTY_GOLD[difficulty]

    if "attribute" in data:
        if data["attribute"] not in VALID_ATTRIBUTES:
            return validation_error("invalid attribute")
        quest.attribute = data["attribute"]

    if "dueLabel" in data:
        quest.due_label = str(data["dueLabel"])[:30]

    if "xpReward" in data:
        xp = int(data["xpReward"])
        if xp < 0 or xp > 10000:
            return validation_error("xpReward must be between 0 and 10000")
        quest.xp_reward = xp

    if "goldReward" in data:
        gold = int(data["goldReward"])
        if gold < 0 or gold > 10000:
            return validation_error("goldReward must be between 0 and 10000")
        quest.gold_reward = gold

    db.session.commit()
    return jsonify(quest.to_dict())


@quests_bp.patch("/<int:quest_id>/complete")
@jwt_required()
def complete_quest(quest_id):
    user_id = get_user_id()
    quest = Quest.query.filter_by(id=quest_id, user_id=user_id).first_or_404()
    user = get_current_user()

    if quest.status == "COMPLETED":
        return jsonify({"error": "quest already completed"}), 400

    try:
        world_before = get_world_data(user_id)
    except Exception:
        world_before = {"regions": {}}

    quest.status = "COMPLETED"
    quest.completed_at = datetime.now(timezone.utc)
    events = apply_quest_reward(user, quest, world_before=world_before)

    db.session.commit()
    return jsonify({
        "quest": quest.to_dict(),
        "user": _user_summary(user),
        "events": events,
    })


@quests_bp.delete("/<int:quest_id>")
@jwt_required()
def delete_quest(quest_id):
    user_id = get_user_id()
    quest = Quest.query.filter_by(id=quest_id, user_id=user_id).first_or_404()
    db.session.delete(quest)
    db.session.commit()
    return jsonify({"deleted": quest_id})
