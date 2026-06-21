"""Generation node - generates response using NVIDIA NIM LLM."""

import time
from app.config import Settings
from app.rag.state import RAGState
from app.rag.prompts import SYSTEM_PROMPT, CONTEXT_PROMPT, REFUSAL_PROMPT


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate cost based on model pricing."""
    PRICING = {
        "meta/llama-3.1-70b-instruct": {"input": 0.00060, "output": 0.00240},
        "meta/llama-3.1-8b-instruct": {"input": 0.00005, "output": 0.00010},
        "meta/llama3-70b-instruct": {"input": 0.00060, "output": 0.00240},
    }
    rates = PRICING.get(model, {"input": 0.001, "output": 0.002})
    return (prompt_tokens / 1000 * rates["input"]) + (completion_tokens / 1000 * rates["output"])


def count_tokens_approx(text: str) -> int:
    """Approximate token count (4 chars per token)."""
    return len(text) // 4


async def generation_node(state: RAGState, settings: Settings) -> dict:
    """Generate response using retrieved context and LLM."""
    documents = state.get("retrieved_documents", [])

    if not documents:
        return {
            "generated_response": REFUSAL_PROMPT.format(
                reason="No relevant documents were found in the knowledge base for your query."
            ),
            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "estimated_cost": 0.0,
        }

    # Build context from retrieved documents
    context_parts = []
    for i, doc in enumerate(documents):
        context_parts.append(
            f"[Document {i + 1}: {doc['filename']} ({doc['department']})]\n{doc['content']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    # Build conversation history
    history = state.get("conversation_history", [])
    history_text = ""
    if history:
        history_lines = []
        for msg in history[-6:]:  # Last 6 messages
            history_lines.append(f"{msg['role'].capitalize()}: {msg['content']}")
        history_text = "\n".join(history_lines)
    else:
        history_text = "No previous conversation."

    # Format prompt
    user_prompt = CONTEXT_PROMPT.format(
        context=context,
        history=history_text,
        question=state["user_query"],
    )

    # Call LLM
    start_time = time.perf_counter()
    try:
        from langchain_nvidia_ai_endpoints import ChatNVIDIA
        from langchain_core.messages import SystemMessage, HumanMessage

        llm = ChatNVIDIA(
            model=settings.nvidia_chat_model,
            api_key=settings.nvidia_api_key,
            base_url=settings.nvidia_base_url,
            temperature=0.1,
            max_tokens=1024,
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        response = await llm.ainvoke(messages)
        generated_text = response.content

        # Token estimation
        prompt_tokens = count_tokens_approx(SYSTEM_PROMPT + user_prompt)
        completion_tokens = count_tokens_approx(generated_text)

        # Try to get actual token usage from response
        if hasattr(response, "response_metadata"):
            usage = response.response_metadata.get("token_usage", {})
            prompt_tokens = usage.get("prompt_tokens", prompt_tokens)
            completion_tokens = usage.get("completion_tokens", completion_tokens)

    except Exception as e:
        generated_text = f"I apologize, but I encountered an error processing your request. Please try again later. (Error: {str(e)[:100]})"
        prompt_tokens = 0
        completion_tokens = 0

    total_tokens = prompt_tokens + completion_tokens
    estimated_cost = estimate_cost(settings.nvidia_chat_model, prompt_tokens, completion_tokens)

    return {
        "generated_response": generated_text,
        "token_usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        },
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost": estimated_cost,
    }
