#!/usr/bin/env bash
# Back-end development script (revised)
# - Creates a local venv (NFS-safe with --copies)
# - Installs deps inside the venv
# - Loads .env (if present)
# - Runs uvicorn with autoreload, binding to HOST/PORT from env or defaults
#
# Usage:
#   bash scripts/dev.sh
#   bash scripts/dev.sh --log-level debug  # extra uvicorn args are passed through
set -Eeuo pipefail

# 1) Ensure a virtualenv exists (use --copies for NFS/remote filesystems)
if [ ! -d ".venv" ]; then
  echo "[dev] Creating virtualenv (.venv)…"
  python3 -m venv .venv --copies 2>/dev/null || python3 -m venv .venv
fi

# 2) Activate venv
#   shellcheck disable=SC1091
source .venv/bin/activate

# 3) Install deps inside the venv
echo "[dev] Installing Python dependencies…"
python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt >/dev/null

# 4) Load environment from .env if present (export all keys while sourcing)
if [ -f ".env" ]; then
  echo "[dev] Loading environment from .env"
  set -a
  #   shellcheck disable=SC1091
  . ./.env
  set +a
fi

# 5) Defaults for host/port; allow overrides via env/.env
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
LOG_LEVEL="${LOG_LEVEL:-info}"

echo "[dev] Starting FastAPI on ${HOST}:${PORT} (log-level=${LOG_LEVEL})…"
# 6) Start uvicorn with reload; pass through any extra args
exec python -m uvicorn app.main:app   --reload   --reload-dir app   --reload-exclude ".venv/*"   --host "${HOST}"   --port "${PORT}"   --log-level "${LOG_LEVEL}"   "$@"
