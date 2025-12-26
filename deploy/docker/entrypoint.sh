#!/usr/bin/env bash
set -e

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

# Load environment variables
ENV_FILE=/app/env/dev.env
if [ -n "${ENV_FILE:-}" ] && [ -f "$ENV_FILE" ]; then
  set -a
  . "$ENV_FILE"
  set +a
fi

# Wait for database to be ready (simple wait - backend will handle connection)
echo "Waiting for database to be ready..."
sleep 3

# Install frontend dependencies if node_modules is missing or empty
# This handles the case where frontend is mounted as a volume
if [ ! -d "/app/frontend/node_modules" ] || [ -z "$(ls -A /app/frontend/node_modules 2>/dev/null)" ]; then
  echo "Installing frontend dependencies..."
  cd /app/frontend
  npm install
fi

# Function to handle shutdown
cleanup() {
  echo "Shutting down..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
  wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
  exit 0
}

trap cleanup SIGTERM SIGINT

# Start backend in background
echo "Starting backend server..."
cd /app/backend
uvicorn server.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --reload \
  --reload-dir /app/backend/server &
BACKEND_PID=$!

# Start frontend in background
echo "Starting frontend dev server..."
cd /app/frontend
npm run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!

# Wait a moment for processes to start
sleep 2

# Check if processes are still running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
  echo "Error: Backend failed to start"
  exit 1
fi

if ! kill -0 $FRONTEND_PID 2>/dev/null; then
  echo "Error: Frontend failed to start"
  exit 1
fi

echo "✓ Backend running on port 8000 (PID: $BACKEND_PID)"
echo "✓ Frontend running on port 5173 (PID: $FRONTEND_PID)"
echo "Both services are running. Press Ctrl+C to stop."

# Wait for both processes (if one dies, we'll catch it)
wait $BACKEND_PID $FRONTEND_PID
