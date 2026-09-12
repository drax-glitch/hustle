"""Shared RPG utility functions for character progression."""
from typing import Optional


# Attribute tier thresholds
ATTRIBUTE_TIERS = {
    "Novice": (0, 19),
    "Apprentice": (20, 39),
    "Skilled": (40, 59),
    "Expert": (60, 79),
    "Master": (80, 99),
    "Legendary": (100, 100),
}

# Centralized category to attribute mapping
CATEGORY_TO_ATTRIBUTE = {
    "Work": "Discipline",
    "Learning": "Intelligence",
    "Health": "Strength",
    "Creative": "Creativity",
    "Wellness": "Vitality",
}

# Region definitions mapping categories to world regions
REGIONS = {
    "health": {
        "id": "health",
        "name": "Health",
        "description": "Physical wellbeing and vitality",
        "category": "Health",
        "attribute": "Strength",
        "icon": "❤️",
        "color": "from-rose-500 to-rose-400",
    },
    "knowledge": {
        "id": "knowledge",
        "name": "Knowledge",
        "description": "Intellectual growth and learning",
        "category": "Learning",
        "attribute": "Intelligence",
        "icon": "📚",
        "color": "from-cyan-500 to-cyan-400",
    },
    "career": {
        "id": "career",
        "name": "Career",
        "description": "Professional development and work",
        "category": "Work",
        "attribute": "Discipline",
        "icon": "⚔️",
        "color": "from-amber-500 to-amber-400",
    },
    "creativity": {
        "id": "creativity",
        "name": "Creativity",
        "description": "Artistic expression and innovation",
        "category": "Creative",
        "attribute": "Creativity",
        "icon": "🎨",
        "color": "from-fuchsia-500 to-fuchsia-400",
    },
    "discipline": {
        "id": "discipline",
        "name": "Discipline",
        "description": "Habits, consistency, and mental fortitude",
        "category": "Wellness",
        "attribute": "Vitality",
        "icon": "🧘",
        "color": "from-emerald-500 to-emerald-400",
    },
}

# Region progression stages
REGION_STAGES = {
    "unknown": (0, 19, "🌑 Unknown"),
    "discovered": (20, 39, "🌱 Discovered"),
    "explored": (40, 59, "🗺️ Explored"),
    "developed": (60, 79, "🏗️ Developed"),
    "mastered": (80, 99, "👑 Mastered"),
    "legendary": (100, 100, "✨ Legendary"),
}

# Boss difficulty configurations
BOSS_DIFFICULTY = {
    "EASY": {"max_hp": 1000, "damage_multiplier": 1.5},
    "MEDIUM": {"max_hp": 2500, "damage_multiplier": 1.75},
    "HARD": {"max_hp": 5000, "damage_multiplier": 2.0},
    "EPIC": {"max_hp": 10000, "damage_multiplier": 2.5},
}

# Character class definitions
CHARACTER_CLASSES = {
    "WARRIOR": {
        "name": "Warrior",
        "icon": "⚔️",
        "description": "Your physical strength and vitality make you a formidable warrior.",
        "color": "from-rose-500 to-rose-400",
    },
    "SCHOLAR": {
        "name": "Scholar",
        "icon": "🧠",
        "description": "Your dedication to learning has shaped you into a master of knowledge.",
        "color": "from-cyan-500 to-cyan-400",
    },
    "CREATOR": {
        "name": "Creator",
        "icon": "🎨",
        "description": "Your creative spirit allows you to bring ideas to life.",
        "color": "from-fuchsia-500 to-fuchsia-400",
    },
    "GUARDIAN": {
        "name": "Guardian",
        "icon": "🛡️",
        "description": "Your discipline and vitality make you a steadfast protector.",
        "color": "from-emerald-500 to-emerald-400",
    },
    "EXPLORER": {
        "name": "Explorer",
        "icon": "🧭",
        "description": "Your balanced development makes you adaptable to any challenge.",
        "color": "from-amber-500 to-amber-400",
    },
    "MASTER_ADVENTURER": {
        "name": "Master Adventurer",
        "icon": "🌟",
        "description": "Your exceptional mastery across all attributes makes you a legendary hero.",
        "color": "from-purple-500 to-purple-400",
    },
}


def get_attribute_for_category(category: str) -> str:
    """Get the attribute associated with a quest category."""
    return CATEGORY_TO_ATTRIBUTE.get(category, "Discipline")


def get_attribute_tier(value: int) -> str:
    """Get the tier name for an attribute value."""
    for tier, (min_val, max_val) in ATTRIBUTE_TIERS.items():
        if min_val <= value <= max_val:
            return tier
    return "Novice"


