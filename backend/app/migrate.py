import os
from sqlalchemy import inspect, text

from app.extensions import db
from app.models import Achievement, ShopItem, Skill


USER_COLUMNS = {
    "best_streak": "INTEGER DEFAULT 0",
    "skill_points": "INTEGER DEFAULT 0",
    "daily_goal_bonus_date": "DATE NULL",
    "seen_evolution_stage": "VARCHAR(30) DEFAULT 'novice'",
    "onboarding_completed": "BOOLEAN DEFAULT FALSE",
    "life_goals": "VARCHAR(200) NULL",
}

BOSS_COLUMNS = {
    "reward_claimed": "BOOLEAN DEFAULT FALSE",
}

INDEXES = [
    ("idx_quests_user_id", "quests", "user_id"),
    ("idx_quests_user_status", "quests", "user_id, status"),
    ("idx_xp_log_user_date", "xp_log", "user_id, log_date"),
    ("idx_inventory_user", "user_inventory", "user_id"),
    ("idx_chronicle_user_date", "chronicle_events", "user_id, event_date"),
]

DEFAULT_ACHIEVEMENTS = [
    ("FIRST_QUEST", "First Quest", "Complete your very first quest", 50, "🏆"),
    ("SEVEN_DAY_STREAK", "7-Day Streak", "Maintain a streak for 7 days straight", 100, "🔥"),
    ("SCHOLAR", "Scholar", "Reach Intelligence level 50", 200, "🧠"),
    ("CENTURY_WARRIOR", "Century Warrior", "Complete 100 quests total", 600, "⚔️"),
    ("HIGH_KING", "High King", "Reach level 25", 1000, "👑"),
    ("HOARDER", "Hoarder", "Accumulate 5,000 gold", 300, "💰"),
    ("IRONCLAD", "Ironclad", "Reach Strength level 80", 400, "🛡️"),
    ("WELLNESS_MASTER", "Wellness Master", "Complete 10 Wellness quests", 150, "🧘"),
    ("THIRTY_DAY_STREAK", "30-Day Streak", "Maintain a 30-day streak", 600, "⚡"),
    ("QUEST_MASTER", "Quest Master", "Create 50 custom quests", 300, "🛠️"),
]

DEFAULT_SHOP_ITEMS = [
    ("Dragon Avatar", "Avatars", "Unleash your inner beast with this legendary avatar", 1500, "🐉"),
    ("Legendary Frame", "Frames", "Golden ornate frame for your character profile", 800, "🗡️"),
    ("Cyber Theme", "Themes", "Transform your UI with neon cyberpunk aesthetics", 2000, "🌈"),
    ("Royal Badge", "Badges", "Display prestige with this regal insignia", 1200, "👑"),
    ("Mystic Cat", "Companions", "A mystical feline companion for your journey", 600, "🐱"),
    ("Phoenix Wings", "Companions", "Rise from the ashes with blazing phoenix wings", 3000, "🦅"),
    ("Shadow Blade", "Weapons", "Wield the blade of shadows as your weapon icon", 900, "🗡️"),
    ("Crystal Orb", "Magic", "Gaze into your destiny with a mystical crystal orb", 700, "🔮"),
]

DEFAULT_SKILLS = [
    ("Power I", "Increase Strength attribute rewards by 5%", "Strength", 1, None, "attribute_boost", 5, "💪"),
    ("Power II", "Increase Strength attribute rewards by 10%", "Strength", 2, 1, "attribute_boost", 10, "💪"),
    ("Mighty", "Increase Strength attribute rewards by 15%", "Strength", 3, 2, "attribute_boost", 15, "⚔️"),
    ("Fast Learner", "Increase XP from Intelligence quests by 5%", "Intelligence", 1, None, "xp_boost", 5, "🧠"),
    ("Deep Study", "Increase XP from Intelligence quests by 10%", "Intelligence", 2, 4, "xp_boost", 10, "📚"),
    ("Knowledge Master", "Increase XP from Intelligence quests by 15%", "Intelligence", 3, 5, "xp_boost", 15, "🎓"),
    ("Focus I", "Increase Discipline attribute rewards by 5%", "Discipline", 1, None, "attribute_boost", 5, "🔥"),
    ("Focus II", "Increase Discipline attribute rewards by 10%", "Discipline", 2, 7, "attribute_boost", 10, "🔥"),
    ("Flow State", "Increase Discipline attribute rewards by 15%", "Discipline", 3, 8, "attribute_boost", 15, "🌊"),
    ("Endurance I", "Increase Vitality attribute rewards by 5%", "Vitality", 1, None, "attribute_boost", 5, "❤️"),
    ("Recovery", "Increase Vitality attribute rewards by 10%", "Vitality", 2, 10, "attribute_boost", 10, "💊"),
    ("Vitality", "Increase Vitality attribute rewards by 15%", "Vitality", 3, 11, "attribute_boost", 15, "✨"),
    ("Creative Flow", "Increase Creativity attribute rewards by 5%", "Creativity", 1, None, "attribute_boost", 5, "🎨"),
    ("Idea Generator", "Increase Creativity attribute rewards by 10%", "Creativity", 2, 13, "attribute_boost", 10, "💡"),
    ("Creative Mastery", "Increase Creativity attribute rewards by 15%", "Creativity", 3, 14, "attribute_boost", 15, "🎭"),
]

