"""FastAPI application factory and main entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.logging import setup_logging
from app.db.mongodb import init_db, close_db
from app.db.qdrant import init_qdrant, close_qdrant
from app.api.router import api_router
from app.middleware.monitoring import MonitoringMiddleware
from app.middleware.logging import LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    settings = get_settings()
    setup_logging(settings.log_level)

    # Startup
    app.state.mongo_client = await init_db(settings)
    app.state.qdrant_client = await init_qdrant(settings)

    yield

    # Shutdown
    await close_db(app.state.mongo_client)
    await close_qdrant(app.state.qdrant_client)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Enterprise Knowledge Assistant API",
        description="Secure RAG-powered internal knowledge assistant with RBAC, guardrails, and monitoring",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            settings.frontend_url,
            "http://localhost:3000",
            "http://localhost:3001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware
    app.add_middleware(MonitoringMiddleware)
    app.add_middleware(LoggingMiddleware)

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
