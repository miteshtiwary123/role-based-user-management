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
    