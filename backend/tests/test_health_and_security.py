import os
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from pydantic import ValidationError
from alembic.config import Config
from alembic import command

from app.main import app
from app.db.session import get_db
from app.core.config import Settings, mask_database_url

def test_liveness_probe(client):
    """GET /api/v1/health/live should return 200 ok without DB interaction."""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_readiness_probe_success(client):
    """GET /api/v1/health/ready should return 200 when DB is connected."""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "connected"}

def test_readiness_probe_failure_503(client):
    """GET /api/v1/health/ready should return 503 when DB fails, without leaking credentials."""
    def mock_broken_db():
        mock = MagicMock()
        mock.execute.side_effect = Exception("OperationalError: unable to connect to secret_db://user:supersecret@dbhost:3306")
        yield mock

    app.dependency_overrides[get_db] = mock_broken_db
    try:
        response = client.get("/api/v1/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "not_ready"
        assert data["database"] == "disconnected"
        # Ensure no credential or traceback leakage
        assert "supersecret" not in response.text
        assert "OperationalError" not in response.text
    finally:
        # Reset dependency override
        from conftest import override_get_db
        app.dependency_overrides[get_db] = override_get_db

def test_general_health_check(client):
    """GET /api/v1/health returns application status with sanitized db check."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["database"] == "healthy"
    assert "model_health" in data

def test_mask_database_url():
    """Verify mask_database_url hides credentials."""
    url = "mysql+pymysql://automind_admin:SuperSecretPass123!@db.internal:3306/production_db"
    masked = mask_database_url(url)
    assert "SuperSecretPass123!" not in masked
    assert "automind_admin:****@db.internal" in masked

def test_config_production_fails_on_insecure_defaults():
    """Verify that Settings raises validation error when production has missing/default secrets."""
    with pytest.raises((ValueError, ValidationError), match="APP_SECRET"):
        Settings(
            APP_ENV="production",
            APP_SECRET="insecure-development-app-secret-key-change-me",
            JWT_SECRET="valid-long-secret-key-at-least-32-chars-ok",
            DATABASE_URL="mysql+pymysql://produser:prodpass@db:3306/proddb",
            CORS_ALLOWED_ORIGINS="https://automind.ai",
            DEBUG=False
        )

    with pytest.raises((ValueError, ValidationError), match="JWT_SECRET"):
        Settings(
            APP_ENV="production",
            APP_SECRET="valid-long-app-secret-at-least-32-chars-ok",
            JWT_SECRET="insecure-development-jwt-secret-key-change-me",
            DATABASE_URL="mysql+pymysql://produser:prodpass@db:3306/proddb",
            CORS_ALLOWED_ORIGINS="https://automind.ai",
            DEBUG=False
        )

    with pytest.raises((ValueError, ValidationError), match="wildcard"):
        Settings(
            APP_ENV="production",
            APP_SECRET="valid-long-app-secret-at-least-32-chars-ok",
            JWT_SECRET="valid-long-jwt-secret-at-least-32-chars-ok",
            DATABASE_URL="mysql+pymysql://produser:prodpass@db:3306/proddb",
            CORS_ALLOWED_ORIGINS="*",
            DEBUG=False
        )

    with pytest.raises((ValueError, ValidationError), match="DEBUG must be set to False"):
        Settings(
            APP_ENV="production",
            APP_SECRET="valid-long-app-secret-at-least-32-chars-ok",
            JWT_SECRET="valid-long-jwt-secret-at-least-32-chars-ok",
            DATABASE_URL="mysql+pymysql://produser:prodpass@db:3306/proddb",
            CORS_ALLOWED_ORIGINS="https://automind.ai",
            DEBUG=True
        )

def test_alembic_migration_upgrade_and_downgrade():
    """Alembic migration smoke test against isolated SQLite database."""
    test_db_path = "./alembic_smoke_test.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    try:
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alembic_cfg = Config(os.path.join(backend_dir, "alembic.ini"))
        alembic_cfg.set_main_option("script_location", os.path.join(backend_dir, "alembic"))
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{test_db_path}")

        # Test upgrade head
        command.upgrade(alembic_cfg, "head")

        # Test downgrade base
        command.downgrade(alembic_cfg, "base")
    finally:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
