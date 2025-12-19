#!/usr/bin/env bash

# Simple dev helper to run FlowMason Studio backend and frontend
# from source with hot reload.
#
# Usage:
#   ./scripts/dev.sh
#   BACKEND_PORT=8999 FRONTEND_PORT=5173 ./scripts/dev.sh
#
# Assumes:
#   - You have an active Python env with `flowmason` installed (e.g. `pip install -e .[all]`)
#   - Node.js + npm are available for the frontend

set -euo pipefail

BACKEND_PORT="${BACKEND_PORT:-8999}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "FlowMason dev runner"
echo "  Backend port : $BACKEND_PORT"
echo "  Frontend port: $FRONTEND_PORT"
echo

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  echo
  echo "Shutting down dev services..."
  if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    echo "  Stopping frontend (PID $FRONTEND_PID)..."
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi

  if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo "  Stopping backend (PID $BACKEND_PID)..."
    kill "$BACKEND_PID" 2>/dev/null || true
  fi

  wait || true
}

trap cleanup EXIT INT TERM

echo "Starting Studio backend (uvicorn via CLI)..."

# Ensure no existing background studio is running
if command -v flowmason >/dev/null 2>&1; then
  flowmason studio stop >/dev/null 2>&1 || true
fi

if ! command -v flowmason >/dev/null 2>&1; then
  echo "Error: 'flowmason' CLI not found on PATH."
  echo "Make sure you've installed the project, e.g.:"
  echo "  pip install -e \".[all]\""
  exit 1
fi

# Start backend with reload in foreground (we background the process here)
flowmason studio start --host 127.0.0.1 --port "$BACKEND_PORT" --reload &
BACKEND_PID=$!

sleep 2

echo "Starting Studio frontend (Vite dev server)..."
cd "$ROOT_DIR/studio/frontend"

if [[ ! -d node_modules ]]; then
  echo "Installing frontend dependencies (npm install)..."
  npm install
fi

npm run dev -- --port "$FRONTEND_PORT" &
FRONTEND_PID=$!

echo
echo "Dev environment started:"
echo "  Backend : http://127.0.0.1:${BACKEND_PORT}"
echo "  Frontend: http://127.0.0.1:${FRONTEND_PORT}"
echo
echo "Press Ctrl+C to stop both."

wait

