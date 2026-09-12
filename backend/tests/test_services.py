from datetime import date, timedelta, datetime, timezone

from app.extensions import db
from app.models import User, Attributes, Quest, Achievement, ShopItem, UserInventory
from app.services import apply_xp, _update_streak, check_achievements, equip_item, _utc_today


def _make_user(app, streak=0, last_active=None):
    with app.app_context():
        user = User(
            username="svcuser",
            email="svc@test.com",
            password_hash="x",
            display_name="Svc",
            streak=streak,
            last_active_date=last_active,
            best_streak=streak,
            gold=1000,
            daily_goal=1,
        )
        db.session.add(user)
        db.session.flush()
        db.session.add(Attributes(user_id=user.id))
        db.session.commit()
        return user.id


def _get_user(user_id):
    return db.session.get(User, user_id)


def test_streak_first_day(app):
    with app.app_context():
        user = _get_user(_make_user(app))
        _update_streak(user)
        assert user.streak == 1
        assert user.best_streak == 1


def test_streak_same_day_no_increment(app):
    with app.app_context():
        user = _get_user(_make_user(app, streak=1, last_active=_utc_today()))
        _update_streak(user)
        assert user.streak == 1


def test_streak_consecutive(app):
    with app.app_context():
        user = _get_user(_make_user(app, streak=2, last_active=_utc_today() - timedelta(days=1)))
        _update_streak(user)
        assert user.streak == 3
        assert user.best_streak == 3


def test_streak_reset_after_gap(app):
    with app.app_context():
        user = _get_user(_make_user(app, streak=5, last_active=_utc_today() - timedelta(days=3)))
        _update_streak(user)
        assert user.streak == 1


def test_level_up_and_multi_level(app):
    with app.app_context():
        user = User(username="lvl", email="lvl@test.com", password_hash="x", display_name="L", xp_to_next=100)
        db.session.add(user)
        db.session.commit()
        gained = apply_xp(user, 250)
        assert gained >= 2
        assert user.level >= 3


def test_achievement_unlock_and_xp(app):
    with app.app_context():
        user = User(username="ach", email="ach@test.com", password_hash="x", display_name="A")
        db.session.add(user)
        db.session.flush()
        db.session.add(Attributes(user_id=user.id))
        db.session.commit()

        quest = Quest(user_id=user.id, title="Q", category="Work", difficulty="EASY", attribute="Discipline",
                      xp_reward=10, gold_reward=5)
        quest.status = "COMPLETED"
        quest.completed_at = datetime.now(timezone.utc)
        db.session.add(quest)
        db.session.commit()

        old_level = user.level
        unlocked = check_achievements(user)
        assert len(unlocked) == 1
        assert user.xp >= 50 or user.level > old_level


def test_equip_owned_item(app):
    with app.app_context():
        user = User(username="eq", email="eq@test.com", password_hash="x", display_name="E", gold=500)
        db.session.add(user)
        db.session.flush()
        item = ShopItem(name="Avatar", category="Avatars", description="d", price=100, icon="🐲")
        db.session.add(item)
        db.session.flush()
        db.session.add(UserInventory(user_id=user.id, item_id=item.id))
        db.session.commit()

        equipped = equip_item(user, item.id)
        assert equipped.icon == "🐲"
        assert user.avatar == "🐲"
