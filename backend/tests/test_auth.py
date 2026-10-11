from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings
from app.core.security import create_access_token

def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@automind.ai", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@automind.ai"

def test_login_failure_wrong_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@automind.ai", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_login_failure_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@automind.ai", "password": "anypassword"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_reject_demo_user_bypass(client):
    """Ensure demo@automind.ai cannot login with arbitrary password or bypass auth."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@automind.ai", "password": "arbitrary_password_123"}
    )
    assert response.status_code == 401

def test_reject_demo_jwt_token_hardcoded_bypass(client):
    """Ensure legacy hardcoded demo JWT token is strictly rejected with 401."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer demo-jwt-token-automind-2026"}
    )
    assert response.status_code == 401

def test_missing_auth_header(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_malformed_jwt_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-valid-jwt-token"}
    )
    assert response.status_code == 401

def test_token_with_invalid_sub(client):
    """Token with non-numeric sub should return 401 rather than 500 error."""
    token = jwt.encode(
        {"sub": "not_an_int", "exp": datetime.utcnow() + timedelta(minutes=15)},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401

def test_expired_jwt_token(client):
    token = jwt.encode(
        {"sub": "1", "exp": datetime.utcnow() - timedelta(minutes=15)},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401

def test_valid_token_authenticated_endpoint(client):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test@automind.ai", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    
    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "test@automind.ai"

def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "New Registered User",
            "email": "unique_new_user@automind.ai",
            "password": "ValidPassword123",
            "confirm_password": "ValidPassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data
    assert data["user"]["email"] == "unique_new_user@automind.ai"
    assert data["user"]["full_name"] == "New Registered User"

def test_register_duplicate_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Duplicate User",
            "email": "test@automind.ai",
            "password": "ValidPassword123",
            "confirm_password": "ValidPassword123"
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_register_case_insensitive_duplicate_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Duplicate Upper User",
            "email": "TEST@AUTOMIND.AI",
            "password": "ValidPassword123",
            "confirm_password": "ValidPassword123"
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_register_password_mismatch(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Mismatch User",
            "email": "mismatch@automind.ai",
            "password": "ValidPassword123",
            "confirm_password": "DifferentPassword123"
        }
    )
    assert response.status_code == 400
    assert "Passwords do not match" in response.json()["detail"]

def test_register_short_password_validation(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Short Password User",
            "email": "short@automind.ai",
            "password": "short",
            "confirm_password": "short"
        }
    )
    assert response.status_code == 422
    assert "at least 8 characters" in response.json()["detail"]


