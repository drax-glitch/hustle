def test_shop_buy_and_equip(client, auth_headers):
    headers = auth_headers()
    items = client.get("/api/shop", headers=headers).get_json()
    weapon = next(i for i in items if i["category"] == "Weapons")

    res = client.post(f"/api/shop/{weapon['id']}/buy", headers=headers)
    assert res.status_code == 200

    res = client.post(f"/api/shop/{weapon['id']}/equip", headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["item"]["equipped"] is True

    char = client.get("/api/character", headers=headers).get_json()
    assert any(e["category"] == "Weapons" for e in char["equipped"])

    res = client.post(f"/api/shop/{weapon['id']}/unequip", headers=headers)
    assert res.status_code == 200


def test_avatar_equip_updates_user(client, auth_headers):
    headers = auth_headers()
    items = client.get("/api/shop", headers=headers).get_json()
    avatar = next(i for i in items if i["category"] == "Avatars")

    client.post(f"/api/shop/{avatar['id']}/buy", headers=headers)
    res = client.post(f"/api/shop/{avatar['id']}/equip", headers=headers)
    assert res.status_code == 200
    assert res.get_json()["user"]["avatar"] == "🐉"


def test_equip_not_owned(client, auth_headers):
    headers = auth_headers()
    items = client.get("/api/shop", headers=headers).get_json()
    item_id = items[0]["id"]
    res = client.post(f"/api/shop/{item_id}/equip", headers=headers)
    assert res.status_code == 400
