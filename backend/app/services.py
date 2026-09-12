from datetime import date, timedelta, datetime, timezone

def _utc_today() -> date:
    return datetime.now(timezone.utc).date()

from app.extensions import db
from app.models import (
    User, Quest, Achievement, UserAchievement, XPLog, UserInventory, ShopItem, UserSkill,
    EQUIPPABLE_CATEGORIES,
)
from app.rpg_utils import get_attribute_for_category, get_evolution_stage, get_region_for_category, build_evolution_payload

DAILY_GOAL_BONUS_XP = 75
DAILY_GOAL_BONUS_GOLD = 50
LEVEL_UP_GOLD_BONUS = 100


def apply_quest_reward(user: User, quest: Quest, world_before: dict = None) -> dict:
    """Apply XP/gold/attribute/streak/level effects of completing a quest."""
    old_level = user.level
    old_stage = get_evolution_stage(old_level)
    from app.world_services import get_world_data
    if world_before is None:
        world_before = {"regions": {}}

    events = {
        "oldLevel": old_level,
        "newLevel": old_level,
        "levelsGained": 0,
        "achievementsUnlocked": [],
        "dailyGoalCompleted": False,
        "dailyGoalBonus": None,
        "attributeGains": {},
        "bossDamage": None,
    }

    # Apply skill modifiers to XP
    modified_xp = apply_skill_modifiers(user, quest.xp_reward, quest.attribute)
    user.gold += quest.gold_reward
    apply_xp(user, modified_xp)

    if user.attributes:
        # Apply skill modifiers to attribute rewards
        base_attribute_gain = calculate_attribute_gain(quest.xp_reward)
        modified_attribute_gain = apply_skill_attribute_modifiers(user, quest.attribute, base_attribute_gain)
        user.attributes.bump(quest.attribute, amount=modified_attribute_gain)
        events["attributeGains"] = {quest.attribute: modified_attribute_gain}

    _update_streak(user)
    _log_daily_xp(user, modified_xp, quest.gold_reward, count_quest=True)

    events["xpGained"] = modified_xp
    events["goldGained"] = quest.gold_reward
    events["streak"] = user.streak

    newly_unlocked = check_achievements(user)
    events["achievementsUnlocked"] = newly_unlocked

    daily_bonus = _apply_daily_goal_bonus(user)
    if daily_bonus:
        events["dailyGoalCompleted"] = True
        events["dailyGoalBonus"] = daily_bonus

    # Apply boss damage if quest is linked to an active boss
    boss_damage_result = _apply_boss_damage_if_linked(user.id, quest.id, quest.xp_reward)
    if boss_damage_result:
        events["bossDamage"] = boss_damage_result

    events["newLevel"] = user.level
    events["levelsGained"] = user.level - old_level

    from app.chronicle_service import log_chronicle_event
    log_chronicle_event(user.id, "quest_completed", {
        "id": quest.id,
        "title": quest.title,
        "category": quest.category,
        "xp": quest.xp_reward,
        "gold": quest.gold_reward,
    })
    if events["attributeGains"]:
        log_chronicle_event(user.id, "attribute_gain", events["attributeGains"])
    if events["levelsGained"] > 0:
        log_chronicle_event(user.id, "level_up", {
            "oldLevel": old_level,
            "newLevel": user.level,
            "levelsGained": events["levelsGained"],
        })
        new_stage = get_evolution_stage(user.level)
        if new_stage != old_stage:
            from app.rpg_utils import calculate_character_class
            attrs = user.attributes.to_dict() if user.attributes else {}
            class_key = calculate_character_class(attrs)
            events["evolution"] = {
                "evolved": True,
                **build_evolution_payload(user.level, class_key, old_stage),
                "oldStage": old_stage,
                "newStage": new_stage,
            }
    for ach in events["achievementsUnlocked"]:
        log_chronicle_event(user.id, "achievement", {
            "id": ach.get("id"),
            "title": ach.get("title"),
            "icon": ach.get("icon"),
        })
    if events.get("bossDamage"):
        bd = events["bossDamage"]
        log_chronicle_event(user.id, "boss_damage", {
            "bossId": bd.get("bossId"),
            "title": bd.get("bossTitle"),
            "damage": bd.get("damage"),
            "oldHp": bd.get("oldHp"),
            "newHp": bd.get("newHp"),
            "hpPercent": bd.get("hpPercent"),
        })
        if bd.get("phaseChanged"):
            log_chronicle_event(user.id, "boss_phase", {
                "bossId": bd.get("bossId"),
                "oldPhase": bd.get("oldPhase"),
                "newPhase": bd.get("newPhase"),
                "oldPhaseName": bd.get("oldPhaseName"),
                "newPhaseName": bd.get("newPhaseName"),
            })
        if bd.get("defeated"):
            log_chronicle_event(user.id, "boss_defeated", {
                "id": bd.get("bossId"),
                "title": bd.get("bossTitle"),
            })
    try:
        world_after = get_world_data(user.id)
        region_id = get_region_for_category(quest.category)
        before = world_before.get("regions", {}).get(region_id, {})
        after = world_after.get("regions", {}).get(region_id, {})
        if before.get("stage") and after.get("stage") and before.get("stage") != after.get("stage"):
            log_chronicle_event(user.id, "region_milestone", {
                "regionId": region_id,
                "regionName": after.get("name"),
                "oldStage": before.get("stage"),
                "newStage": after.get("stage"),
                "oldProgress": before.get("progress"),
                "newProgress": after.get("progress"),
            })
        elif before.get("progress") is not None and after.get("progress") is not None and after.get("progress") != before.get("progress"):
            log_chronicle_event(user.id, "region_progress", {
                "regionId": region_id,
                "regionName": after.get("name"),
                "oldProgress": before.get("progress"),
                "newProgress": after.get("progress"),
            })
    except Exception:
        pass

    return events


