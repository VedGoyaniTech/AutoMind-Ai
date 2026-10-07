"""
AutoMind AI — FastAPI Main Entrypoint for Vercel / ASGI Deployments
Exposes the root FastAPI application instance for Vercel Serverless Functions and Uvicorn.
"""
from app.main import app

__all__ = ["app"]
