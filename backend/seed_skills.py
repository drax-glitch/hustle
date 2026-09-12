"""Seed skills into the database."""
from app import create_app
from app.extensions import db
from app.models import Skill

app = create_app()

SKILLS = [
    # Strength Skills (IDs 1-3)
    ("Power I", "Increase Strength attribute rewards by 5%", "Strength", 1, None, "attribute_boost", 5, "💪"),
    ("Power II", "Increase Strength attribute rewards by 10%", "Strength", 2, 1, "attribute_boost", 10, "💪"),
    ("Mighty", "Increase Strength attribute rewards by 15%", "Strength", 3, 2, "attribute_boost", 15, "⚔️"),
    
    # Intelligence Skills (IDs 4-6)
    ("Fast Learner", "Increase XP from Intelligence quests by 5%", "Intelligence", 1, None, "xp_boost", 5, "🧠"),
    ("Deep Study", "Increase XP from Intelligence quests by 10%", "Intelligence", 2, 4, "xp_boost", 10, "📚"),
    ("Knowledge Master", "Increase XP from Intelligence quests by 15%", "Intelligence", 3, 5, "xp_boost", 15, "🎓"),
    
    # Discipline Skills (IDs 7-9)
    ("Focus I", "Increase Discipline attribute rewards by 5%", "Discipline", 1, None, "attribute_boost", 5, "🔥"),
    ("Focus II", "Increase Discipline attribute rewards by 10%", "Discipline", 2, 7, "attribute_boost", 10, "🔥"),
    ("Flow State", "Increase Discipline attribute rewards by 15%", "Discipline", 3, 8, "attribute_boost", 15, "🌊"),
    
    # Vitality Skills (IDs 10-12)
    ("Endurance I", "Increase Vitality attribute rewards by 5%", "Vitality", 1, None, "attribute_boost", 5, "❤️"),
    ("Recovery", "Increase Vitality attribute rewards by 10%", "Vitality", 2, 10, "attribute_boost", 10, "💊"),
    ("Vitality", "Increase Vitality attribute rewards by 15%", "Vitality", 3, 11, "attribute_boost", 15, "✨"),
    
    # Creativity Skills (IDs 13-15)
    ("Creative Flow", "Increase Creativity attribute rewards by 5%", "Creativity", 1, None, "attribute_boost", 5, "🎨"),
    ("Idea Generator", "Increase Creativity attribute rewards by 10%", "Creativity", 2, 13, "attribute_boost", 10, "💡"),
    ("Creative Mastery", "Increase Creativity attribute rewards by 15%", "Creativity", 3, 14, "attribute_boost", 15, "🎭"),
]

# Map for setting prerequisites after IDs are known
PREREQUISITE_MAP = {
    2: 1,   # Power II requires Power I
    3: 2,   # Mighty requires Power II
    5: 4,   # Deep Study requires Fast Learner
    6: 5,   # Knowledge Master requires Deep Study
    8: 7,   # Focus II requires Focus I
    9: 8,   # Flow State requires Focus II
    11: 10, # Recovery requires Endurance I
    12: 11, # Vitality requires Recovery
    14: 13, # Idea Generator requires Creative Flow
    15: 14, # Creative Mastery requires Idea Generator
}

def run():
    with app.app_context():
        db.create_all()  # Create tables including new Skill and UserSkill tables
        
        if not Skill.query.first():
            # First pass: create all skills without prerequisites
            for name, desc, attr, cost, prereq, effect_type, effect_value, icon in SKILLS:
                skill = Skill(
                    name=name,
                    description=desc,
                    attribute=attr,
                    cost=cost,
                    prerequisite_id=None,  # Set to None initially
                    effect_type=effect_type,
                    effect_value=effect_value,
                    icon=icon,
                )
                db.session.add(skill)
            db.session.commit()
            
            # Second pass: set prerequisites using actual IDs
            for skill_id, prereq_id in PREREQUISITE_MAP.items():
                skill = Skill.query.get(skill_id)
                if skill:
                    skill.prerequisite_id = prereq_id
            db.session.commit()
            
            print("Skills seeded successfully!")
        else:
            print("Skills already exist in database.")

if __name__ == "__main__":
    run()
