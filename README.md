# Grok Chatbot Starter — Revised

This starter is a **minimal, production‑ready** chatbot powered by the xAI Grok API with:

- **Backend**: FastAPI proxy that **streams** tokens via **Server‑Sent Events (SSE)**
- **Frontend**: React + TypeScript (Vite) chat UI
- Ready for **local dev** (VS Code bash) and **Ubuntu** deployment
- **Docker Compose** with **Nginx** serving the static frontend
- All secrets/config via **environment variables** (`.env`, build args) — no hardcoded tokens

> You can run bare‑metal (venv + Vite dev) or via Docker. In Docker we bind services **inside containers to `0.0.0.0`** and publish them on your **LAN IP** (e.g., `192.168.1.187`) with Compose `host_ip`.

---

## Repository structure

```
grok-chatbot/
├── backend/                  # FastAPI service (SSE proxy to Grok)
│   ├── app/
│   │   ├── main.py           # Creates FastAPI app, CORS, routes
│   │   ├── config.py         # pydantic-settings configuration from env
│   │   ├── schemas.py        # Request models ({ messages: [{role, content}], ... })
│   │   ├── routes/chat.py    # POST /api/chat (SSE stream back to client)
│   │   └── services/grok_client.py # Grok client wrapper (currently demo stream; see below)
│   ├── requirements.txt
│   ├── .env.example
│   ├── README.md
│   └── scripts/
│       ├── dev.sh            # venv + uvicorn reload
│       └── test.sh           # pytest + coverage
├── frontend/                 # React + TS UI (Vite)
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── types.ts
│   │   ├── lib/api.ts        # fetch + ReadableStream SSE reader
│   │   └── components/Chat.tsx  # streaming UI (safe UUID fallback)
│   ├── package.json
│   ├── vite.config.ts
│   ├── .env.example
│   ├── README.md
│   └── scripts/
│       ├── dev.sh
│       └── build.sh
├── docker-compose.yml        # Backend + Nginx frontend; host_ip pinning
└── README.md                 # This file
```

---

## Quickstart — Docker (recommended)

1) **Backend env** (`backend/.env`):
```ini
# Required
GROK_API_KEY=YOUR_KEY
# Optional
GROK_MODEL=grok-2-latest
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=http://192.168.1.187:5173
```

2) **Build the frontend with the API base at build‑time** (Compose passes this as a build arg):
```yaml
# docker-compose.yml (excerpt)
services:
  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_BASE: "http://192.168.1.187:8000"
    ports:
      - target: 80
        published: 5173
        protocol: tcp
        host_ip: 192.168.1.187
  backend:
    build:
      context: ./backend
    env_file:
      - ./backend/.env
    command: ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
    ports:
      - target: 8000
        published: 8000
        protocol: tcp
        host_ip: 192.168.1.187
```

3) **Up the stack**:
```bash
docker compose build --no-cache
docker compose up -d
# Frontend: http://192.168.1.187:5173
# Backend:  http://192.168.1.187:8000/docs
```

> The frontend shows a blank page when the JS crashes. If that happens, open **DevTools → Console**. We’ve added a robust SSE parser and a **safe UUID fallback** (avoids `crypto.randomUUID` errors).

---

## Quickstart — local dev (bare‑metal)

**Backend** (Ubuntu/Linux/macOS):
```bash
cd backend
cp .env.example .env   # set GROK_API_KEY etc.
# If your source dir is on NFS, avoid symlink issues:
python3 -m venv .venv --copies
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"
```

**Frontend**:
```bash
cd frontend
cp .env.example .env   # VITE_API_BASE=http://localhost:8000 (or another host)
npm install
npm run dev            # http://localhost:5173
```

> Vite injects `VITE_*` values **at build time**. When changing `VITE_API_BASE`, **rebuild** the production image (`docker compose build frontend`) or restart `npm run dev` locally.

---

## API and streaming contract

- `POST /api/chat` accepts:
  ```json
  { "messages": [{ "role": "user", "content": "..." }], "sessionId": "optional" }
  ```
- Response is `text/event-stream` where each event is a line prefixed with `data:`; stream ends with `data: [DONE]`.
- The frontend reads tokens from a `ReadableStream` and updates the UI progressively.

**Note about Grok integration**  
`services/grok_client.py` currently emits a **demo stream**. Replace the placeholder with a real HTTP call to the Grok API and yield streamed tokens as they arrive (keeping the `data:` and `[DONE]` contract). Keep your API key in env (`GROK_API_KEY`).

---

## Troubleshooting

- **Blank frontend page** → open Console. Common causes:
  - missing `VITE_API_BASE` in a production build (fix by passing Compose build arg)
  - older browsers/policies blocking `crypto.randomUUID` (fixed with safe fallback)
- **CORS** → set `ALLOWED_ORIGINS` to the exact frontend origin (e.g., `http://192.168.1.187:5173`)
- **Ubuntu PEP 668** (“externally‑managed‑environment”) → always use a **virtualenv**; on NFS use `--copies`.
- **Binding IP** → in containers use `0.0.0.0` internally; publish on the host IP with Compose `host_ip`.

---

## License & notes

This starter is meant to be adapted to your project. Add linting (ruff/black for Python; ESLint/Prettier for JS) and CI as needed. Contributions welcome.
