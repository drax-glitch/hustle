"""Run once after creating the database:  python seed.py
Creates all tables, seeds achievements + shop items, and adds a demo user
(username: aelindra / password: password123) matching the sample UI.
"""
from datetime import date, timedelta
import bcrypt

from app import create_app
from app.extensions import db
from app.models import (
    User, Attributes, Quest, Achievement, ShopItem, UserInventory, XPLog
)

app = create_app()

ACHIEVEMENTS = [
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

SHOP_ITEMS = [
    ("Dragon Avatar", "Avatars", "Unleash your inner beast with this legendary avatar", 1500, "🐉"),
    ("Legendary Frame", "Frames", "Golden ornate frame for your character profile", 800, "🗡️"),
    ("Cyber Theme", "Themes", "Transform your UI with neon cyberpunk aesthetics", 2000, "🌈"),
    ("Royal Badge", "Badges", "Display prestige with this regal insignia", 1200, "👑"),
    ("Mystic Cat", "Companions", "A mystical feline companion for your journey", 600, "🐱"),
    ("Phoenix Wings", "Companions", "Rise from the ashes with blazing phoenix wings", 3000, "🦅"),
    ("Shadow Blade", "Weapons", "Wield the blade of shadows as your weapon icon", 900, "🗡️"),
    ("Crystal Orb", "Magic", "Gaze into your destiny with a mystical crystal orb", 700, "🔮"),
]

DEMO_QUESTS = [
    ("Complete DSA Practice", "Learning", "MEDIUM", "Intelligence", 120, 30, "Today"),
    ("Morning Workout Session", "Health", "EASY", "Strength", 80, 20, "Today"),
    ("Read 30 Pages", "Learning", "EASY", "Intelligence", 60, 15, "Today"),
    ("Design System Documentation", "Creative", "HARD", "Creativity", 200, 50, "Tomorrow"),
    ("Code Review & Refactor", "Work", "MEDIUM", "Discipline", 140, 35, "Today"),
    ("Sketch Character Concepts", "Creative", "MEDIUM", "Creativity", 100, 25, "This Week"),
]


def run():
    with app.app_context():
        db.create_all()

        if not Achievement.query.first():
            for code, title, desc, xp, icon in ACHIEVEMENTS:
                db.session.add(Achievement(code=code, title=title, description=desc,
                                            xp_reward=xp, icon=icon))

        if not ShopItem.query.first():
            for name, cat, desc, price, icon in SHOP_ITEMS:
                db.session.add(ShopItem(name=name, category=cat, description=desc,
                                         price=price, icon=icon))
        db.session.commit()

        if not User.query.filter_by(username="aelindra").first():
            pw_hash = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode()
            user = User(
                username="aelindra",
                email="aelindra@liferpg.dev",
                password_hash=pw_hash,
                display_name="Aelindra Stormveil",
                title="Arcane Adventurer",
                avatar="🧙",
                level=12,
                xp=1240,
                xp_to_next=1500,
                gold=2450,
                streak=14,
                best_streak=14,
                last_active_date=date.today() - timedelta(days=1),
            )
            db.session.add(user)
            db.session.flush()

            db.session.add(Attributes(
                user_id=user.id, strength=34, intelligence=67,
                discipline=51, creativity=45, vitality=72,
            ))

            for title, cat, diff, attr, xp, gold, due in DEMO_QUESTS:
                db.session.add(Quest(
                    user_id=user.id, title=title, category=cat, difficulty=diff,
                    attribute=attr, xp_reward=xp, gold_reward=gold, due_label=due,
                ))

            legendary_frame = ShopItem.query.filter_by(name="Legendary Frame").first()
            if legendary_frame:
                db.session.add(UserInventory(user_id=user.id, item_id=legendary_frame.id,
                                              equipped=True))

            db.session.commit()
            print("Seeded demo user 'aelindra' / password 'password123'")

        print("Seed complete.")


if __name__ == "__main__":
    run()
