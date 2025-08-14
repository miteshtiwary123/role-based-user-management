from app.models.user import RoleEnum

def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}

def test_admin_can_create_user(client, admin_tokens):
    hdrs = auth_header(admin_tokens["access_token"])
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "alicepass",
        "role": "user"
    }
    res = client.post("/users/", json=payload, headers=hdrs)
    assert res.status_code == 200
    assert res.json()["email"] == "alice@example.com"

def test_user_cannot_create_user(client, user_tokens):
    hdrs = auth_header(user_tokens["access_token"])
    payload = {"name": "Eve", "email": "eve@example.com", "password": "pass", "role": "user"}
    res = client.post("/users/", json=payload, headers=hdrs)
    assert res.status_code == 403

def test_list_users_requires_auth(client):
    res = client.get("/users/")
    assert res.status_code == 401

def test_list_users_pagination_and_meta(client, admin_tokens):
    hdrs = auth_header(admin_tokens["access_token"])
    # create a few users
    for i in range(15):
        client.post("/users/", json={
            "name": f"U{i}",
            "email": f"u{i}@example.com",
            "password": "x",
            "role": "user"
        }, headers=hdrs)
    # fetch with limit/offset
    res = client.get("/users/?limit=5&offset=10", headers=hdrs)
    assert res.status_code == 200
    data = res.json()
    assert data["meta"]["limit"] == 5
    assert data["meta"]["offset"] == 10
    assert data["meta"]["total"] >= 15  # plus seeded users
    assert len(data["items"]) == 5

def test_list_users_filtering_and_sorting(client, admin_tokens):
    hdrs = auth_header(admin_tokens["access_token"])
    # Ensure some predictable users
    client.post("/users/", json={"name": "Charlie", "email": "charlie@x.com", "password": "x", "role": "user"}, headers=hdrs)
    client.post("/users/", json={"name": "Charlotte", "email": "charlotte@x.com", "password": "x", "role": "user"}, headers=hdrs)

    # search by q
    res = client.get("/users/?q=charl&sort_by=name&sort_order=asc", headers=hdrs)
    assert res.status_code == 200
    names = [u["name"] for u in res.json()["items"]]
    assert "Charlie" in names and "Charlotte" in names

    # filter by role
    res = client.get("/users/?role=admin", headers=hdrs)
    assert res.status_code == 200
    assert any(u["role"] == "admin" for u in res.json()["items"])

def test_update_and_delete_user(client, admin_tokens):
    hdrs = auth_header(admin_tokens["access_token"])
    # create a target user
    res = client.post("/users/", json={"name": "Temp", "email": "temp@x.com", "password": "p"}, headers=hdrs)
    uid = res.json()["id"]
    # update
    res = client.put(f"/users/{uid}", json={"name": "Temp2", "email": "temp2@x.com"}, headers=hdrs)
    assert res.status_code == 200
    assert res.json()["name"] == "Temp2"
    # delete
    res = client.delete(f"/users/{uid}", headers=hdrs)
    assert res.status_code == 200