def calculate_character_class(attributes: dict) -> str:
    """
    Calculate character class based on attribute distribution.
    Deterministic: same stats always produce same class.
    """
    strength = attributes.get("strength", 0)
    intelligence = attributes.get("intelligence", 0)
    discipline = attributes.get("discipline", 0)
    creativity = attributes.get("creativity", 0)
    vitality = attributes.get("vitality", 0)

    # Check for Master Adventurer (high balanced stats)
    total = strength + intelligence + discipline + creativity + vitality
    if total >= 300:  # Average 60+ across all attributes
        return "MASTER_ADVENTURER"

    # Check for specialized classes
    physical_score = strength + vitality
    mental_score = intelligence + discipline
    creative_score = creativity + discipline

    max_score = max(physical_score, mental_score, creative_score)

    if max_score == physical_score and physical_score >= 120:
        return "WARRIOR"
    elif max_score == mental_score and mental_score >= 120:
        return "SCHOLAR"
    elif max_score == creative_score and creative_score >= 120:
        return "CREATOR"
    elif discipline >= 70 and vitality >= 60:
        return "GUARDIAN"
    else:
        return "EXPLORER"


def get_region_for_category(category: str) -> str:
    """Get the region ID associated with a quest category."""
    category_region_map = {
        "Health": "health",
        "Learning": "knowledge",
        "Work": "career",
        "Creative": "creativity",
        "Wellness": "discipline",
    }
    return category_region_map.get(category, "career")


def calculate_region_progress(category, completed_count, total_count) -> int:
    """
    Calculate region progress percentage based on quest completion.
    Cap at 100% to prevent overflow.
    """
    if total_count == 0:
        return 0
    progress = int((completed_count / total_count) * 100)
    return min(100, progress)


def get_region_stage(progress: int) -> str:
    """Get the stage name for a region progress percentage."""
    for stage, (min_val, max_val, _) in REGION_STAGES.items():
        if min_val <= progress <= max_val:
            return stage
    return "unknown"


def get_region_stage_display(stage: str) -> str:
    """Get the display name for a region stage."""
    for key, (_, _, display) in REGION_STAGES.items():
        if key == stage:
            return display
    return "🌑 Unknown"


def calculate_world_progress(region_progresses: dict) -> int:
    """Calculate overall world progress as average of all region progresses."""
    if not region_progresses:
        return 0
    total = sum(region_progresses.values())
    return int(total / len(region_progresses))


def calculate_boss_damage(xp_reward: int, difficulty: str) -> int:
    """
    Calculate boss damage based on quest XP and boss difficulty.
    Uses the configured damage multiplier from BOSS_DIFFICULTY.
    """
    multiplier = BOSS_DIFFICULTY.get(difficulty, {}).get("damage_multiplier", 1.5)
    return int(xp_reward * multiplier)


def calculate_boss_phase(current_hp: int, max_hp: int, num_phases: int = 5) -> int:
    """
    Calculate current boss phase (1-indexed) based on HP.
    Phases are determined by percentage of HP remaining.
    """
    if current_hp <= 0:
        return num_phases
    hp_percent = (current_hp / max_hp) * 100
    phase_size = 100 / num_phases
    phase = int((100 - hp_percent) / phase_size) + 1
    return min(phase, num_phases)


PHASE_NAMES = [
    "🔍 Research",
    "🎨 Design",
    "💻 Build",
    "🧪 Test",
    "🚀 Deploy",
]


def get_phase_name(phase: int) -> str:
    """Get the display name for a boss phase."""
    if 1 <= phase <= len(PHASE_NAMES):
        return PHASE_NAMES[phase - 1]
    return f"Phase {phase}"


# Character evolution stages
EVOLUTION_STAGES = {
    "novice": (1, 4, "🌱 Novice"),
    "adventurer": (5, 9, "⚔️ Adventurer"),
    "hero": (10, 19, "🛡️ Hero"),
    "elite": (20, 29, "🔥 Elite"),
    "legend": (30, 999, "👑 Legend"),
}


# Class-specific evolution titles
CLASS_EVOLUTION_TITLES = {
    "WARRIOR": {
        "novice": "Rookie Fighter",
        "adventurer": "Battle Warrior",
        "hero": "Warlord",
        "elite": "Champion",
        "legend": "Legendary Champion",
    },
    "SCHOLAR": {
        "novice": "Student",
        "adventurer": "Researcher",
        "hero": "Sage",
        "elite": "Grand Scholar",
        "legend": "Archmage",
    },
    "CREATOR": {
        "novice": "Apprentice",
        "adventurer": "Maker",
        "hero": "Master Creator",
        "elite": "Grand Artisan",
        "legend": "Legendary Artisan",
    },
    "GUARDIAN": {
        "novice": "Recruit",
        "adventurer": "Protector",
        "hero": "Sentinel",
        "elite": "Warden",
        "legend": "Guardian Legend",
    },
    "EXPLORER": {
        "novice": "Traveler",
        "adventurer": "Pathfinder",
        "hero": "Adventurer",
        "elite": "World Explorer",
        "legend": "Living Legend",
    },
    "MASTER_ADVENTURER": {
        "novice": "Adventurer",
        "adventurer": "Hero",
        "hero": "Master",
        "elite": "Grand Master",
        "legend": "Living Legend",
    },
}


