def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password_hash" not in data

def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})
    response = client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})
    assert response.status_code == 409

def test_register_weak_password(client):
    response = client.post("/auth/register", json={"email": "weak@example.com", "password": "123"})
    assert response.status_code == 422

def test_login_success(client):
    client.post("/auth/register", json={"email": "login@example.com", "password": "password123"})
    response = client.post("/auth/login", data={"username": "login@example.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "wrong@example.com", "password": "password123"})
    response = client.post("/auth/login", data={"username": "wrong@example.com", "password": "wrongpass"})
    assert response.status_code == 401

def test_get_me_protected(client):
    client.post("/auth/register", json={"email": "me@example.com", "password": "password123"})
    login_resp = client.post("/auth/login", data={"username": "me@example.com", "password": "password123"})
    token = login_resp.json()["access_token"]
    
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"

def test_get_me_no_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_get_me_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401