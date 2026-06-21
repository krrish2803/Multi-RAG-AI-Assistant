"""Health check API routes."""

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.models.user import User

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "enterprise-knowledge-assistant"}


@router.get("/readiness")
async def readiness_check(settings: Settings = Depends(get_settings)):
    """Detailed readiness check for all dependencies."""
    checks = {}

    # Check MongoDB
    try:
        count = await User.find().count()
        checks["mongodb"] = {"status": "ready", "user_count": count}
    except Exception as e:
        checks["mongodb"] = {"status": "error", "error": str(e)}

    # Check Qdrant
    try:
        from qdrant_client import AsyncQdrantClient
        client = AsyncQdrantClient(**settings.get_qdrant_client_kwargs())
        collections = await client.get_collections()
        await client.close()
        checks["qdrant"] = {
            "status": "ready",
            "collections": [c.name for c in collections.collections],
        }
    except Exception as e:
        checks["qdrant"] = {"status": "error", "error": str(e)}

    all_ready = all(c["status"] == "ready" for c in checks.values())

    return {
        "status": "ready" if all_ready else "degraded",
        "checks": checks,
    }
