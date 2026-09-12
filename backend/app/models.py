from datetime import datetime, date, timezone
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(80), default="Adventurer")
    avatar = db.Column(db.String(10), default="🧙")
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    xp_to_next = db.Column(db.Integer, default=500)
    gold = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    best_streak = db.Column(db.Integer, default=0)
    skill_points = db.Column(db.Integer, default=0)
    last_active_date = db.Column(db.Date, nullable=True)
    daily_goal = db.Column(db.Integer, default=5)
    daily_goal_bonus_date = db.Column(db.Date, nullable=True)
    quest_reminders = db.Column(db.Boolean, default=True)
    streak_alerts = db.Column(db.Boolean, default=True)
    levelup_celebrations = db.Column(db.Boolean, default=True)
    achievement_unlocks = db.Column(db.Boolean, default=True)
    onboarding_completed = db.Column(db.Boolean, default=False)
    life_goals = db.Column(db.String(200), nullable=True)  # Comma-separated goals
    seen_evolution_stage = db.Column(db.String(30), default="novice")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    attributes = db.relationship("Attributes", backref="user", uselist=False,
                                  cascade="all, delete-orphan")
    quests = db.relationship("Quest", backref="user", cascade="all, delete-orphan")
    inventory = db.relationship("UserInventory", backref="user", cascade="all, delete-orphan")
    bosses = db.relationship("Boss", backref="user", cascade="all, delete-orphan")

    def to_dict(self, quests_done=None):
        return {
            "id": self.id,
            "username": self.username,
            "displayName": self.display_name,
            "title": self.title,
            "avatar": self.avatar,
            "level": self.level,
            "xp": self.xp,
            "xpToNext": self.xp_to_next,
            "gold": self.gold,
            "streak": self.streak,
            "bestStreak": self.best_streak,
            "skillPoints": self.skill_points,
            "dailyGoal": self.daily_goal,
            "questsDone": quests_done if quests_done is not None else 0,
            "onboardingCompleted": self.onboarding_completed,
            "lifeGoals": self.life_goals,
            "settings": {
                "questReminders": self.quest_reminders,
                "streakAlerts": self.streak_alerts,
                "levelUpCelebrations": self.levelup_celebrations,
                "achievementUnlocks": self.achievement_unlocks,
            },
        }


class Attributes(db.Model):
    __tablename__ = "attributes"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    strength = db.Column(db.Integer, default=0)
    intelligence = db.Column(db.Integer, default=0)
    discipline = db.Column(db.Integer, default=0)
    creativity = db.Column(db.Integer, default=0)
    vitality = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "strength": self.strength,
            "intelligence": self.intelligence,
            "discipline": self.discipline,
            "creativity": self.creativity,
            "vitality": self.vitality,
        }

    def bump(self, attribute_name, amount=1):
        key = attribute_name.lower()
        if hasattr(self, key):
            current_value = getattr(self, key)
            new_value = max(0, min(100, current_value + amount))
            setattr(self, key, new_value)


class Quest(db.Model):
    __tablename__ = "quests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    difficulty = db.Column(db.Enum("EASY", "MEDIUM", "HARD", name="difficulty_enum"),
                            default="EASY")
    attribute = db.Column(db.String(30), nullable=False)
    xp_reward = db.Column(db.Integer, default=50)
    gold_reward = db.Column(db.Integer, default=10)
    due_label = db.Column(db.String(30), default="Today")
    status = db.Column(db.Enum("ACTIVE", "COMPLETED", name="status_enum"), default="ACTIVE")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "difficulty": self.difficulty,
            "attribute": self.attribute,
            "xpReward": self.xp_reward,
            "goldReward": self.gold_reward,
            "dueLabel": self.due_label,
            "status": self.status,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
        }


class Achievement(db.Model):
    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    xp_reward = db.Column(db.Integer, default=100)
    icon = db.Column(db.String(10), default="🏆")

    def to_dict(self, unlocked=False):
        return {
            "id": self.id,
            "code": self.code,
            "title": self.title,
            "description": self.description,
            "xpReward": self.xp_reward,
            "icon": self.icon,
            "unlocked": unlocked,
        }