def apply_skill_modifiers(user: User, base_xp: int, quest_attribute: str) -> int:
    """Apply skill XP modifiers to quest rewards."""
    if not user.attributes:
        return base_xp
    
    # Get user's unlocked skills
    unlocked_skills = [
        us.skill
        for us in UserSkill.query.filter_by(user_id=user.id).all()
    ]
    
    total_bonus = 0
    for skill in unlocked_skills:
        if skill.effect_type == "xp_boost" and skill.attribute == quest_attribute:
            # skill.effect_value is percentage (e.g., 5 for 5%)
            bonus = int(base_xp * (skill.effect_value / 100))
            total_bonus += bonus
    
    return base_xp + total_bonus


def apply_skill_attribute_modifiers(user: User, quest_attribute: str, base_gain: int) -> int:
    """Apply skill attribute modifiers to attribute rewards."""
    if not user.attributes:
        return base_gain
    
    # Get user's unlocked skills
    unlocked_skills = [
        us.skill
        for us in UserSkill.query.filter_by(user_id=user.id).all()
    ]
    
    total_bonus = 0
    for skill in unlocked_skills:
        if skill.effect_type == "attribute_boost" and skill.attribute == quest_attribute:
            # skill.effect_value is percentage (e.g., 5 for 5%)
            bonus = int(base_gain * (skill.effect_value / 100))
            total_bonus += bonus
    
    return base_gain + total_bonus


