import os
import pytest

# Force in-memory DB before app factory runs
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["FLASK_ENV"] = "development"

from app import create_app
from app.extensions import db
from app.models import Achievement, ShopItem


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret",
        "JWT_SECRET_KEY": "test-jwt-secret",
    })
    with app.app_context():
        db.create_all()
        if not Achievement.query.first():
            for code, title, desc, xp, icon in [
                ("FIRST_QUEST", "First Quest", "Complete your first quest", 50, "🏆"),
                ("WELLNESS_MASTER", "Wellness Master", "Complete 10 Wellness quests", 150, "🧘"),
                ("QUEST_MASTER", "Quest Master", "Create 50 quests", 300, "🛠️"),
            ]:
                db.session.add(Achievement(code=code, title=title, description=desc, xp_reward=xp, icon=icon))
        if not ShopItem.query.first():
            db.session.add(ShopItem(name="Dragon Avatar", category="Avatars", description="A dragon", price=100, icon="🐉"))
            db.session.add(ShopItem(name="Shadow Blade", category="Weapons", description="A blade", price=50, icon="🗡️"))
        db.session.commit()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    def _register_and_login(username="testuser", email="test@example.com", password="password123"):
        client.post("/api/auth/register", json={
            "username": username,
            "email": email,
            "password": password,
            "displayName": "Test User",
        })
        res = client.post("/api/auth/login", json={"username": username, "password": password})
        token = res.get_json()["token"]
        return {"Authorization": f"Bearer {token}"}
    return _register_and_login
