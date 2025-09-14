#!/usr/bin/env bash
# Back-end test script (revised)
# - Uses local venv
# - Installs deps
# - Loads .env.test if present (else .env) for any required config
# - Runs pytest with coverage (pass-through extra args)
#
# Usage:
#   bash scripts/test.sh
#   bash scripts/test.sh -k test_chat  # run subset
set -Eeuo pipefail

# 1) Ensure venv
if [ ! -d ".venv" ]; then
  echo "[test] Creating virtualenv (.venv)…"
  python3 -m venv .venv --copies 2>/dev/null || python3 -m venv .venv
fi

# 2) Activate venv
#   shellcheck disable=SC1091
source .venv/bin/activate

# 3) Install deps
echo "[test] Installing Python dependencies…"
python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt >/dev/null

# 4) Load env for tests (prefer .env.test)
if [ -f ".env.test" ]; then
  echo "[test] Loading environment from .env.test"
  set -a; . ./.env.test; set +a
elif [ -f ".env" ]; then
  echo "[test] Loading environment from .env"
  set -a; . ./.env; set +a
fi

# 5) Run tests with coverage; pass through additional args
echo "[test] Running pytest…"
exec python -m pytest --cov=app --cov-report=term-missing "$@"
