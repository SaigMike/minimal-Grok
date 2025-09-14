# Back‑end (FastAPI) — Revised

FastAPI service that accepts chat messages and **streams tokens over SSE**. It is a thin proxy around the xAI Grok API (currently a demo stream), with clean separation of config, routes, and services.

## Run locally

```bash
cd backend
cp .env.example .env     # set GROK_API_KEY, GROK_MODEL, ALLOWED_ORIGINS, etc.

# Prefer a virtualenv; on NFS add --copies to avoid symlinks
python3 -m venv .venv --copies
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Run
python -m uvicorn app.main:app --reload --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"
```

### Docker / Compose

`docker-compose.yml` runs FastAPI in a container binding to `0.0.0.0` **inside** and publishes **only** on your host IP (e.g., `192.168.1.187`) via `host_ip` mapping.

```yaml
services:
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

## API

### `POST /api/chat`

- **Body**: `{ "messages": [{ "role": "user" | "assistant" | "system", "content": "..." }], "sessionId": "optional" }`
- **Response**: `text/event-stream` of `data: <token>` lines; terminated by `data: [DONE]`.

Example:
```bash
curl -N -X POST http://localhost:8000/api/chat   -H 'Content-Type: application/json'   -H 'Accept: text/event-stream'   -d '{"messages":[{"role":"user","content":"Say hi"}]}'
```

### CORS

Set `ALLOWED_ORIGINS` in `.env` to your frontend origin (e.g., `http://192.168.1.187:5173`).

## Configuration (env)

| Variable          | Purpose                                                            |
|------------------|--------------------------------------------------------------------|
| `GROK_API_KEY`   | xAI Grok API key (read from env only)                              |
| `GROK_MODEL`     | Model name (e.g., `grok-2-latest`, `grok-3-mini-latest`)           |
| `HOST` / `PORT`  | Bind address and port (default `0.0.0.0:8000`)                     |
| `ALLOWED_ORIGINS`| Comma‑separated CORS origins                                       |
| `LOG_LEVEL`      | Uvicorn/logging level                                              |
| `SYSTEM_PROMPT`  | Optional system message injected server‑side                       |

> **Note:** The project uses **pydantic‑settings** (`BaseSettings`) on Pydantic v2.

## Grok client

`app/services/grok_client.py` currently yields a **demo** stream to prove end‑to‑end SSE. To integrate the real Grok API, post to the Grok chat/completions endpoint with `stream=true`, map fields (model, messages, etc.), and **yield** each token as `data: <token>\n\n`. End with `data: [DONE]\n\n`.

## Tests

```bash
./scripts/test.sh
```

## Troubleshooting

- **No tokens in UI**: test the endpoint directly (`curl -N ...`) to confirm streaming. If curl works, check the frontend SSE parser and `VITE_API_BASE`.
- **PEP 668**: use a venv; add `--copies` on network filesystems.
