"""MongoDB connection using Motor (async) and Beanie ODM."""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import Settings
from app.models.user import User
from app.models.document import IngestedDocument
from app.models.conversation import Conversation, Message
from app.models.metrics import RequestMetrics, GuardrailEvent, EvalRun, EvalResult


async def init_db(settings: Settings) -> AsyncIOMotorClient:
    """Initialize MongoDB connection and register Beanie document models."""
    client = AsyncIOMotorClient(settings.mongo_uri)

    # Test connection
    await client.admin.command("ping")

    # Initialize Beanie with all document models
    await init_beanie(
        database=client[settings.mongo_db],
        document_models=[
            User,
            IngestedDocument,
            Conversation,
            Message,
            RequestMetrics,
            GuardrailEvent,
            EvalRun,
            EvalResult,
        ],
    )

    return client


async def close_db(client: AsyncIOMotorClient) -> None:
    """Close MongoDB connection."""
    client.close()
