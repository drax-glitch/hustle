from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import Skill, UserSkill, User
from app.utils import get_user_id, get_current_user, validation_error

skills_bp = Blueprint("skills", __name__, url_prefix="/api/skills")


@skills_bp.get("")
@jwt_required()
def list_skills():
    """Get all skills with unlock status for current user."""
    user_id = get_user_id()
    
    # Get all skills
    all_skills = Skill.query.all()
    
    # Get user's unlocked skills
    unlocked_ids = {
        us.skill_id
        for us in UserSkill.query.filter_by(user_id=user_id).all()
    }
    
    # Build response with unlock status and prerequisite info
    skills_data = []
    for skill in all_skills:
        skill_dict = skill.to_dict(unlocked=skill.id in unlocked_ids)
        
        # Add prerequisite info
        if skill.prerequisite_id:
            prereq_skill = Skill.query.get(skill.prerequisite_id)
            if prereq_skill:
                skill_dict["prerequisite"] = {
                    "id": prereq_skill.id,
                    "name": prereq_skill.name,
                    "unlocked": prereq_skill.id in unlocked_ids,
                }
            else:
                skill_dict["prerequisite"] = None
        else:
            skill_dict["prerequisite"] = None
        
        skills_data.append(skill_dict)
    
    return jsonify(skills_data)


@skills_bp.post("/<int:skill_id>/unlock")
@jwt_required()
def unlock_skill(skill_id):
    """Unlock a skill for the current user."""
    user = get_current_user()
    
    # Validate skill exists
    skill = Skill.query.get_or_404(skill_id)
    
    # Check if already unlocked
    existing = UserSkill.query.filter_by(user_id=user.id, skill_id=skill_id).first()
    if existing:
        return validation_error("skill already unlocked")
    
    # Check user has enough skill points
    if user.skill_points < skill.cost:
        return validation_error(f"need {skill.cost} skill points, have {user.skill_points}")
    
    # Check prerequisite is unlocked
    if skill.prerequisite_id:
        prereq_unlocked = UserSkill.query.filter_by(
            user_id=user.id, 
            skill_id=skill.prerequisite_id
        ).first()
        if not prereq_unlocked:
            prereq_skill = Skill.query.get(skill.prerequisite_id)
            return validation_error(f"unlock {prereq_skill.name} first")
    
    # Unlock the skill
    user.skill_points -= skill.cost
    db.session.add(UserSkill(user_id=user.id, skill_id=skill_id))
    from app.chronicle_service import log_chronicle_event
    log_chronicle_event(user.id, "skill_unlocked", {
        "id": skill.id,
        "name": skill.name,
        "attribute": skill.attribute,
    })
    db.session.commit()
    
    return jsonify({
        "skill": skill.to_dict(unlocked=True),
        "skillPoints": user.skill_points,
    })
