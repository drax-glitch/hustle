"""Chronicle API — always scoped to the authenticated user."""
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.chronicle_service import get_daily_chronicle, get_chronicle_history, get_today_summary
from app.utils import get_user_id

chronicle_bp = Blueprint("chronicle", __name__, url_prefix="/api/chronicle")


@chronicle_bp.get("")
@jwt_required()
def list_chronicle():
    user_id = get_user_id()
    days = int(request.args.get("days", 30))
    days = min(max(days, 1), 365)
    return jsonify(get_chronicle_history(user_id, days))


@chronicle_bp.get("/today")
@jwt_required()
def get_today_chronicle():
    return jsonify(get_today_summary(get_user_id()))


@chronicle_bp.get("/history")
@jwt_required()
def get_chronicle_history_route():
    user_id = get_user_id()
    days = int(request.args.get("days", 30))
    days = min(max(days, 1), 365)
    return jsonify(get_chronicle_history(user_id, days))


def _chronicle_for_date(date_str):
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None
    return get_daily_chronicle(get_user_id(), target_date)


@chronicle_bp.get("/date/<date_str>")
@jwt_required()
def get_chronicle_by_date(date_str):
    chronicle = _chronicle_for_date(date_str)
    if chronicle is None:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    return jsonify(chronicle)


@chronicle_bp.get("/<date_str>")
@jwt_required()
def get_chronicle_date_short(date_str):
    chronicle = _chronicle_for_date(date_str)
    if chronicle is None:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    return jsonify(chronicle)
