import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.session import engine, Base
from app.api.v1.auth import router as auth_router
from app.api.v1.cars import router as cars_router
from app.api.v1.conversations import router as conv_router
from app.api.v1.chat import router as chat_router
from app.api.v1.saved import router as saved_router
from app.api.v1.admin import router as admin_router
from app.api.v1.health import router as health_router
from app.api.v1.pricing import router as pricing_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.voice import router as voice_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("automind.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing AutoMind AI Backend...")
    # Automatically create database tables if they do not exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema verified.")

    # Auto-seed database if empty
    try:
        from scripts.seed_db import seed
        seed()
        logger.info("Initial data auto-seeded successfully.")
    except Exception as e:
        logger.info(f"Auto-seed status: {e}")

    yield
    logger.info("AutoMind AI Backend shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent Automotive Research Assistant API with Hybrid RAG Retrieval",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    logger.error(f"Unhandled Exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again."}
    )

# Include Routers under /api/v1
api_prefix = "/api/v1"
app.include_router(health_router, prefix=api_prefix)
app.include_router(auth_router, prefix=api_prefix)
app.include_router(cars_router, prefix=api_prefix)
app.include_router(conv_router, prefix=api_prefix)
app.include_router(chat_router, prefix=api_prefix)
app.include_router(saved_router, prefix=api_prefix)
app.include_router(admin_router, prefix=api_prefix)
app.include_router(pricing_router, prefix=api_prefix)
app.include_router(feedback_router, prefix=api_prefix)
app.include_router(voice_router, prefix=api_prefix)

@app.get("/")
def root():
    return {"message": "AutoMind AI Core API Server is active.", "docs_url": "/docs"}
