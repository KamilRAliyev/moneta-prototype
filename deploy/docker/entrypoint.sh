#!/usr/bin/env sh
set -e

cd /app/backend

# Ensure data directory exists and has correct permissions
DATA_DIR="${DATA_DIR:-/data}"
if [ ! -d "$DATA_DIR" ]; then
  mkdir -p "$DATA_DIR"
fi

# Fix ownership and permissions (run as root in container)
# This ensures the volume is writable
if [ -w "$DATA_DIR" ] 2>/dev/null; then
  # Directory is writable, ensure permissions are correct
  chmod 777 "$DATA_DIR" 2>/dev/null || true
else
  # Directory is not writable, try to fix
  chown -R root:root "$DATA_DIR" 2>/dev/null || true
  chmod 777 "$DATA_DIR" 2>/dev/null || chmod 755 "$DATA_DIR" 2>/dev/null || true
  # If still not writable, create a subdirectory that we can write to
  if [ ! -w "$DATA_DIR" ] 2>/dev/null; then
    echo "Warning: Cannot make $DATA_DIR writable. Volume may be read-only." >&2
  fi
fi

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
