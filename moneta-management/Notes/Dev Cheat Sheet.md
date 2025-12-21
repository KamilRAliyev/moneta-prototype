# Dev Cheat Sheet

1️⃣ Build backend Docker image (dev)

```bash
docker build \
  -f deploy/docker/Dockerfile \
  -t moneta-backend-dev \
  .
```

What it does?
- Uses Python 3.11 slim as base image
- Installs Poetry Dependencies
- Prepares dev image with Uvicorn + relaod

2️⃣ Start backend container (live reload)

```bash
docker run --rm \
  -p 8000:8000 \
  -v "$PWD/backend:/app/backend" \
  -v "$PWD/env:/app/env" \
  -e ENV_FILE=/app/env/dev.env \
  moneta-backend-dev
```

What it does?
	•	API available at: http://localhost:8000
	•	Health check: http://localhost:8000/api/health/
    •	Code changes → instant reload


3️⃣ Start backend with Docker Compose (preferred)

```bash
docker compose \
  -f deploy/compose/docker-compose-dev.yml \
  up --build
```

To stop:
```bash
docker compose -f deploy/compose/docker-compose-dev.yml down
```
