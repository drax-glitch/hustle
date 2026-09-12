"""Lightweight schema upgrades for existing databases (no Alembic)."""

from sqlalchemy import inspect, text

from app.extensions import db


USER_COLUMNS = {
    "best_streak": "INTEGER DEFAULT 0",
    "skill_points": "INTEGER DEFAULT 0",
    "daily_goal_bonus_date": "DATE NULL",
    "seen_evolution_stage": "VARCHAR(30) DEFAULT 'novice'",
    "onboarding_completed": "BOOLEAN DEFAULT 0",
    "life_goals": "VARCHAR(200) NULL",
}

BOSS_COLUMNS = {
    "reward_claimed": "BOOLEAN DEFAULT 0",
}

INDEXES = [
    ("idx_quests_user_id", "quests", "user_id"),
    ("idx_quests_user_status", "quests", "user_id, status"),
    ("idx_xp_log_user_date", "xp_log", "user_id, log_date"),
    ("idx_inventory_user", "user_inventory", "user_id"),
    ("idx_chronicle_user_date", "chronicle_events", "user_id, event_date"),
]


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

        for column, ddl in USER_COLUMNS.items():
            if column not in _column_names(inspector, "users"):
                db.session.execute(text(f"ALTER TABLE users ADD COLUMN {column} {ddl}"))

        if _table_exists(inspector, "bosses"):
            for column, ddl in BOSS_COLUMNS.items():
                if column not in _column_names(inspector, "bosses"):
                    db.session.execute(text(f"ALTER TABLE bosses ADD COLUMN {column} {ddl}"))

        db.session.commit()

        if not _table_exists(inspector, "chronicle_events"):
            db.create_all()
            inspector = inspect(db.engine)

        _ensure_indexes(inspector)


def _ensure_indexes(inspector):
    dialect = db.engine.dialect.name
    existing_indexes = set()
    for table in inspector.get_table_names():
        for idx in inspector.get_indexes(table):
            existing_indexes.add(idx.get("name"))

    for name, table, columns in INDEXES:
        if name in existing_indexes or not _table_exists(inspector, table):
            continue
        cols = ", ".join(columns.split(", "))
        if dialect == "sqlite":
            db.session.execute(text(f"CREATE INDEX IF NOT EXISTS {name} ON {table} ({cols})"))
        else:
            db.session.execute(text(f"CREATE INDEX {name} ON {table} ({cols})"))
    db.session.commit()
