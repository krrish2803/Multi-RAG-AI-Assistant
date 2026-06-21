"""Document models for ingested content."""

from datetime import datetime
from enum import Enum
from typing import Optional

from beanie import Document, Indexed
from pydantic import Field


class SensitivityLevel(str, Enum):
    """Document sensitivity levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class IngestedDocument(Document):
    """Metadata for ingested documents."""

    filename: str
    file_type: str  # pdf, docx, txt, csv
    file_size: int = 0
    file_path: Optional[str] = None
    department: str = "company-wide"
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL
    allowed_roles: list[str] = Field(default_factory=list)
    uploaded_by: str
    chunk_count: int = 0
    qdrant_collection: str = "knowledge_base"
    status: str = "pending"  # pending, processing, ready, failed
    version: int = 1
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "documents"

    class Config:
        json_schema_extra = {
            "example": {
                "filename": "company_policy.pdf",
                "file_type": "pdf",
                "department": "company-wide",
                "sensitivity": "internal",
            }
        }
