import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check local model weight availability
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "ml", "models", settings.LLM_MODEL_ID)
    model_weights_available = os.path.exists(model_path) and len(os.listdir(model_path)) > 0 if os.path.exists(model_path) else False

    model_health = {
        "status": "healthy" if model_weights_available else "degraded",
        "reason": "Local weights active" if model_weights_available else "Local weights not present; deterministic grounded fallback active",
        "fallbackAvailable": True
    }

    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": db_status,
        "model_health": model_health,
        "llm_provider": "LocalAutoMindProvider (local curated engine — no external API)",
        "llm_model": settings.LLM_MODEL_ID,
        "embedding_model": settings.EMBEDDING_MODEL_ID
    }
