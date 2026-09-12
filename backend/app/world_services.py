"""World and Boss system services."""
from datetime import datetime
from app.extensions import db
from app.models import Quest, Boss, BossQuest
from app.rpg_utils import (
    REGIONS, get_region_for_category, calculate_region_progress,
    get_region_stage, get_region_stage_display, calculate_world_progress,
    calculate_boss_damage, calculate_boss_phase, get_phase_name, BOSS_DIFFICULTY,
)


def get_world_data(user_id: int) -> dict:
    """
    Calculate world progress data for a user.
    Returns region progresses, world progress, and active bosses.
    """
    region_data = {}
    
    for region_id, region_info in REGIONS.items():
        # Count completed quests for this region's category
        completed_count = Quest.query.filter(
            Quest.user_id == user_id,
            Quest.category == region_info["category"],
            Quest.status == "COMPLETED"
        ).count()
        
        # Count total quests for this region's category
        total_count = Quest.query.filter(
            Quest.user_id == user_id,
            Quest.category == region_info["category"]
        ).count()
        
        progress = calculate_region_progress(region_info["category"], completed_count, total_count)
        stage = get_region_stage(progress)
        stage_display = get_region_stage_display(stage)
        
        region_data[region_id] = {
            **region_info,
            "progress": progress,
            "stage": stage,
            "stageDisplay": stage_display,
            "completedQuests": completed_count,
            "totalQuests": total_count,
        }
    
    world_progress = calculate_world_progress({k: v["progress"] for k, v in region_data.items()})
    
    # Get active bosses
    active_bosses = Boss.query.filter(
        Boss.user_id == user_id,
        Boss.status == "active"
    ).all()
    
    return {
        "regions": region_data,
        "worldProgress": world_progress,
        "activeBosses": [boss.to_dict() for boss in active_bosses],
    }


def get_region_detail(user_id: int, region_id: str) -> dict:
    """
    Get detailed information about a specific region.
    """
    if region_id not in REGIONS:
        raise ValueError(f"Invalid region: {region_id}")
    
    region_info = REGIONS[region_id]
    
    # Get region quests
    quests = Quest.query.filter(
        Quest.user_id == user_id,
        Quest.category == region_info["category"]
    ).all()
    
    completed_quests = [q for q in quests if q.status == "COMPLETED"]
    active_quests = [q for q in quests if q.status == "ACTIVE"]
    
    # Calculate progress
    completed_count = len(completed_quests)
    total_count = len(quests)
    progress = calculate_region_progress(region_info["category"], completed_count, total_count)
    stage = get_region_stage(progress)
    stage_display = get_region_stage_display(stage)
    
    # Get active boss for this region
    active_boss = Boss.query.filter(
        Boss.user_id == user_id,
        Boss.category == region_info["category"],
        Boss.status == "active"
    ).first()
    
    return {
        "region": {
            **region_info,
            "progress": progress,
            "stage": stage,
            "stageDisplay": stage_display,
            "completedQuests": completed_count,
            "totalQuests": total_count,
        },
        "quests": [q.to_dict() for q in quests],
        "activeBoss": active_boss.to_dict() if active_boss else None,
    }


def create_boss(user_id: int, boss_data: dict) -> Boss:
    """
    Create a new boss battle.
    """
    from datetime import date, datetime
    from app.rpg_utils import BOSS_DIFFICULTY
    
    difficulty = boss_data.get("difficulty", "MEDIUM")
    config = BOSS_DIFFICULTY.get(difficulty, BOSS_DIFFICULTY["MEDIUM"])
    
    deadline_val = boss_data.get("deadline")
    if isinstance(deadline_val, str) and deadline_val.strip():
        try:
            deadline_val = date.fromisoformat(deadline_val.split("T")[0])
        except Exception:
            deadline_val = None
    elif not isinstance(deadline_val, date):
        deadline_val = None

    boss = Boss(
        user_id=user_id,
        title=boss_data["title"],
        description=boss_data["description"],
        category=boss_data["category"],
        max_hp=config["max_hp"],
        current_hp=config["max_hp"],
        difficulty=difficulty,
        deadline=deadline_val,
    )
    
    db.session.add(boss)
    db.session.commit()
    
    return boss


def apply_boss_damage(boss: Boss, quest_xp: int) -> dict:
    """
    Apply damage to a boss from quest completion.
    Returns damage dealt and phase change info.
    """
    old_phase = calculate_boss_phase(boss.current_hp, boss.max_hp)
    
    damage = calculate_boss_damage(quest_xp, boss.difficulty)
    boss.current_hp = max(0, boss.current_hp - damage)
    boss.updated_at = datetime.now()
    
    new_phase = calculate_boss_phase(boss.current_hp, boss.max_hp)
    
    result = {
        "damage": damage,
        "oldHp": boss.current_hp + damage,
        "newHp": boss.current_hp,
        "hpPercent": int((boss.current_hp / boss.max_hp) * 100) if boss.max_hp > 0 else 0,
        "phaseChanged": new_phase != old_phase,
        "oldPhase": old_phase,
        "newPhase": new_phase,
        "oldPhaseName": get_phase_name(old_phase),
        "newPhaseName": get_phase_name(new_phase),
    }
    
    # Check for boss defeat
    if boss.current_hp <= 0 and boss.status == "active":
        boss.status = "defeated"
        result["defeated"] = True
    else:
        result["defeated"] = False
    
    db.session.commit()
    
    return result


def link_quest_to_boss(boss_id: int, quest_id: int, user_id: int) -> BossQuest:
    """
    Link a quest to a boss for damage dealing.
    """
    # Verify boss ownership
    boss = Boss.query.filter_by(id=boss_id, user_id=user_id).first()
    if not boss:
        raise ValueError("Boss not found or access denied")
    
    # Verify quest ownership
    quest = Quest.query.filter_by(id=quest_id, user_id=user_id).first()
    if not quest:
        raise ValueError("Quest not found or access denied")
    
    # Check if already linked
    existing = BossQuest.query.filter_by(boss_id=boss_id, quest_id=quest_id).first()
    if existing:
        raise ValueError("Quest already linked to this boss")
    
    boss_quest = BossQuest(boss_id=boss_id, quest_id=quest_id)
    db.session.add(boss_quest)
    db.session.commit()
    
    return boss_quest


def unlink_quest_from_boss(boss_id: int, quest_id: int, user_id: int):
    """
    Unlink a quest from a boss.
    """
    # Verify boss ownership
    boss = Boss.query.filter_by(id=boss_id, user_id=user_id).first()
    if not boss:
        raise ValueError("Boss not found or access denied")
    
    boss_quest = BossQuest.query.filter_by(boss_id=boss_id, quest_id=quest_id).first()
    if not boss_quest:
        raise ValueError("Quest not linked to this boss")
    
    db.session.delete(boss_quest)
    db.session.commit()


def grant_boss_rewards(boss: Boss, user) -> dict:
    """
    Grant rewards for defeating a boss.
    """
    from app.services import apply_xp
    
    boss_xp_reward = 1000
    boss_gold_reward = 500
    boss_skill_point_reward = 1
    
    # Apply XP (may trigger level-up)
    levels_gained = apply_xp(user, boss_xp_reward)
    
    # Grant gold
    user.gold += boss_gold_reward
    
    # Grant skill point
    user.skill_points += boss_skill_point_reward
    
    # Mark rewards as claimed
    boss.reward_claimed = True
    
    db.session.commit()
    
    return {
        "xpReward": boss_xp_reward,
        "goldReward": boss_gold_reward,
        "skillPointReward": boss_skill_point_reward,
        "levelsGained": levels_gained,
    }