def get_evolution_stage(level: int) -> str:
    """Get the evolution stage for a given level."""
    for stage, (min_level, max_level, _) in EVOLUTION_STAGES.items():
        if min_level <= level <= max_level:
            return stage
    return "novice"


def get_evolution_stage_display(stage: str) -> str:
    """Get the display name for an evolution stage."""
    for s, (_, _, display) in EVOLUTION_STAGES.items():
        if s == stage:
            return display
    return "🌱 Novice"


def get_evolution_title(character_class: str, evolution_stage: str) -> str:
    """Get the class-specific evolution title."""
    class_key = character_class.upper() if character_class else "EXPLORER"
    titles = CLASS_EVOLUTION_TITLES.get(class_key, CLASS_EVOLUTION_TITLES["EXPLORER"])
    return titles.get(evolution_stage, "Adventurer")


def get_next_evolution_stage(current_stage: str) -> Optional[str]:
    """Get the next evolution stage after the current one."""
    stage_order = ["novice", "adventurer", "hero", "elite", "legend"]
    try:
        current_index = stage_order.index(current_stage)
        if current_index < len(stage_order) - 1:
            return stage_order[current_index + 1]
    except ValueError:
        pass
    return None


def get_evolution_requirements(target_stage: str) -> int:
    """Get the level requirement for a target evolution stage."""
    for stage, (min_level, _, _) in EVOLUTION_STAGES.items():
        if stage == target_stage:
            return min_level
    return 1


# Visual cosmetics unlocked at each evolution stage (no 3D models required)
EVOLUTION_COSMETICS = {
    "novice": {
        "aura": None,
        "frame": "plain",
        "badge": None,
        "equipment": "basic",
        "unlocked": ["Simple Avatar"],
    },
    "adventurer": {
        "aura": None,
        "frame": "bronze",
        "badge": "Adventurer Seal",
        "equipment": "starter",
        "unlocked": ["Bronze Frame", "Adventurer Seal"],
    },
    "hero": {
        "aura": "heroic",
        "frame": "silver",
        "badge": "Hero Crest",
        "equipment": "advanced",
        "unlocked": ["Heroic Aura", "Silver Frame", "Hero Crest"],
    },
    "elite": {
        "aura": "elite",
        "frame": "gold",
        "badge": "Elite Mark",
        "equipment": "elite",
        "unlocked": ["Elite Aura", "Gold Frame", "Elite Mark"],
    },
    "legend": {
        "aura": "legendary",
        "frame": "legendary",
        "badge": "Legend Crown",
        "equipment": "legendary",
        "unlocked": ["Legendary Aura", "Legendary Frame", "Legend Crown"],
    },
}


def get_evolution_cosmetics(stage: str) -> dict:
    """Return visual cosmetics for an evolution stage."""
    return EVOLUTION_COSMETICS.get(stage, EVOLUTION_COSMETICS["novice"])


def get_evolution_progress(level: int) -> dict:
    """Progress toward the next evolution stage."""
    stage = get_evolution_stage(level)
    next_stage = get_next_evolution_stage(stage)
    min_level, _, _ = EVOLUTION_STAGES.get(stage, (1, 4, "🌱 Novice"))
    if not next_stage:
        return {
            "percent": 100,
            "levelsUntil": 0,
            "currentMin": min_level,
            "nextLevel": None,
        }
    next_req = get_evolution_requirements(next_stage)
    span = max(1, next_req - min_level)
    percent = int(((level - min_level) / span) * 100)
    return {
        "percent": min(100, max(0, percent)),
        "levelsUntil": max(0, next_req - level),
        "currentMin": min_level,
        "nextLevel": next_req,
    }


def crossed_evolution_threshold(old_level: int, new_level: int) -> bool:
    """True only when a level-up actually changes evolution stage."""
    return get_evolution_stage(old_level) != get_evolution_stage(new_level)


def build_evolution_payload(level: int, character_class: str, seen_stage: str = None) -> dict:
    """Central evolution payload used by APIs and level-up events."""
    stage = get_evolution_stage(level)
    next_stage = get_next_evolution_stage(stage)
    progress = get_evolution_progress(level)
    cosmetics = get_evolution_cosmetics(stage)
    seen = seen_stage or "novice"
    return {
        "stage": stage,
        "display": get_evolution_stage_display(stage),
        "title": get_evolution_title(character_class, stage),
        "level": level,
        "nextStage": next_stage,
        "nextDisplay": get_evolution_stage_display(next_stage) if next_stage else None,
        "nextRequirement": get_evolution_requirements(next_stage) if next_stage else None,
        "progressPercent": progress["percent"],
        "levelsUntilNext": progress["levelsUntil"],
        "cosmetics": cosmetics,
        "justEvolved": seen != stage and stage != "novice",
    }