PREREQUISITE_MAP = {
    2: 1,
    3: 2,
    5: 4,
    6: 5,
    8: 7,
    9: 8,
    11: 10,
    12: 11,
    14: 13,
    15: 14,
}


def _table_exists(inspector, table_name):
    return table_name in inspector.get_table_names()


def _column_names(inspector, table_name):
    return {col["name"] for col in inspector.get_columns(table_name)}


def run_migrations(app):
    """Apply additive migrations safely on startup."""
    with app.app_context():
        inspector = inspect(db.engine)
        if not _table_exists(inspector, "users"):
            db.create_all()
            inspector = inspect(db.engine)

        dialect = db.engine.dialect.name

        for column, ddl in USER_COLUMNS.items():
            if column not in _column_names(inspector, "users"):
                col_ddl = ddl
                if dialect in ("sqlite", "mysql") and "DEFAULT FALSE" in ddl:
                    col_ddl = ddl.replace("DEFAULT FALSE", "DEFAULT 0")
                db.session.execute(text(f"ALTER TABLE users ADD COLUMN {column} {col_ddl}"))

        if _table_exists(inspector, "bosses"):
            for column, ddl in BOSS_COLUMNS.items():
                if column not in _column_names(inspector, "bosses"):
                    col_ddl = ddl
                    if dialect in ("sqlite", "mysql") and "DEFAULT FALSE" in ddl:
                        col_ddl = ddl.replace("DEFAULT FALSE", "DEFAULT 0")
                    db.session.execute(text(f"ALTER TABLE bosses ADD COLUMN {column} {col_ddl}"))

        db.session.commit()

        if not _table_exists(inspector, "chronicle_events"):
            db.create_all()
            inspector = inspect(db.engine)

        _ensure_indexes(inspector)
        if not app.config.get("TESTING") and not os.environ.get("PYTEST_CURRENT_TEST"):
            _ensure_seed_data()


def _ensure_indexes(inspector):
    dialect = db.engine.dialect.name
    existing_indexes = set()
    for table in inspector.get_table_names():
        for idx in inspector.get_indexes(table):
            if idx.get("name"):
                existing_indexes.add(idx.get("name"))

    for name, table, columns in INDEXES:
        if name in existing_indexes or not _table_exists(inspector, table):
            continue
        cols = ", ".join(columns.split(", "))
        if dialect in ("sqlite", "postgresql"):
            db.session.execute(text(f"CREATE INDEX IF NOT EXISTS {name} ON {table} ({cols})"))
        else:
            db.session.execute(text(f"CREATE INDEX {name} ON {table} ({cols})"))
    db.session.commit()


def _ensure_seed_data():
    """Ensure essential game catalog items (achievements, shop items, skills) exist."""
    changed = False
    if not Achievement.query.first():
        for code, title, desc, xp, icon in DEFAULT_ACHIEVEMENTS:
            db.session.add(Achievement(code=code, title=title, description=desc, xp_reward=xp, icon=icon))
        changed = True

    if not ShopItem.query.first():
        for name, cat, desc, price, icon in DEFAULT_SHOP_ITEMS:
            db.session.add(ShopItem(name=name, category=cat, description=desc, price=price, icon=icon))
        changed = True

    if not Skill.query.first():
        for name, desc, attr, cost, prereq, effect_type, effect_value, icon in DEFAULT_SKILLS:
            db.session.add(Skill(
                name=name, description=desc, attribute=attr, cost=cost,
                prerequisite_id=None, effect_type=effect_type, effect_value=effect_value, icon=icon
            ))
        db.session.commit()
        for skill_id, prereq_id in PREREQUISITE_MAP.items():
            skill = db.session.get(Skill, skill_id) if hasattr(db.session, "get") else Skill.query.get(skill_id)
            if skill:
                skill.prerequisite_id = prereq_id
        changed = True

    if changed:
        db.session.commit()
