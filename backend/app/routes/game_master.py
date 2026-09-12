"""Game Master API routes. Advice only — never mutates game state."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.models import Quest, Boss, BossQuest, Skill, UserSkill, XPLog
from app.game_master_service import game_master
from app.world_services import get_world_data
from app.rpg_utils import calculate_character_class, get_region_for_category, REGIONS, get_phase_name, calculate_boss_phase
from app.utils import get_user_id, get_current_user
from app.services import _utc_today

game_master_bp = Blueprint("game_master", __name__, url_prefix="/api/game-master")


def _gather_user_state(user):
    attrs = user.attributes.to_dict() if user.attributes else {}
    class_key = calculate_character_class(attrs) if attrs else "EXPLORER"

    state = {
        "user_id": user.id,
        "display_name": user.display_name,
        "level": user.level,
        "class": class_key,
        "attributes": {
            "Strength": attrs.get("strength", 0),
            "Intelligence": attrs.get("intelligence", 0),
            "Discipline": attrs.get("discipline", 0),
            "Creativity": attrs.get("creativity", 0),
            "Vitality": attrs.get("vitality", 0),
        },
        "skill_points": user.skill_points or 0,
        "streak": user.streak or 0,
        "life_goals": user.life_goals,
        "region_progress": {},
        "world_progress": 0,
        "active_boss": None,
        "unfinished_quests": [],
        "recommended_skill": None,
        "recent_activity": 0,
    }

    try:
        world_data = get_world_data(user.id)
        state["region_progress"] = {
            rid: world_data["regions"].get(rid, {}).get("progress", 0)
            for rid in REGIONS
        }
        state["world_progress"] = world_data.get("worldProgress", 0)
    except Exception:
        pass

    today = _utc_today()
    xp_log = XPLog.query.filter_by(user_id=user.id, log_date=today).first()
    state["recent_activity"] = xp_log.quests_done if xp_log else 0

    active_boss = Boss.query.filter_by(user_id=user.id, status="active").first()
    if active_boss:
        linked_ids = [bq.quest_id for bq in BossQuest.query.filter_by(boss_id=active_boss.id).all()]
        region_id = get_region_for_category(active_boss.category)
        phase = calculate_boss_phase(active_boss.current_hp, active_boss.max_hp)
        state["active_boss"] = {
            "id": active_boss.id,
            "title": active_boss.title,
            "category": active_boss.category,
            "region_name": REGIONS.get(region_id, {}).get("name"),
            "hp_percent": int((active_boss.current_hp / active_boss.max_hp) * 100) if active_boss.max_hp > 0 else 0,
            "linked_quest_ids": linked_ids,
            "phase": phase,
            "phase_name": get_phase_name(phase),
        }

    unfinished = (
        Quest.query.filter_by(user_id=user.id, status="ACTIVE")
        .order_by(Quest.created_at)
        .limit(12)
        .all()
    )
    state["unfinished_quests"] = [
        {
            "id": q.id,
            "title": q.title,
            "category": q.category,
            "difficulty": q.difficulty,
            "xp_reward": q.xp_reward,
            "region_name": REGIONS.get(get_region_for_category(q.category), {}).get("name"),
        }
        for q in unfinished
    ]

    if (user.skill_points or 0) > 0:
        unlocked_ids = {us.skill_id for us in UserSkill.query.filter_by(user_id=user.id).all()}
        for skill in Skill.query.order_by(Skill.cost.asc(), Skill.id.asc()).all():
            if skill.id in unlocked_ids:
                continue
            if skill.cost > (user.skill_points or 0):
                continue
            if skill.prerequisite_id and skill.prerequisite_id not in unlocked_ids:
                continue
            state["recommended_skill"] = {
                "id": skill.id,
                "name": skill.name,
                "attribute": skill.attribute,
            }
            break

    state["signals"] = game_master.compute_signals(state)
    return state


def _advice_payload(user, refresh=False):
    state = _gather_user_state(user)
    if refresh:
        game_master.clear_cache(user.id)
    advice = game_master.generate_advice(state, use_cache=not refresh)
    briefing = game_master.generate_briefing(state, advice)
    return {
        "advice": advice,
        "briefing": briefing,
        "source": advice.get("source", "fallback"),
        **advice,
    }


@game_master_bp.get("")
@jwt_required()
def get_game_master():
    user = get_current_user()
    refresh = request.args.get("refresh") in ("1", "true", "yes")
    return jsonify(_advice_payload(user, refresh=refresh))


@game_master_bp.get("/advice")
@jwt_required()
def get_game_master_advice():
    user = get_current_user()
    refresh = request.args.get("refresh") in ("1", "true", "yes")
    return jsonify(_advice_payload(user, refresh=refresh))


@game_master_bp.get("/briefing")
@jwt_required()
def get_game_master_briefing():
    user = get_current_user()
    payload = _advice_payload(user, refresh=False)
    return jsonify(payload["briefing"])


@game_master_bp.post("/advice")
@jwt_required()
def post_game_master_advice():
    """Explicit refresh. Does not modify XP, gold, attributes, bosses, or skills."""
    user = get_current_user()
    snapshot = {
        "xp": user.xp,
        "gold": user.gold,
        "level": user.level,
        "skill_points": user.skill_points,
    }
    payload = _advice_payload(user, refresh=True)
    user_after = get_current_user()
    payload["stateUnchanged"] = (
        user_after.xp == snapshot["xp"]
        and user_after.gold == snapshot["gold"]
        and user_after.level == snapshot["level"]
        and user_after.skill_points == snapshot["skill_points"]
    )
    return jsonify(payload)
