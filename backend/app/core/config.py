import os
import re
import logging
from typing import List, Optional, Set
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("automind.config")

# Known insecure development secrets that MUST NOT be used in production
KNOWN_DEV_SECRETS: Set[str] = {
    "super-secret-key-automind-2026",
    "jwt-super-secret-key-change-me-automind-key-9988",
    "dev-insecure-app-secret-do-not-use-in-prod-2026",
    "dev-insecure-jwt-secret-do-not-use-in-prod-2026",
    "your-strong-app-secret-here-use-openssl-rand-hex-32",
    "your-strong-jwt-secret-here-use-openssl-rand-hex-32",
    "secret",
    "changeme",
    "password",
    "admin",
    "default"
}

DEV_DEFAULT_APP_SECRET = "dev-insecure-app-secret-do-not-use-in-prod-2026"
DEV_DEFAULT_JWT_SECRET = "dev-insecure-jwt-secret-do-not-use-in-prod-2026"
DEV_DEFAULT_DB_URL = "mysql+pymysql://automind_user:automind_pass@localhost:3306/automind_db"

def mask_database_url(url: Optional[str]) -> str:
    """Mask credentials in database URL for safe logging."""
    if not url:
        return "[NOT SET]"
    return re.sub(r':([^@/]+)@', ':****@', url)

class Settings(BaseSettings):
    APP_NAME: str = "AutoMind AI"
    APP_ENV: str = "development"  # "development", "staging", "production"
    APP_SECRET: Optional[str] = None
    DEBUG: bool = False

    # Database Settings
    DATABASE_URL: Optional[str] = None

    # JWT Settings
    JWT_SECRET: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # AI & LLM Settings
    LLM_PROVIDER: str = "local"
    LLM_MODEL_ID: str = "qwen_lora_v4"
    EMBEDDING_MODEL_ID: str = "all-MiniLM-L6-v2"

    # Vector Store Settings
    VECTOR_STORE_TYPE: str = "local"
    VECTOR_INDEX_PATH: str = "./vector_index"

    # RAG Settings
    RETRIEVAL_TOP_K: int = 20
    RERANK_TOP_K: int = 8
    MAX_CONTEXT_DOCUMENTS: int = 8
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # Real-time Web Grounding Settings
    ENABLE_DUCKDUCKGO_SEARCH: bool = True
    DUCKDUCKGO_MAX_RESULTS: int = 5

    # Ingestion Settings
    INGESTION_BATCH_SIZE: int = 1000

    # CORS Configuration
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ALLOWED_ORIGINS: Optional[str] = None

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated allowed origins or return safe development defaults."""
        if self.CORS_ALLOWED_ORIGINS:
            origins = [o.strip() for o in self.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]
            return origins
        if self.APP_ENV in ("production", "prod", "staging"):
            # Never default production CORS to a localhost URL
            if self.FRONTEND_URL and "localhost" not in self.FRONTEND_URL and "127.0.0.1" not in self.FRONTEND_URL:
                return [self.FRONTEND_URL.strip()]
            return []
        return [
            self.FRONTEND_URL,
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ]

    @model_validator(mode="after")
    def validate_environment_and_security(self) -> "Settings":
        """
        Enforce strict production security checks and log development notices.
        Fails fast at startup in production if secrets, DB, or CORS are unsafe.
        """
        is_prod = self.APP_ENV in ("production", "prod", "staging")

        if is_prod:
            # 1. DEBUG must be False in production
            if self.DEBUG:
                raise ValueError(
                    "Production configuration error: DEBUG must be set to False in production environment."
                )

            # 2. APP_SECRET validation
            if (
                not self.APP_SECRET
                or not self.APP_SECRET.strip()
                or self.APP_SECRET in KNOWN_DEV_SECRETS
                or any(bad in self.APP_SECRET.lower() for bad in ("insecure", "change-me", "changeme"))
            ):
                raise ValueError(
                    "Production configuration error: APP_SECRET is missing, blank, or equals an insecure development default. "
                    "Generate a strong 256-bit secret using `openssl rand -hex 32`."
                )

            # 3. JWT_SECRET validation
            if (
                not self.JWT_SECRET
                or not self.JWT_SECRET.strip()
                or self.JWT_SECRET in KNOWN_DEV_SECRETS
                or any(bad in self.JWT_SECRET.lower() for bad in ("insecure", "change-me", "changeme"))
            ):
                raise ValueError(
                    "Production configuration error: JWT_SECRET is missing, blank, or equals an insecure development default. "
                    "Generate a strong 256-bit secret using `openssl rand -hex 32`."
                )

            # 4. DATABASE_URL validation
            if not self.DATABASE_URL or not self.DATABASE_URL.strip():
                raise ValueError(
                    "Production configuration error: DATABASE_URL is missing or blank. Provide a valid production database connection string."
                )

            # 5. CORS_ALLOWED_ORIGINS validation in production
            if not self.CORS_ALLOWED_ORIGINS or not self.CORS_ALLOWED_ORIGINS.strip():
                raise ValueError(
                    "Production configuration error: CORS_ALLOWED_ORIGINS is missing or blank. "
                    "Explicitly set comma-separated production origins (e.g. 'https://automind.ai')."
                )

            origins = [o.strip() for o in self.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]
            if any(o == "*" for o in origins):
                raise ValueError(
                    "Production configuration error: CORS_ALLOWED_ORIGINS cannot contain wildcard '*' while credentials are enabled."
                )
            if any("localhost" in o or "127.0.0.1" in o for o in origins):
                logger.warning("[PRODUCTION NOTICE] CORS_ALLOWED_ORIGINS contains localhost addresses.")

        else:
            # Development fallback with explicit security warnings
            if not self.APP_SECRET or self.APP_SECRET in KNOWN_DEV_SECRETS:
                self.APP_SECRET = DEV_DEFAULT_APP_SECRET
                logger.warning("[SECURITY WARNING] APP_SECRET using insecure development default. Never deploy with this secret.")

            if not self.JWT_SECRET or self.JWT_SECRET in KNOWN_DEV_SECRETS:
                self.JWT_SECRET = DEV_DEFAULT_JWT_SECRET
                logger.warning("[SECURITY WARNING] JWT_SECRET using insecure development default. Never deploy with this secret.")

            if not self.DATABASE_URL or not self.DATABASE_URL.strip():
                self.DATABASE_URL = DEV_DEFAULT_DB_URL
                logger.warning("[SECURITY WARNING] DATABASE_URL not set. Defaulting to local development MySQL: %s", mask_database_url(self.DATABASE_URL))

        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
