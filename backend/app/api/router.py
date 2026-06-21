"""Central API router aggregator."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.documents import router as documents_router
from app.api.v1.users import router as users_router
from app.api.v1.monitoring import router as monitoring_router
from app.api.v1.evaluation import router as evaluation_router
from app.api.v1.health import router as health_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring"])
api_router.include_router(evaluation_router, prefix="/evaluation", tags=["Evaluation"])
api_router.include_router(health_router, tags=["Health"])
