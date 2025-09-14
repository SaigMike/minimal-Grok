"""
Chat endpoint for the Grok chatbot.

This module defines a single POST endpoint, ``/api/chat``, which accepts a
conversation history and streams back the assistant's reply as Server‑Sent
Events (SSE).  The endpoint delegates to the ``GrokClient`` service to
interface with the underlying model.  Responses are emitted one token at a
time to provide a responsive user experience.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

from ..schemas import ChatRequest
from ..services.grok_client import GrokClient
from ..config import get_settings, Settings


router = APIRouter()


@router.post("/chat", summary="Stream chat completions", response_description="Server‑sent events stream")
async def chat_endpoint(request: ChatRequest, settings: Settings = Depends(get_settings)) -> StreamingResponse:
    """
    Accept a list of chat messages and stream the assistant's reply.

    The request body must contain a ``messages`` array following the xAI Grok
    format (`{role: string, content: string}`).  The optional ``sessionId``
    allows callers to correlate multiple conversations on the client side.  The
    response is streamed as a sequence of SSE events with one token per event.
    Once the model has finished generating its reply, a final event with
    ``[DONE]`` is sent.
    """
    # Ensure an API key is configured.  If none is provided, return a 500 to
    # surface misconfiguration quickly during development.
    if not settings.grok_api_key:
        raise HTTPException(status_code=500, detail="GROK_API_KEY is not configured")

    client = GrokClient(api_key=settings.grok_api_key, model=settings.grok_model)

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            async for token in client.stream_chat_completions(request.messages, system_prompt=settings.system_prompt):
                # SSE format: each line begins with 'data: ' and ends with a blank line
                yield f"data: {token}\n\n"
            # Signal completion
            yield "data: [DONE]\n\n"
        except Exception as exc:
            # Emit an error event and re‑raise to trigger a proper HTTP error response
            yield f"data: [ERROR] {str(exc)}\n\n"
            raise

    return StreamingResponse(event_generator(), media_type="text/event-stream")
