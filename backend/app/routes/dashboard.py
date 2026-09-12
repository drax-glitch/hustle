from datetime import datetime
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.models import Quest, XPLog
from app.services import count_completed_today, _utc_today
from app.utils import get_user_id, get_current_user

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.get("/stats")
@jwt_required()
def dashboard_stats():
    user = get_current_user()
    user_id = get_user_id()
    today = _utc_today()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())

    completed_today = count_completed_today(user_id)
    total_completed = Quest.query.filter_by(user_id=user_id, status="COMPLETED").count()
    active_today = Quest.query.filter(
        Quest.user_id == user_id,
        Quest.status == "ACTIVE",
        Quest.due_label == "Today",
    ).count()
    completed_today_list = Quest.query.filter(
        Quest.user_id == user_id,
        Quest.status == "COMPLETED",
        Quest.completed_at >= start,
        Quest.completed_at <= end,
    ).count()

    xp_row = XPLog.query.filter_by(user_id=user_id, log_date=today).first()
    today_xp = xp_row.xp_earned if xp_row else 0
    today_gold = xp_row.gold_earned if xp_row else 0

    daily_goal = max(1, user.daily_goal or 5)
    remaining = max(0, daily_goal - completed_today)
    goal_complete = completed_today >= daily_goal

    return jsonify({
        "completedToday": completed_today,
        "dailyGoal": daily_goal,
        "remainingToday": remaining,
        "dailyGoalComplete": goal_complete,
        "dailyGoalBonusAwarded": user.daily_goal_bonus_date == today,
        "totalCompleted": total_completed,
        "activeToday": active_today,
        "activeTotal": Quest.query.filter_by(user_id=user_id, status="ACTIVE").count(),
        "todayXp": today_xp,
        "todayGold": today_gold,
    })