class UserAchievement(db.Model):
    __tablename__ = "user_achievements"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey("achievements.id"), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# Categories that can be equipped (Themes reserved for a future update)
EQUIPPABLE_CATEGORIES = {"Avatars", "Frames", "Badges", "Companions", "Effects", "Weapons", "Magic"}


class ShopItem(db.Model):
    __tablename__ = "shop_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Integer, nullable=False)
    icon = db.Column(db.String(10), default="✨")

    def to_dict(self, owned=False, equipped=False):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "price": self.price,
            "icon": self.icon,
            "owned": owned,
            "equipped": equipped,
            "equippable": self.category in EQUIPPABLE_CATEGORIES,
        }


class UserInventory(db.Model):
    __tablename__ = "user_inventory"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("shop_items.id"), nullable=False)
    equipped = db.Column(db.Boolean, default=False)
    owned_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    item = db.relationship("ShopItem")


class XPLog(db.Model):
    __tablename__ = "xp_log"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    log_date = db.Column(db.Date, default=date.today)
    xp_earned = db.Column(db.Integer, default=0)
    quests_done = db.Column(db.Integer, default=0)
    gold_earned = db.Column(db.Integer, default=0)


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    attribute = db.Column(db.String(30), nullable=False)
    cost = db.Column(db.Integer, default=1, nullable=False)
    prerequisite_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=True)
    effect_type = db.Column(db.String(30), nullable=False)  # "xp_boost", "attribute_boost"
    effect_value = db.Column(db.Integer, default=0, nullable=False)
    icon = db.Column(db.String(10), default="✨")

    def to_dict(self, unlocked=False):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "attribute": self.attribute,
            "cost": self.cost,
            "prerequisiteId": self.prerequisite_id,
            "effectType": self.effect_type,
            "effectValue": self.effect_value,
            "icon": self.icon,
            "unlocked": unlocked,
        }


class UserSkill(db.Model):
    __tablename__ = "user_skills"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    skill = db.relationship("Skill")


class Boss(db.Model):
    __tablename__ = "bosses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(30), nullable=False)  # Maps to region
    max_hp = db.Column(db.Integer, nullable=False)
    current_hp = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Enum("EASY", "MEDIUM", "HARD", "EPIC", name="boss_difficulty_enum"), nullable=False)
    status = db.Column(db.Enum("active", "defeated", "abandoned", name="boss_status_enum"), default="active")
    reward_claimed = db.Column(db.Boolean, default=False, nullable=False)
    deadline = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        from app.rpg_utils import calculate_boss_phase, get_phase_name, get_region_for_category
        phase = calculate_boss_phase(self.current_hp, self.max_hp)
        region_id = get_region_for_category(self.category)
        
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "regionId": region_id,
            "maxHp": self.max_hp,
            "currentHp": self.current_hp,
            "hpPercent": int((self.current_hp / self.max_hp) * 100) if self.max_hp > 0 else 0,
            "difficulty": self.difficulty,
            "status": self.status,
            "rewardClaimed": self.reward_claimed,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "currentPhase": phase,
            "phaseName": get_phase_name(phase),
            "createdAt": self.created_at.isoformat(),
        }


class BossQuest(db.Model):
    __tablename__ = "boss_quests"

    id = db.Column(db.Integer, primary_key=True)
    boss_id = db.Column(db.Integer, db.ForeignKey("bosses.id"), nullable=False)
    quest_id = db.Column(db.Integer, db.ForeignKey("quests.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    boss = db.relationship("Boss")
    quest = db.relationship("Quest")


class ChronicleEvent(db.Model):
    """Append-only activity log for Daily Chronicle. Does not replace XP/gold source of truth."""
    __tablename__ = "chronicle_events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    event_date = db.Column(db.Date, default=date.today, index=True)
    event_type = db.Column(db.String(40), nullable=False)
    payload = db.Column(db.Text, default="{}")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
