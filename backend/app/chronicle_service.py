"""Daily Chronicle — deterministic aggregation with optional AI titles."""
import json
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List

from app.extensions import db
from app.models import (
    Quest, XPLog, Boss, UserSkill, UserAchievement, Achievement, ChronicleEvent,
)
from app.rpg_utils import get_attribute_for_category, get_region_for_category, REGIONS


def _utc_today() -> date:
    return datetime.now(timezone.utc).date()


def log_chronicle_event(user_id: int, event_type: str, payload: Dict[str, Any], event_date=None):
    """Append an activity event. Caller is responsible for committing."""
    event = ChronicleEvent(
        user_id=user_id,
        event_type=event_type,
        event_date=event_date or _utc_today(),
        payload=json.dumps(payload or {}),
    )
    db.session.add(event)
    return event


def _payload(event) -> dict:
    try:
        return json.loads(event.payload or "{}")
    except (TypeError, ValueError):
        return {}


def _day_bounds(target_date: date):
    start = datetime.combine(target_date, datetime.min.time())
    end = datetime.combine(target_date, datetime.max.time())
    return start, end


def _deterministic_title(stats: dict, events_by_type: dict) -> str:
    if stats.get("bossDefeated"):
        bosses = events_by_type.get("boss_defeated") or []
        if bosses:
            name = _payload(bosses[0]).get("title") or "the Boss"
            return f"The Day of the {name} Battle"
        return "The Day of Victory"
    if stats.get("levelUps"):
        return "The Day of Ascension"
    if stats.get("skillsUnlocked"):
        return "The Scholar's Return"
    regions = events_by_type.get("region_milestone") or []
    if regions:
        region = _payload(regions[0]).get("regionName") or "the Realm"
        return f"{region} Progress Day"
    if stats.get("questsCompleted", 0) >= 5:
        return "The Productive Day"
    if stats.get("questsCompleted", 0) >= 3:
        return "The Balanced Day"
    if stats.get("questsCompleted", 0) >= 1:
        return "The Journey Continues"
    return "A Day of Rest"


def _maybe_ai_title(stats: dict, fallback: str) -> str:
    if stats.get("questsCompleted", 0) == 0 and not stats.get("bossDefeated"):
        return fallback
    from app.game_master_service import game_master
    if not game_master.is_available():
        return fallback
    try:
        raw = game_master._http_chat(
            "You name RPG journal entries. Return JSON {\"title\": \"...\"} only. Max 8 words. No quotes in the title.",
            json.dumps({"stats": stats, "fallback": fallback}),
        )
        data = json.loads(game_master._extract_json(raw))
        title = (data.get("title") or "").strip()[:80]
        return title or fallback
    except Exception:
        return fallback


