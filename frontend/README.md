# Front‑end (React + TypeScript) — Revised

Vite‑powered React UI for the Grok chatbot. It renders a simple chat interface and consumes the backend’s **SSE** stream using `fetch` + `ReadableStream`. It includes a **safe UUID** fallback for session IDs and a **robust SSE parser**.

## Local dev

```bash
cd frontend
cp .env.example .env              # set VITE_API_BASE=http://localhost:8000 (or another host)
npm install
npm run dev                       # http://localhost:5173
```

## Docker / Nginx production build

The production image builds the app and serves static files via **Nginx**. Because Vite bakes env at build time, we pass the API base as a **build arg**.

```yaml
services:
  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_BASE: "http://192.168.1.187:8000"
    # Optional: custom SPA nginx.conf with fallback and caching
    # volumes:
    #   - ./frontend/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    ports:
      - target: 80
        published: 5173
        protocol: tcp
        host_ip: 192.168.1.187
```

> If you change the API base, **rebuild** the image: `docker compose build --no-cache frontend`.

## Environment

| Variable         | Purpose                                        |
|-----------------|------------------------------------------------|
| `VITE_API_BASE` | Base URL for the backend (no trailing slash).  |

Values prefixed with `VITE_` are **compiled into the bundle**. Don’t put secrets here.

## How streaming works

- The UI posts `{ messages, sessionId }` to `/api/chat` at `VITE_API_BASE`.
- It reads the SSE response via `ReadableStream`, splitting on **double newlines** (`\n\n`), extracting the last `data:` line per event, and appending tokens until `[DONE]`.
- Visual UX: user/assistant bubbles, timestamps, typing indicator, errors inline.

## Troubleshooting

- **Blank page**: open DevTools → Console. Common causes:
  - blocked `crypto.randomUUID` (we now use a safe fallback)
  - wrong `VITE_API_BASE` baked into the prod build (rebuild with correct arg)
- **No tokens**: check the Network tab → `POST /api/chat` → Response should show streaming `data:` lines.

