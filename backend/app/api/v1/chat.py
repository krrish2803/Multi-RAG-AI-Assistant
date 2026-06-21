"""Chat API routes with SSE streaming support."""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.config import Settings, get_settings
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.metrics import RequestMetrics
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    MessageResponse,
    SourceCitation,
)
from app.api.deps import get_current_user
from app.services.chat_service import ChatService

router = APIRouter()


def get_chat_service(settings: Settings = Depends(get_settings)) -> ChatService:
    """Dependency to get chat service instance."""
    return ChatService(settings)


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    """Send a message and get AI response using RAG pipeline."""
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())

    chat_service = ChatService(settings)

    try:
        result = await chat_service.process_message(
            user=user,
            message=request.message,
            conversation_id=request.conversation_id,
            request_id=request_id,
        )

        latency_ms = int((time.perf_counter() - start_time) * 1000)

        # Log metrics
        await RequestMetrics(
            request_id=request_id,
            user_id=str(user.id),
            user_email=user.email,
            user_role=user.role.value,
            endpoint="/chat/send",
            method="POST",
            status_code=200,
            latency_ms=latency_ms,
            prompt_tokens=result.get("prompt_tokens", 0),
            completion_tokens=result.get("completion_tokens", 0),
            total_tokens=result.get("total_tokens", 0),
            estimated_cost_usd=result.get("estimated_cost", 0.0),
            guardrail_triggered=result.get("blocked", False),
        ).insert()

        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            sources=[
                SourceCitation(
                    filename=s.get("filename", "unknown"),
                    department=s.get("department", "unknown"),
                    chunk_index=s.get("chunk_index", 0),
                    score=s.get("score", 0.0),
                    content_snippet=s.get("content", "")[:200],
                )
                for s in result.get("sources", [])
            ],
            blocked=result.get("blocked", False),
            block_reason=result.get("block_reason"),
            latency_ms=latency_ms,
        )

    except Exception as e:
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        await RequestMetrics(
            request_id=request_id,
            user_id=str(user.id),
            user_email=user.email,
            user_role=user.role.value,
            endpoint="/chat/send",
            method="POST",
            status_code=500,
            latency_ms=latency_ms,
            error_message=str(e),
        ).insert()
        raise


@router.post("/send/stream")
async def send_message_stream(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    """Send a message and stream the response via SSE."""
    chat_service = ChatService(settings)

    async def event_generator():
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        try:
            result = await chat_service.process_message(
                user=user,
                message=request.message,
                conversation_id=request.conversation_id,
                request_id=request_id,
            )

            # Stream response in chunks
            response_text = result["response"]
            chunk_size = 20
            for i in range(0, len(response_text), chunk_size):
                chunk = response_text[i : i + chunk_size]
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                await asyncio.sleep(0.02)

            # Send final event with sources
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            yield f"data: {json.dumps({'type': 'done', 'sources': result.get('sources', []), 'conversation_id': result['conversation_id'], 'latency_ms': latency_ms})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(user: User = Depends(get_current_user)):
    """List all conversations for the current user."""
    conversations = await Conversation.find(
        Conversation.user_id == str(user.id)
    ).sort("-updated_at").to_list(100)

    return [
        ConversationResponse(
            id=str(c.id),
            title=c.title,
            message_count=c.message_count,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}", response_model=list[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    user: User = Depends(get_current_user),
):
    """Get all messages in a conversation."""
    # Verify conversation ownership
    conversation = await Conversation.get(conversation_id)
    if conversation is None or conversation.user_id != str(user.id):
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Conversation")

    messages = await Message.find(
        Message.conversation_id == conversation_id
    ).sort("created_at").to_list(1000)

    return [
        MessageResponse(
            id=str(m.id),
            role=m.role,
            content=m.content,
            sources=m.sources,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user),
):
    """Delete a conversation and all its messages."""
    conversation = await Conversation.get(conversation_id)
    if conversation is None or conversation.user_id != str(user.id):
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Conversation")

    # Delete all messages
    await Message.find(Message.conversation_id == conversation_id).delete()
    # Delete conversation
    await conversation.delete()

    return {"message": "Conversation deleted"}
