"""Qdrant vector database client and collection management."""

from typing import Optional

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    Filter,
    FieldCondition,
    MatchAny,
    PayloadSchemaType,
)

from app.config import Settings


async def init_qdrant(settings: Settings) -> AsyncQdrantClient:
    """Initialize Qdrant client and create collection if needed."""
    client = AsyncQdrantClient(**settings.get_qdrant_client_kwargs())

    # Check if collection exists, create if not
    collections = [c.name for c in (await client.get_collections()).collections]

    if settings.qdrant_collection not in collections:
        await client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(
                size=settings.qdrant_vector_size,
                distance=Distance.COSINE,
            ),
        )

        # Create payload indexes for RBAC filtering (critical for performance)
        await client.create_payload_index(
            collection_name=settings.qdrant_collection,
            field_name="department",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        await client.create_payload_index(
            collection_name=settings.qdrant_collection,
            field_name="sensitivity",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        await client.create_payload_index(
            collection_name=settings.qdrant_collection,
            field_name="document_id",
            field_schema=PayloadSchemaType.KEYWORD,
        )

    return client


async def close_qdrant(client: AsyncQdrantClient) -> None:
    """Close Qdrant client connection."""
    await client.close()
