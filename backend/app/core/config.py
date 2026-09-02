import os
import logging
from typing import List, Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("automind.config")

DEV_DEFAULT_APP_SECRET = "super-secret-key-automind-2026"
DEV_DEFAULT_JWT_SECRET = "jwt-super-secret-key-change-me-automind-key-9988"

class Settings(BaseSettings):
    APP_NAME: str = "AutoMind AI"
    APP_ENV: str = "development"  # "development", "staging", "production"
    APP_SECRET: str = DEV_DEFAULT_APP_SECRET
    DEBUG: bool = True

    # Database Settings (Local MySQL with SQLite fallback)
    DATABASE_URL: str = "mysql+pymysql://automind_user:automind_pass@localhost:3306/automind_db"

    # JWT Settings
    JWT_SECRET: str = DEV_DEFAULT_JWT_SECRET
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
            return [o.strip() for o in self.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]
        if self.APP_ENV == "production":
            return [self.FRONTEND_URL]
        return [
            self.FRONTEND_URL,
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ]

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """Enforce strict production security checks and log dev warnings."""
        if self.APP_ENV == "production":
            if self.APP_SECRET == DEV_DEFAULT_APP_SECRET:
                raise ValueError("SECURITY ERROR: APP_SECRET must be configured with a strong secret in production. Generate using `openssl rand -hex 32`.")
            if self.JWT_SECRET == DEV_DEFAULT_JWT_SECRET:
                raise ValueError("SECURITY ERROR: JWT_SECRET must be configured with a strong secret in production. Generate using `openssl rand -hex 32`.")
            if "localhost" in self.DATABASE_URL and not os.getenv("ALLOW_LOCALHOST_DB_IN_PROD"):
                logger.warning("Production DATABASE_URL contains localhost.")
        else:
            if self.APP_SECRET == DEV_DEFAULT_APP_SECRET or self.JWT_SECRET == DEV_DEFAULT_JWT_SECRET:
                logger.info("[SECURITY NOTICE] Running in development mode with default local keys. In production, set APP_ENV=production with secure secrets.")
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
