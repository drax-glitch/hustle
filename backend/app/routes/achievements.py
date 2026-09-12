from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import Achievement, UserAchievement

achievements_bp = Blueprint("achievements", __name__, url_prefix="/api/achievements")


@achievements_bp.get("")
@jwt_required()
def list_achievements():
    user_id = get_jwt_identity()
    unlocked_ids = {
        ua.achievement_id
        for ua in UserAchievement.query.filter_by(user_id=user_id).all()
    }
    all_achievements = Achievement.query.all()

    result = [
        {
            "id": a.id,
            "code": a.code,
            "title": a.title,
            "description": a.description,
            "xpReward": a.xp_reward,
            "icon": a.icon,
            "unlocked": a.id in unlocked_ids,
        }
        for a in all_achievements
    ]
    return jsonify({
        "achievements": result,
        "unlockedCount": len(unlocked_ids),
        "totalCount": len(all_achievements),
    })