def calculate_attribute_gain(xp_reward: int) -> int:
    """Calculate attribute points based on XP reward (balanced progression)."""
    # 1 point per 20 XP, minimum 1 point
    # This means: Easy (60 XP) = 3 points, Medium (130 XP) = 6 points, Hard (220 XP) = 11 points
    return max(1, xp_reward // 20)


def apply_xp(user: User, amount: int) -> int:
    """Add XP and process level-ups. Returns number of levels gained."""
    if amount <= 0:
        return 0
    start_level = user.level
    user.xp += amount
    while user.xp >= user.xp_to_next:
        user.xp -= user.xp_to_next
        user.level += 1
        user.skill_points += 1
        user.gold += LEVEL_UP_GOLD_BONUS
        user.xp_to_next = int(user.xp_to_next * 1.15)
    return user.level - start_level


def _update_streak(user: User):
    today = _utc_today()
    if user.last_active_date == today:
        return

    if user.last_active_date == today - timedelta(days=1):
        user.streak += 1
    else:
        user.streak = 1

    user.last_active_date = today
    user.best_streak = max(user.best_streak or 0, user.streak)


def _log_daily_xp(user: User, xp_earned: int, gold_earned: int, count_quest: bool = False):
    today = _utc_today()
    row = XPLog.query.filter_by(user_id=user.id, log_date=today).first()
    if not row:
        row = XPLog(user_id=user.id, log_date=today, xp_earned=0, quests_done=0, gold_earned=0)
        db.session.add(row)
    row.xp_earned += xp_earned
    if count_quest:
        row.quests_done += 1
    row.gold_earned += gold_earned


def count_completed_today(user_id: int) -> int:
    today = _utc_today()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    return Quest.query.filter(
        Quest.user_id == user_id,
        Quest.status == "COMPLETED",
        Quest.completed_at >= start,
        Quest.completed_at <= end,
    ).count()


def _apply_daily_goal_bonus(user: User):
    """Award bonus once per day when daily goal is reached."""
    today = _utc_today()
    if user.daily_goal_bonus_date == today:
        return None

    completed_today = count_completed_today(user.id)
    if completed_today < user.daily_goal:
        return None

    user.daily_goal_bonus_date = today
    user.gold += DAILY_GOAL_BONUS_GOLD
    apply_xp(user, DAILY_GOAL_BONUS_XP)
    _log_daily_xp(user, DAILY_GOAL_BONUS_XP, DAILY_GOAL_BONUS_GOLD, count_quest=False)
    return {"xp": DAILY_GOAL_BONUS_XP, "gold": DAILY_GOAL_BONUS_GOLD}


def check_achievements(user: User) -> list:
    """Unlock achievements the user newly qualifies for. Returns unlocked list."""
    unlocked_ids = {
        ua.achievement_id
        for ua in UserAchievement.query.filter_by(user_id=user.id).all()
    }
    completed_count = Quest.query.filter_by(user_id=user.id, status="COMPLETED").count()
    wellness_completed = Quest.query.filter_by(
        user_id=user.id, status="COMPLETED", category="Wellness"
    ).count()
    quests_created = Quest.query.filter_by(user_id=user.id).count()

    conditions = {
        "FIRST_QUEST": completed_count >= 1,
        "SEVEN_DAY_STREAK": user.streak >= 7,
        "THIRTY_DAY_STREAK": user.streak >= 30,
        "SCHOLAR": user.attributes and user.attributes.intelligence >= 50,
        "IRONCLAD": user.attributes and user.attributes.strength >= 80,
        "CENTURY_WARRIOR": completed_count >= 100,
        "HIGH_KING": user.level >= 25,
        "HOARDER": user.gold >= 5000,
        "WELLNESS_MASTER": wellness_completed >= 10,
        "QUEST_MASTER": quests_created >= 50,
    }

    newly_unlocked = []
    for code, met in conditions.items():
        if not met:
            continue
        achievement = Achievement.query.filter_by(code=code).first()
        if achievement and achievement.id not in unlocked_ids:
            db.session.add(UserAchievement(user_id=user.id, achievement_id=achievement.id))
            unlocked_ids.add(achievement.id)
            apply_xp(user, achievement.xp_reward)
            newly_unlocked.append(achievement.to_dict(unlocked=True))
    return newly_unlocked


def equip_item(user: User, item_id: int) -> ShopItem:
    """Equip an owned shop item. Unequips others in the same category."""
    inventory_row = UserInventory.query.filter_by(user_id=user.id, item_id=item_id).first()
    if not inventory_row:
        raise ValueError("item not owned")

    item = ShopItem.query.get_or_404(item_id)
    if item.category not in EQUIPPABLE_CATEGORIES:
        raise ValueError(f"{item.category} items cannot be equipped yet")

    _unequip_category(user.id, item.category)
    inventory_row.equipped = True

    if item.category == "Avatars":
        user.avatar = item.icon

    return item


def unequip_item(user: User, item_id: int) -> ShopItem:
    inventory_row = UserInventory.query.filter_by(
        user_id=user.id, item_id=item_id, equipped=True
    ).first()
    if not inventory_row:
        raise ValueError("item is not equipped")

    item = inventory_row.item
    inventory_row.equipped = False

    if item.category == "Avatars":
        user.avatar = "🧙"

    return item


def _unequip_category(user_id: int, category: str):
    rows = (
        UserInventory.query.join(ShopItem)
        .filter(UserInventory.user_id == user_id, ShopItem.category == category)
        .all()
    )
    for row in rows:
        row.equipped = False


def _apply_boss_damage_if_linked(user_id: int, quest_id: int, quest_xp: int):
    """Apply boss damage if the quest is linked to an active boss."""
    from app.world_services import apply_boss_damage
    from app.models import BossQuest, Boss
    
    # Find if this quest is linked to any active boss
    boss_quest = BossQuest.query.join(Boss).filter(
        BossQuest.quest_id == quest_id,
        Boss.user_id == user_id,
        Boss.status == "active"
    ).first()
    
    if not boss_quest:
        return None
    
    boss = boss_quest.boss
    
    # Don't damage defeated bosses
    if boss.status == "defeated":
        return None
    
    # Apply damage
    damage_result = apply_boss_damage(boss, quest_xp)
    
    return {
        "bossId": boss.id,
        "bossTitle": boss.title,
        **damage_result,
    }
