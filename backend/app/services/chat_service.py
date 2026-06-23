"""Chat service - orchestrates the RAG pipeline for chat interactions."""

import uuid
from datetime import datetime
from typing import Optional

from app.config import Settings
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.rag.graph import RAGGraph


class ChatService:
    """Service for handling chat interactions through the RAG pipeline."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.rag_graph = RAGGraph(settings)

    async def process_message(
        self,
        user: User,
        message: str,
        conversation_id: Optional[str] = None,
        request_id: Optional[str] = None,
        document_ids: Optional[list[str]] = None,
    ) -> dict:
        """Process a user message through the RAG pipeline."""
        request_id = request_id or str(uuid.uuid4())

        # Get or create conversation
        conversation = None
        if conversation_id:
            conversation = await Conversation.get(conversation_id)
            if conversation is None or conversation.user_id != str(user.id):
                conversation = None

        if conversation is None:
            conversation = Conversation(
                user_id=str(user.id),
                title=message[:100],
                message_count=0,
            )
            await conversation.insert()

        # Save user message
        user_message = Message(
            conversation_id=str(conversation.id),
            role="user",
            content=message,
        )
        await user_message.insert()

        # Load conversation history (last 10 messages)
        history = await Message.find(
            Message.conversation_id == str(conversation.id)
        ).sort("-created_at").limit(10).to_list()
        history = list(reversed(history))
        history_dicts = [
            {"role": m.role, "content": m.content}
            for m in history
            if m.role != "user" or m.content != message  # exclude current
        ]

        # Run RAG pipeline
        result = await self.rag_graph.run(
            user_query=message,
            user_role=user.role.value,
            user_departments=user.departments,
            conversation_history=history_dicts,
            request_id=request_id,
            document_ids=document_ids,
        )

        # Save assistant message
        assistant_message = Message(
            conversation_id=str(conversation.id),
            role="assistant",
            content=result["response"],
            sources=result.get("sources", []),
            token_count=result.get("total_tokens", 0),
            latency_ms=result.get("latency_ms", 0),
            guardrail_flags=result.get("guardrail_flags", []),
        )
        await assistant_message.insert()

        # Update conversation
        conversation.message_count += 2
        conversation.updated_at = datetime.utcnow()
        await conversation.save()

        return {
            "response": result["response"],
            "conversation_id": str(conversation.id),
            "sources": result.get("sources") or [],
            "blocked": result.get("blocked", False),
            "block_reason": result.get("block_reason"),
            "prompt_tokens": result.get("prompt_tokens", 0),
            "completion_tokens": result.get("completion_tokens", 0),
            "total_tokens": result.get("total_tokens", 0),
            "estimated_cost": result.get("estimated_cost", 0.0),
        }
