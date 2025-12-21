#!/usr/bin/env sh
set -e

cd /app/backend


ENV_FILE=/app/env/dev.env

if [ -n "${ENV_FILE:-}" ] && [ -f "$ENV_FILE" ]; then
  set -a
  . "$ENV_FILE"
  set +a
fi

exec uvicorn server.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --reload \
  --reload-dir /app/backend/server
