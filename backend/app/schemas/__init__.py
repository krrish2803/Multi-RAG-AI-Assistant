"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import Role
from app.models.document import SensitivityLevel


# ============================================
# Auth Schemas
# ============================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ============================================
# User Schemas
# ============================================

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: Role
    departments: list[str]
    is_active: bool
    created_at: datetime


class UserUpdateRequest(BaseModel):
    role: Optional[Role] = None
    departments: Optional[list[str]] = None
    is_active: Optional[bool] = None


# ============================================
# Chat Schemas
# ============================================

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class SourceCitation(BaseModel):
    filename: str
    department: str
    chunk_index: int
    score: float
    content_snippet: str


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: list[SourceCitation] = Field(default_factory=list)
    blocked: bool = False
    block_reason: Optional[str] = None
    latency_ms: int = 0


class ConversationResponse(BaseModel):
    id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sources: Optional[list[dict]] = None
    created_at: datetime


# ============================================
# Document Schemas
# ============================================

class DocumentUploadRequest(BaseModel):
    department: str = "company-wide"
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL
    allowed_roles: list[str] = Field(default_factory=list)


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    department: str
    sensitivity: str
    status: str
    chunk_count: int
    uploaded_by: str
    created_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


# ============================================
# Monitoring Schemas
# ============================================

class MonitoringSummary(BaseModel):
    total_requests: int
    avg_latency_ms: float
    total_tokens: int
    total_cost_usd: float
    guardrail_triggers: int
    error_count: int


class CostSummary(BaseModel):
    total_cost_usd: float
    cost_by_role: dict[str, float]
    cost_by_model: dict[str, float]


class ErrorSummary(BaseModel):
    total_errors: int
    recent_errors: list[dict]


class GuardrailSummary(BaseModel):
    total_triggers: int
    by_type: dict[str, int]


# ============================================
# Evaluation Schemas
# ============================================

class EvalRunRequest(BaseModel):
    dataset_name: str = "default"
    run_name: Optional[str] = None


class EvalRunResponse(BaseModel):
    id: str
    run_name: str
    dataset_name: str
    total_questions: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime


class EvalResultResponse(BaseModel):
    id: str
    run_id: str
    question: str
    ground_truth: str
    generated_answer: str
    faithfulness: Optional[float] = None
    answer_relevancy: Optional[float] = None
    context_precision: Optional[float] = None
    context_recall: Optional[float] = None
