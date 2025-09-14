#!/usr/bin/env bash
# Front-end production build & preview (revised)
# - Installs deps reproducibly (npm ci when lockfile present)
# - Builds with Vite (VITE_* env baked at build time)
# - Optionally previews the built site (Nginx is used in Docker; preview is for local checks)
#
# Usage:
#   VITE_API_BASE=http://192.168.1.187:8000 bash scripts/build.sh
#   HOST=0.0.0.0 PORT=5173 bash scripts/build.sh
set -Eeuo pipefail

if command -v npm >/dev/null 2>&1; then
  : # ok
else
  echo "[build] npm not found in PATH" >&2
  exit 1
fi

echo "[build] Installing dependencies…"
if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi

echo "[build] VITE_API_BASE='${VITE_API_BASE:-}'"
if [ -z "${VITE_API_BASE:-}" ]; then
  echo "[build] WARNING: VITE_API_BASE is not set. The build will bake values from .env/.env.production if present."
fi

echo "[build] Building…"
npm run build

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-5173}"
echo "[build] Preview on ${HOST}:${PORT} (Ctrl+C to stop)"
exec npm run preview -- --host "${HOST}" --port "${PORT}" "$@"
