"""
FastAPI application entry point.

This module creates and configures the FastAPI application, wiring up CORS,
routes and settings.  The actual chat implementation lives in
``app/routes/chat.py``; configuration is provided via environment variables as
described in ``app/config.py``.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routes import chat


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(title="Grok Chatbot", version="0.1.0")

    # Configure CORS to allow requests from the front‑end during development.
    # Multiple origins can be supplied as a comma‑separated string.
    origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes under the /api prefix
    app.include_router(chat.router, prefix="/api")

    return app


# Instantiate the application for use by ASGI servers like Uvicorn
app = create_app()
