"""
Pydantic data models for the chat API.

These classes define the shape of incoming requests and responses.  The
``ChatRequest`` model accepts a list of ``Message`` objects and an optional
session identifier.  The response is streamed as Server‑Sent Events and does
not have a static schema.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a single chat message from the user or assistant."""

    role: str = Field(..., description="Role of the message author (e.g. user, assistant, system)")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""

    messages: List[Message] = Field(..., description="Array of messages forming the conversation")
    sessionId: Optional[str] = Field(None, description="Optional identifier for the chat session")
