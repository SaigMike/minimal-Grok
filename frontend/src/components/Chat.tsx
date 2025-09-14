import React, { useState, useRef, useEffect } from 'react';
import { Message } from '../types';
import { postChat } from '../lib/api';

/**
 * Chat component implementing a simple conversational UI with streaming
 * responses from the back‑end.  Messages are stored in component state and
 * rendered as chat bubbles.  When the user sends a message, the entire
 * conversation is POSTed to the back‑end.  The assistant's reply is streamed
 * back token by token and appended to the message list.
 */
const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const endRef = useRef<HTMLDivElement | null>(null);

  // On mount, load or generate a session ID for continuity.  This value is
  // persisted in localStorage so the user retains the same session across
  // refreshes.
  useEffect(() => {
    const stored = localStorage.getItem('grok_session_id');
    if (stored) {
      setSessionId(stored);
    } else {
      const id = crypto.randomUUID();
      localStorage.setItem('grok_session_id', id);
      setSessionId(id);
    }
  }, []);

  // Scroll to the bottom whenever messages change
  useEffect(() => {
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Handle sending a new message
  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    // Append the user's message
    const userMsg: Message = {
      role: 'user',
      content: trimmed,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setError(null);
    setLoading(true);
    try {
      // Build payload without timestamps for the API
      const payloadMessages = [...messages, userMsg].map(({ role, content }) => ({ role, content }));
      const stream = await postChat(payloadMessages, sessionId);
      const reader = stream.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      // Prepare the assistant message placeholder
      let assistantMsg: Message = {
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n\n');
        for (let i = 0; i < parts.length - 1; i++) {
          const line = parts[i].trim();
          if (!line.startsWith('data:')) continue;
          const data = line.slice('data:'.length).trim();
          if (!data) continue;
          if (data === '[DONE]') {
            setLoading(false);
            return;
          }
          if (data.startsWith('[ERROR]')) {
            setError(data.replace('[ERROR]', '').trim());
            setLoading(false);
            return;
          }
          // Append token to assistant message
          assistantMsg.content = assistantMsg.content ? `${assistantMsg.content} ${data}` : data;
          setMessages((prev) => {
            const newMsgs = [...prev];
            newMsgs[newMsgs.length - 1] = { ...assistantMsg };
            return newMsgs;
          });
        }
        buffer = parts[parts.length - 1];
      }
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Unknown error');
      setLoading(false);
    }
  };

  // Handle key presses to submit on Enter but allow newlines with Shift+Enter
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '1rem',
          backgroundColor: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: '0.5rem',
        }}
      >
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: '0.5rem',
            }}
          >
            <div
              style={{
                maxWidth: '70%',
                padding: '0.5rem 0.75rem',
                borderRadius: '0.5rem',
                backgroundColor: msg.role === 'user' ? '#e5e7eb' : '#dbeafe',
                color: '#111827',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}
            >
              {msg.content}
              <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem', textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ color: '#6b7280', fontStyle: 'italic' }}>Assistant is typing…</div>
        )}
        {error && (
          <div style={{ color: '#dc2626', marginTop: '0.5rem' }}>Error: {error}</div>
        )}
        <div ref={endRef}></div>
      </div>
      <div style={{ marginTop: '0.5rem', display: 'flex', flexDirection: 'column' }}>
        <textarea
          rows={3}
          placeholder="Type your message…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          aria-label="Message input"
          style={{
            width: '100%',
            padding: '0.5rem',
            borderRadius: '0.5rem',
            border: '1px solid #d1d5db',
            resize: 'none',
          }}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          style={{
            marginTop: '0.5rem',
            padding: '0.5rem 1rem',
            borderRadius: '0.5rem',
            border: 'none',
            backgroundColor: loading || !input.trim() ? '#9ca3af' : '#2563eb',
            color: '#fff',
            cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
            alignSelf: 'flex-end',
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default Chat;