def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@automind.ai", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@automind.ai"

def test_login_failure(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@automind.ai", "password": "wrongpassword"}
    )
    assert response.status_code == 401
