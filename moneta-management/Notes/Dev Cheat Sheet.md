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
- API available at: http://localhost:8000
- Health check: http://localhost:8000/api/health/
- Code changes → instant reload
- Swagger docs: http://localhost:8000/docs

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

4️⃣ Run backend locally (without Docker)
```bash
cd backend
poetry install
poetry run uvicorn server.main:app --reload
```

5️⃣ Run tests
```bash
poetry install
poetry run pytest
```

Inside Docker (one-off)
```bash
docker run --rm \
  -v "$PWD/backend:/app/backend" \
  moneta-backend-dev \
  poetry run pytest
```

6️⃣ Database Migrations (Alembic)

Create a new migration:
```bash
cd backend
poetry run alembic revision --autogenerate -m "Migration message"
```

Apply migrations:
```bash
poetry run alembic upgrade head
```

Rollback one migration:
```bash
poetry run alembic downgrade -1
```

Show current revision:
```bash
poetry run alembic current
```

Inside Docker (one-off):
```bash
docker run --rm \
  -v "$PWD/backend:/app/backend" \
  -v "$PWD/env:/app/env" \
  -e ENV_FILE=/app/env/dev.env \
  moneta-backend-dev \
  poetry run alembic upgrade head
```

7️⃣ Clean up Docker artifacts
```bash
docker image prune
docker container prune
```
⚠️ This removes unused images/containers.

🔒 Environment variables
mounted from: `env/dev.env`
Loaded via: `ENV_FILE=/app/env/dev.env`

Database settings (DB_*):
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- See `server/core/settings/database.py` for all options
