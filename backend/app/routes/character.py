from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import Quest, UserInventory, ShopItem, UserSkill, Skill
from app.utils import get_user_id, get_current_user
from app.rpg_utils import (
    get_attribute_tier,
    calculate_character_class,
    CHARACTER_CLASSES,
    build_evolution_payload,
)

character_bp = Blueprint("character", __name__, url_prefix="/api/character")


@character_bp.get("")
@jwt_required()
def get_character():
    user_id = get_user_id()
    user = get_current_user()
    quests_done = Quest.query.filter_by(user_id=user_id, status="COMPLETED").count()

    equipped_rows = (
        UserInventory.query.join(ShopItem)
        .filter(UserInventory.user_id == user_id, UserInventory.equipped.is_(True))
        .all()
    )
    equipped = [
        {"category": row.item.category, "name": row.item.name, "icon": row.item.icon, "itemId": row.item_id}
        for row in equipped_rows
    ]

    # Add tier information to attributes
    attrs = user.attributes.to_dict() if user.attributes else {}
    attrs_with_tiers = {
        "strength": {"value": attrs.get("strength", 0), "tier": get_attribute_tier(attrs.get("strength", 0))},
        "intelligence": {"value": attrs.get("intelligence", 0), "tier": get_attribute_tier(attrs.get("intelligence", 0))},
        "discipline": {"value": attrs.get("discipline", 0), "tier": get_attribute_tier(attrs.get("discipline", 0))},
        "creativity": {"value": attrs.get("creativity", 0), "tier": get_attribute_tier(attrs.get("creativity", 0))},
        "vitality": {"value": attrs.get("vitality", 0), "tier": get_attribute_tier(attrs.get("vitality", 0))},
    }

    # Include class information in character response
    class_key = calculate_character_class(attrs)
    class_info = CHARACTER_CLASSES.get(class_key, CHARACTER_CLASSES["EXPLORER"])

    evolution = build_evolution_payload(user.level, class_key, user.seen_evolution_stage)

    # Get unlocked skills
    unlocked_skills = (
        UserSkill.query.join(Skill)
        .filter(UserSkill.user_id == user_id)
        .all()
    )
    skills_data = [
        {
            "id": us.skill.id,
            "name": us.skill.name,
            "description": us.skill.description,
            "attribute": us.skill.attribute,
            "icon": us.skill.icon,
            "effectType": us.skill.effect_type,
            "effectValue": us.skill.effect_value,
        }
        for us in unlocked_skills
    ]

    return jsonify({
        "user": user.to_dict(quests_done),
        "attributes": attrs_with_tiers,
        "equipped": equipped,
        "class": {
            "key": class_key,
            "name": class_info["name"],
            "icon": class_info["icon"],
            "description": class_info["description"],
            "color": class_info["color"],
        },
        "evolution": evolution,
        "skills": skills_data,
    })


@character_bp.get("/evolution")
@jwt_required()
def get_evolution():
    user = get_current_user()
    attrs = user.attributes.to_dict() if user.attributes else {}
    class_key = calculate_character_class(attrs)
    return jsonify(build_evolution_payload(user.level, class_key, user.seen_evolution_stage))


@character_bp.post("/evolution/ack")
@jwt_required()
def ack_evolution():
    """Mark the current evolution stage as seen so the milestone does not repeat."""
    user = get_current_user()
    attrs = user.attributes.to_dict() if user.attributes else {}
    class_key = calculate_character_class(attrs)
    payload = build_evolution_payload(user.level, class_key, user.seen_evolution_stage)
    user.seen_evolution_stage = payload["stage"]
    db.session.commit()
    payload["justEvolved"] = False
    return jsonify(payload)
