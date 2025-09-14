"""
Tests for the chat endpoint.

These unit tests verify that the `/api/chat` route returns streaming data when
configured correctly and returns an error when the API key is missing.  The
tests use `httpx.AsyncClient` to simulate HTTP requests against the FastAPI
application.  A monkeypatched version of the Grok client yields predictable
tokens so the behaviour can be asserted deterministically.
"""

import pytest
from httpx import AsyncClient

from app.main import app
from app.config import Settings


@pytest.fixture
def anyio_backend() -> str:
    """Configure pytest‑asyncio to use the asyncio backend."""
    return "asyncio"


@pytest.fixture(autouse=True)
def mock_grok_client(monkeypatch):
    """Mock the GrokClient.stream_chat_completions method to yield fixed tokens."""
    from app.services import grok_client as grok_module

    async def fake_stream_chat_completions(self, messages, *, system_prompt=None):
        # Return a few tokens deterministically
        for tok in ["Hello", "world"]:
            yield tok

    monkeypatch.setattr(grok_module.GrokClient, "stream_chat_completions", fake_stream_chat_completions)
    yield


@pytest.mark.anyio
async def test_chat_endpoint_success(monkeypatch):
    """Ensure the chat endpoint streams tokens successfully."""
    # Provide a dummy API key in settings so the endpoint is enabled
    monkeypatch.setenv("GROK_API_KEY", "test-key")
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {"messages": [{"role": "user", "content": "Hi"}]}
        response = await client.post("/api/chat", json=payload)
        assert response.status_code == 200
        # Collect the streamed lines; httpx buffers them but still allows iteration
        lines = []
        async for line in response.aiter_lines():
            if line:
                lines.append(line)
        # We expect data: tokens followed by data: [DONE]
        assert any("data: Hello" in l for l in lines)
        assert any("data: world" in l for l in lines)
        assert any("[DONE]" in l for l in lines)


@pytest.mark.anyio
async def test_chat_endpoint_missing_key(monkeypatch):
    """When GROK_API_KEY is not set, the endpoint should return a 500."""
    # Remove the API key from the environment
    monkeypatch.delenv("GROK_API_KEY", raising=False)
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {"messages": [{"role": "user", "content": "Hi"}]}
        response = await client.post("/api/chat", json=payload)
        assert response.status_code == 500
        assert response.json()["detail"] == "GROK_API_KEY is not configured"
