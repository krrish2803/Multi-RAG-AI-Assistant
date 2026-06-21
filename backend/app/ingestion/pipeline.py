"""Document ingestion pipeline - parse, chunk, embed, and store."""

import os
from pathlib import Path
from typing import Optional

from app.config import Settings
from app.models.document import IngestedDocument
from app.ingestion.parsers import get_parser
from app.ingestion.chunker import Chunker
from app.rag.embeddings import EmbeddingService
from app.core.rbac import ROLE_ACCESS_MATRIX


class IngestionPipeline:
    """Pipeline for processing documents into vector store."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.chunker = Chunker(chunk_size=512, chunk_overlap=64)
        self.embedding_service = EmbeddingService(settings)

    async def process(
        self,
        document_id: str,
        file_path: str,
        filename: str,
        department: str,
        sensitivity: str,
        uploaded_by: str,
    ) -> None:
        """Process a document: parse -> chunk -> embed -> store in Qdrant."""
        try:
            # Update status to processing
            doc = await IngestedDocument.get(document_id)
            if doc:
                doc.status = "processing"
                await doc.save()

            # Parse file to text
            parser = get_parser(file_path)
            text = parser.parse(file_path)

            if not text or len(text.strip()) < 10:
                raise ValueError("Document contains no extractable text")

            # Build metadata
            allowed_roles = list(ROLE_ACCESS_MATRIX.keys())  # All roles that can access this department
            metadata = {
                "document_id": document_id,
                "filename": filename,
                "department": department,
                "sensitivity": sensitivity,
                "uploaded_by": uploaded_by,
                "file_type": Path(file_path).suffix.lstrip("."),
            }

            # Chunk text
            chunks = self.chunker.split(text, metadata)

            if not chunks:
                raise ValueError("No chunks generated from document")

            # Embed chunks in batch
            chunk_texts = [c["text"] for c in chunks]
            embeddings = await self.embedding_service.embed_batch(chunk_texts)

            # Upsert to Qdrant
            from qdrant_client import AsyncQdrantClient
            from qdrant_client.models import PointStruct

            client = AsyncQdrantClient(**self.settings.get_qdrant_client_kwargs())

            try:
                points = []
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    point_id = f"{document_id}_{i}"
                    # Use deterministic ID based on document and chunk
                    import hashlib
                    hash_val = hashlib.md5(point_id.encode()).hexdigest()
                    numeric_id = int(hash_val[:16], 16)

                    points.append(PointStruct(
                        id=numeric_id,
                        vector=embedding,
                        payload={
                            "text": chunk["text"],
                            "filename": filename,
                            "department": department,
                            "sensitivity": sensitivity,
                            "document_id": document_id,
                            "chunk_index": i,
                            "uploaded_by": uploaded_by,
                            "file_type": metadata["file_type"],
                        },
                    ))

                # Batch upsert
                batch_size = 100
                for i in range(0, len(points), batch_size):
                    batch = points[i:i + batch_size]
                    await client.upsert(
                        collection_name=self.settings.qdrant_collection,
                        points=batch,
                    )
            finally:
                await client.close()

            # Update document status
            doc = await IngestedDocument.get(document_id)
            if doc:
                doc.status = "ready"
                doc.chunk_count = len(chunks)
                await doc.save()

        except Exception as e:
            # Update document status on failure
            doc = await IngestedDocument.get(document_id)
            if doc:
                doc.status = "failed"
                doc.error_message = str(e)
                await doc.save()
            raise
