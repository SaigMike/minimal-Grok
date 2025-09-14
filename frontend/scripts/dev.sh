#!/usr/bin/env bash
# Front-end development script (revised)
# - Installs deps reproducibly (npm ci when lockfile present)
# - Uses Vite dev server and binds to HOST/PORT (defaults 0.0.0.0:5173)
# - Honors VITE_API_BASE from environment or .env (baked only in prod builds)
# - Passes through extra args to Vite (e.g., --open)
#
# Usage:
#   bash scripts/dev.sh
#   HOST=0.0.0.0 PORT=5173 bash scripts/dev.sh --open
set -Eeuo pipefail

if command -v npm >/dev/null 2>&1; then
  : # ok
else
  echo "[dev] npm not found in PATH" >&2
  exit 1
fi

echo "[dev] Installing dependencies…"
if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi

if [ -n "${VITE_API_BASE:-}" ]; then
  echo "[dev] VITE_API_BASE=${VITE_API_BASE} (dev server will proxy requests to this base)"
else
  if [ -f ".env" ]; then
    echo "[dev] Using Vite .env/.env.local for VITE_API_BASE (if defined)"
  else
    echo "[dev] NOTE: VITE_API_BASE is not set; ensure your frontend/.env defines it for local dev."
  fi
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-5173}"
echo "[dev] Starting Vite on ${HOST}:${PORT}…"

exec npm run dev -- --host "${HOST}" --port "${PORT}" "$@"
