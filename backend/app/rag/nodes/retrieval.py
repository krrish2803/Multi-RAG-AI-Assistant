"""Retrieval node - searches Qdrant with RBAC filtering."""

from app.config import Settings
from app.rag.state import RAGState
from app.rag.embeddings import EmbeddingService
from app.core.rbac import build_qdrant_filter


async def retrieval_node(state: RAGState, settings: Settings) -> dict:
    """Retrieve relevant documents from Qdrant with RBAC filtering."""
    from qdrant_client import AsyncQdrantClient

    embedding_service = EmbeddingService(settings)

    # Embed the user query
    query_vector = await embedding_service.embed_text(state["user_query"])

    # Build RBAC filter
    from qdrant_client.models import FieldCondition, Filter, MatchValue

    rbac_filter = build_qdrant_filter(
        state["user_role"],
        state.get("user_departments", []),
    )

    # Optionally filter by specific document IDs (OR semantics)
    doc_ids = state.get("document_ids")
    if doc_ids:
        from qdrant_client.models import MatchAny
        rbac_filter.must = (rbac_filter.must or []) + [
            FieldCondition(key="document_id", match=MatchAny(any=doc_ids))
        ]

    # Search Qdrant
    client = AsyncQdrantClient(**settings.get_qdrant_client_kwargs())

    try:
        response = await client.query_points(
            collection_name=settings.qdrant_collection,
            query=query_vector,
            query_filter=rbac_filter,
            limit=5,
            with_payload=True,
        )
        results = response.points
    finally:
        await client.close()

    # Format results
    documents = []
    sources = []
    for hit in results:
        payload = hit.payload or {}
        documents.append({
            "content": payload.get("text", ""),
            "filename": payload.get("filename", "unknown"),
            "department": payload.get("department", "unknown"),
            "document_id": payload.get("document_id", ""),
            "chunk_index": payload.get("chunk_index", 0),
            "score": hit.score,
        })
        sources.append({
            "filename": payload.get("filename", "unknown"),
            "department": payload.get("department", "unknown"),
            "chunk_index": payload.get("chunk_index", 0),
            "score": hit.score,
            "content": payload.get("text", "")[:200],
        })

    return {
        "retrieved_documents": documents,
        "sources": sources,
    }
