#!/usr/bin/env bash
set -e
# Change to the script directory (project root)
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
# Port fallback
PORT="${PORT:-8000}"
# Start uvicorn using the project dir as app-dir so Python finds app.py
uvicorn app:app --reload --app-dir "$DIR" --host 0.0.0.0 --port "$PORT"