def get_daily_chronicle(user_id: int, target_date: date = None) -> Dict[str, Any]:
    if target_date is None:
        target_date = _utc_today()
    start, end = _day_bounds(target_date)

    xp_log = XPLog.query.filter_by(user_id=user_id, log_date=target_date).first()

    completed_quests = Quest.query.filter(
        Quest.user_id == user_id,
        Quest.status == "COMPLETED",
        Quest.completed_at >= start,
        Quest.completed_at <= end,
    ).all()

    events = ChronicleEvent.query.filter_by(user_id=user_id, event_date=target_date).order_by(
        ChronicleEvent.created_at.asc()
    ).all()
    events_by_type: Dict[str, list] = {}
    for ev in events:
        events_by_type.setdefault(ev.event_type, []).append(ev)

    skills = []
    for ev in events_by_type.get("skill_unlocked", []):
        skills.append(_payload(ev))
    if not skills:
        rows = (
            UserSkill.query.filter(
                UserSkill.user_id == user_id,
                UserSkill.unlocked_at >= start,
                UserSkill.unlocked_at <= end,
            ).all()
        )
        skills = [{"id": r.skill_id, "name": r.skill.name if r.skill else "Skill"} for r in rows]

    achievements = []
    for ev in events_by_type.get("achievement", []):
        achievements.append(_payload(ev))
    if not achievements:
        uas = UserAchievement.query.filter(
            UserAchievement.user_id == user_id,
            UserAchievement.unlocked_at >= start,
            UserAchievement.unlocked_at <= end,
        ).all()
        for ua in uas:
            ach = Achievement.query.get(ua.achievement_id)
            if ach:
                achievements.append({"id": ach.id, "title": ach.title, "icon": ach.icon})

    boss_damage_events = [_payload(ev) for ev in events_by_type.get("boss_damage", [])]
    boss_phase_events = [_payload(ev) for ev in events_by_type.get("boss_phase", [])]
    boss_defeated_events = [_payload(ev) for ev in events_by_type.get("boss_defeated", [])]
    if not boss_defeated_events:
        defeated = Boss.query.filter_by(user_id=user_id, status="defeated").all()
        for b in defeated:
            stamp = b.updated_at
            if stamp and stamp.date() == target_date:
                boss_defeated_events.append({"id": b.id, "title": b.title, "category": b.category})

    level_ups = [_payload(ev) for ev in events_by_type.get("level_up", [])]
    region_milestones = [_payload(ev) for ev in events_by_type.get("region_milestone", [])]
    region_milestones += [_payload(ev) for ev in events_by_type.get("region_progress", [])]

    attribute_gains: Dict[str, int] = {}
    for ev in events_by_type.get("attribute_gain", []):
        payload = _payload(ev)
        for key, val in payload.items():
            try:
                attribute_gains[key] = attribute_gains.get(key, 0) + int(val)
            except (TypeError, ValueError):
                continue
    if not attribute_gains:
        for quest in completed_quests:
            attr = get_attribute_for_category(quest.category)
            if attr:
                attribute_gains[attr] = attribute_gains.get(attr, 0) + 1

    total_xp = xp_log.xp_earned if xp_log else sum(q.xp_reward or 0 for q in completed_quests)
    total_gold = xp_log.gold_earned if xp_log else sum(q.gold_reward or 0 for q in completed_quests)
    total_boss_damage = sum(int(e.get("damage") or 0) for e in boss_damage_events)

    stats = {
        "questsCompleted": len(completed_quests),
        "xpGained": total_xp,
        "goldGained": total_gold,
        "attributeGains": attribute_gains,
        "bossDamage": total_boss_damage,
        "bossDefeated": len(boss_defeated_events),
        "levelUps": len(level_ups),
        "skillsUnlocked": len(skills),
        "achievements": len(achievements),
        "regionMilestones": len(region_milestones),
    }

    title = _deterministic_title(stats, events_by_type)
    title = _maybe_ai_title(stats, title)

    return {
        "date": target_date.isoformat(),
        "title": title,
        "stats": stats,
        "quests": [
            {
                "id": q.id,
                "title": q.title,
                "category": q.category,
                "difficulty": q.difficulty,
                "xpReward": q.xp_reward,
                "goldReward": q.gold_reward,
                "region": REGIONS.get(get_region_for_category(q.category), {}).get("name"),
            }
            for q in completed_quests
        ],
        "levelUps": level_ups,
        "skills": skills,
        "achievements": achievements,
        "regionProgress": region_milestones,
        "bossActivity": {
            "damageEvents": boss_damage_events,
            "phaseChanges": boss_phase_events,
            "defeatedBosses": boss_defeated_events,
            "totalDamage": total_boss_damage,
        },
        "hasActivity": (
            stats["questsCompleted"] > 0
            or stats["xpGained"] > 0
            or stats["bossDefeated"] > 0
            or stats["levelUps"] > 0
            or stats["skillsUnlocked"] > 0
        ),
    }


def get_chronicle_history(user_id: int, days: int = 30) -> List[Dict[str, Any]]:
    history = []
    today = _utc_today()
    for i in range(days):
        history.append(get_daily_chronicle(user_id, today - timedelta(days=i)))
    return history


def get_today_summary(user_id: int) -> Dict[str, Any]:
    chronicle = get_daily_chronicle(user_id, _utc_today())
    return {
        "date": chronicle["date"],
        "title": chronicle["title"],
        "questsCompleted": chronicle["stats"]["questsCompleted"],
        "xpGained": chronicle["stats"]["xpGained"],
        "goldGained": chronicle["stats"]["goldGained"],
        "bossDamage": chronicle["stats"]["bossDamage"],
        "levelUps": chronicle["stats"]["levelUps"],
        "hasActivity": chronicle["hasActivity"],
        "quests": chronicle["quests"][:5],
    }
