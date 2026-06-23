"""Document management API routes."""

import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks
from typing import Optional

from app.config import Settings, get_settings
from app.models.user import User
from app.models.document import IngestedDocument, SensitivityLevel
from app.schemas import DocumentResponse, DocumentListResponse
from app.api.deps import get_current_user, require_admin
from app.ingestion.pipeline import IngestionPipeline

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "uploads")


def document_to_response(doc: IngestedDocument) -> DocumentResponse:
    """Convert document model to response schema."""
    return DocumentResponse(
        id=str(doc.id),
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        department=doc.department,
        sensitivity=doc.sensitivity.value if isinstance(doc.sensitivity, SensitivityLevel) else doc.sensitivity,
        status=doc.status,
        chunk_count=doc.chunk_count,
        uploaded_by=doc.uploaded_by,
        created_at=doc.created_at,
    )


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    department: str = Form("company-wide"),
    sensitivity: str = Form("internal"),
    user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    """Upload a document and trigger ingestion pipeline."""
    max_size = 100 * 1024 * 1024  # 100 MB

    # Validate file type
    allowed_types = {".pdf", ".docx", ".txt", ".csv", ".xlsx", ".xls"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_types:
        from app.core.exceptions import ValidationError
        raise ValidationError(f"File type {file_ext} not supported. Allowed: {', '.join(allowed_types)}")

    # Read and validate file
    document_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{document_id}_{file.filename}")
    content = await file.read()
    if len(content) > max_size:
        raise ValidationError(f"File too large ({len(content) / 1024 / 1024:.1f} MB). Maximum allowed: 100 MB")

    # Save file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(content)

    # Create document record
    doc = IngestedDocument(
        filename=file.filename,
        file_type=file_ext.lstrip("."),
        file_size=len(content),
        file_path=file_path,
        department=department,
        sensitivity=SensitivityLevel(sensitivity),
        uploaded_by=user.email,
        status="processing",
    )
    await doc.insert()

    # Run ingestion in background
    background_tasks.add_task(
        run_ingestion,
        str(doc.id),
        file_path,
        file.filename,
        department,
        sensitivity,
        user.email,
        settings,
    )

    return document_to_response(doc)


async def run_ingestion(
    document_id: str,
    file_path: str,
    filename: str,
    department: str,
    sensitivity: str,
    uploaded_by: str,
    settings: Settings,
):
    """Background task to run the ingestion pipeline."""
    try:
        pipeline = IngestionPipeline(settings)
        await pipeline.process(
            document_id=document_id,
            file_path=file_path,
            filename=filename,
            department=department,
            sensitivity=sensitivity,
            uploaded_by=uploaded_by,
        )
    except Exception as e:
        # Update document status on failure
        doc = await IngestedDocument.get(document_id)
        if doc:
            doc.status = "failed"
            doc.error_message = str(e)
            await doc.save()


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    department: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    user: User = Depends(get_current_user),
):
    """List all documents with optional filters."""
    query = {}
    if department:
        query["department"] = department
    if status:
        query["status"] = status

    documents = await IngestedDocument.find(query).sort("-created_at").skip(skip).limit(limit).to_list()
    total = await IngestedDocument.find(query).count()

    return DocumentListResponse(
        documents=[document_to_response(doc) for doc in documents],
        total=total,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    user: User = Depends(get_current_user),
):
    """Get a specific document by ID."""
    doc = await IngestedDocument.get(document_id)
    if doc is None:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Document")

    return document_to_response(doc)


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    user: User = Depends(require_admin),
    settings: Settings = Depends(get_settings),
):
    """Delete a document and its vector embeddings (admin only)."""
    doc = await IngestedDocument.get(document_id)
    if doc is None:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Document")

    # Delete from Qdrant
    try:
        from qdrant_client import AsyncQdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        qdrant = AsyncQdrantClient(**settings.get_qdrant_client_kwargs())
        await qdrant.delete(
            collection_name=settings.qdrant_collection,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            ),
        )
        await qdrant.close()
    except Exception:
        pass  # Best effort cleanup

    # Delete file if exists
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # Delete from MongoDB
    await doc.delete()

    return {"message": "Document deleted"}
