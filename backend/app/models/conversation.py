"""Conversation and Message models."""

from datetime import datetime
from typing import Optional

from beanie import Document, Indexed
from pydantic import Field


class Message(Document):
    """Individual chat message."""

    conversation_id: Indexed(str)
    role: str  # "user" or "assistant"
    content: str
    sources: Optional[list[dict]] = None  # Retrieved document chunks
    token_count: Optional[int] = None
    latency_ms: Optional[int] = None
    guardrail_flags: Optional[list[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "messages"


class Conversation(Document):
    """Chat conversation container."""

    user_id: Indexed(str)
    title: str
    message_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "conversations"
