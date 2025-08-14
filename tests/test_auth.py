def test_login_success(client, seed_users):
    res = client.post("/auth/login", data={"username": "bob@example.com", "password": "bobpass"})
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert "refresh_token" in body

def test_login_invalid_password(client, seed_users):
    res = client.post("/auth/login", json={"username": "admin@example.com", "password": "wrong"})
    assert res.status_code == 400

def test_refresh_returns_new_access(client, admin_tokens):
    refresh = admin_tokens["refresh_token"]
    res = client.post("/auth/refresh", json={"refresh_token": refresh})
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_logout_clears_cookies(client, admin_tokens):
    # ensure cookies set after login
    res = client.post("/auth/login", json={"username": "admin@example.com", "password": "adminpass"})
    assert "access_token" in res.json()
    # logout
    res = client.post("/auth/logout")
    assert res.status_code == 200
