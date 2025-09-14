import { Message } from '../types';

/**
 * Base URL for the API, configured via environment variable at build time.
 * When running locally the default value is `http://localhost:8000`.
 */
const API_BASE = import.meta.env.VITE_API_BASE || '';

/**
 * Post a conversation to the back‑end and return the streaming response body.
 *
 * @param messages Array of chat messages in Grok format
 * @param sessionId Optional session identifier
 */
export async function postChat(
  messages: Omit<Message, 'timestamp'>[],
  sessionId?: string
): Promise<ReadableStream<Uint8Array>> {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify({ messages, sessionId }),
  });
  if (!response.ok || !response.body) {
    throw new Error(`Chat API error: ${response.status}`);
  }
  return response.body;
}