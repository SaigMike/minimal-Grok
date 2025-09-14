"""
Service wrapper for the xAI Grok API.

The ``GrokClient`` class encapsulates the logic required to interact with the
Grok API and stream chat completions back to callers.  It reads the API key
and model name from the environment through ``Settings`` and exposes an
``async stream_chat_completions`` method that yields one token at a time.

**Important:** This implementation currently contains a placeholder response.
Replace the ``stream_chat_completions`` method with actual HTTP requests to
``https://api.grok.x.ai`` once the API format is finalized.  Be sure not to
hardcode the API key; read it from the environment or configuration.
"""

from typing import AsyncGenerator, Iterable, List, Optional
import asyncio
import logging
import httpx

from ..schemas import Message

logger = logging.getLogger(__name__)


class GrokClient:
    """Client for streaming chat completions from the xAI Grok API."""

    def __init__(self, api_key: str, model: str = "grok-2-latest", timeout: float = 60.0) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        # Base endpoint; actual path may differ depending on Grok's API design
        self.base_url = "https://api.grok.x.ai/v1/chat/completions"

    async def stream_chat_completions(
        self,
        messages: Iterable[Message],
        *,
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completions for a given list of messages.

        :param messages: Conversation history, following the Grok API format.
        :param system_prompt: Optional system prompt to prepend to the conversation.
        :yield: Individual tokens as strings.

        **Placeholder implementation:** This method currently yields a fixed
        response token by token.  To integrate with the real Grok API, issue an
        HTTP POST request with ``stream=true`` and asynchronously yield the
        returned tokens.  Handle timeouts, retries and backoff as appropriate.
        """

        # TODO: replace this placeholder with an actual API call when Grok is available.
        dummy_response = "Hello from Grok"
        for token in dummy_response.split():
            # Simulate latency for a more realistic streaming experience
            await asyncio.sleep(0.1)
            yield token

        # In a real implementation, you would do something along these lines:
        #
        # async with httpx.AsyncClient(timeout=self.timeout) as client:
        #     headers = {"Authorization": f"Bearer {self.api_key}"}
        #     payload = {
        #         "model": self.model,
        #         "messages": [m.dict() for m in messages],
        #         "stream": True,
        #     }
        #     if system_prompt:
        #         payload["system_prompt"] = system_prompt
        #     response = await client.post(self.base_url, json=payload, headers=headers)
        #     response.raise_for_status()
        #     async for line in response.aiter_lines():
        #         if line.strip() == "":
        #             continue
        #         # Parse the SSE format; extract the token and yield it
        #         if line.startswith("data:"):
        #             data = line[len("data:"):].strip()
        #             if data == "[DONE]":
        #                 break
        #             yield data
