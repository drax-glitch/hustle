from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import ShopItem, UserInventory
from app.services import equip_item, unequip_item
from app.utils import get_user_id, get_current_user, validation_error

shop_bp = Blueprint("shop", __name__, url_prefix="/api/shop")


def _inventory_map(user_id):
    rows = UserInventory.query.filter_by(user_id=user_id).all()
    return {row.item_id: row for row in rows}


@shop_bp.get("")
@jwt_required()
def list_items():
    user_id = get_user_id()
    category = request.args.get("category")

    query = ShopItem.query
    if category and category != "All":
        query = query.filter_by(category=category)
    items = query.all()

    inv = _inventory_map(user_id)
    return jsonify([
        item.to_dict(
            owned=item.id in inv,
            equipped=inv[item.id].equipped if item.id in inv else False,
        )
        for item in items
    ])


@shop_bp.post("/<int:item_id>/buy")
@jwt_required()
def buy_item(item_id):
    user_id = get_user_id()
    user = get_current_user()
    item = ShopItem.query.get_or_404(item_id)

    if UserInventory.query.filter_by(user_id=user_id, item_id=item_id).first():
        return validation_error("item already owned")

    if user.gold < item.price:
        return validation_error("not enough gold")

    user.gold -= item.price
    db.session.add(UserInventory(user_id=user_id, item_id=item_id))
    db.session.commit()

    return jsonify({
        "item": item.to_dict(owned=True, equipped=False),
        "goldRemaining": user.gold,
    })


@shop_bp.post("/<int:item_id>/equip")
@jwt_required()
def equip(item_id):
    user = get_current_user()
    try:
        item = equip_item(user, item_id)
    except ValueError as exc:
        return validation_error(str(exc))
    db.session.commit()
    return jsonify({
        "item": item.to_dict(owned=True, equipped=True),
        "user": user.to_dict(),
    })


@shop_bp.post("/<int:item_id>/unequip")
@jwt_required()
def unequip(item_id):
    user = get_current_user()
    try:
        item = unequip_item(user, item_id)
    except ValueError as exc:
        return validation_error(str(exc))
    db.session.commit()
    return jsonify({
        "item": item.to_dict(owned=True, equipped=False),
        "user": user.to_dict(),
    })
