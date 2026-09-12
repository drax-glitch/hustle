"""Shared helpers for auth identity, validation, and user lookup."""

import re
from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from app.models import User

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,50}$")

MAX_TITLE_LEN = 80
MAX_DISPLAY_NAME_LEN = 80
MAX_QUEST_TITLE_LEN = 150


def get_user_id():
    """JWT identity is stored as str; normalize to int for ORM queries."""
    return int(get_jwt_identity())


def get_current_user():
    return User.query.get_or_404(get_user_id())


def validate_registration(username, email, password):
    errors = []
    if not username or not USERNAME_RE.match(username):
        errors.append("username must be 3-50 characters (letters, numbers, underscore)")
    if not email or not EMAIL_RE.match(email):
        errors.append("valid email is required")
    if not password or len(password) < 8:
        errors.append("password must be at least 8 characters")
    return errors


def validate_quest_title(title):
    if not title or not str(title).strip():
        return "title is required"
    if len(str(title).strip()) > MAX_QUEST_TITLE_LEN:
        return f"title must be at most {MAX_QUEST_TITLE_LEN} characters"
    return None


def validation_error(message, status=400):
    return jsonify({"error": message}), status
