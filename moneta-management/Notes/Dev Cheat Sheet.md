# Dev Cheat Sheet

1️⃣ Start app with Docker Compose (preferred - runs both backend and frontend)

```bash
cd deploy/compose
docker compose -f docker-compose-dev.yml up --build
```

What it does?
- Starts PostgreSQL database
- Starts pgAdmin (database admin UI)
- Starts app container with:
  - FastAPI backend on port 8000 (hot reload)
  - Vite frontend dev server on port 5173 (HMR)
- All code changes → instant reload for both services

Access:
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Frontend**: http://localhost:5173
- **pgAdmin**: http://localhost:8080
- **PostgreSQL**: localhost:5432

To stop:
```bash
docker compose -f deploy/compose/docker-compose-dev.yml down
```

To stop and remove volumes (⚠️ deletes data):
```bash
docker compose -f deploy/compose/docker-compose-dev.yml down -v
```

2️⃣ Build app Docker image (dev)

```bash
docker build \
  -f deploy/docker/Dockerfile \
  -t moneta-app-dev \
  .
```

What it does?
- Uses Python 3.11 slim as base image
- Installs Node.js 20.x
- Installs Poetry dependencies (backend)
- Installs npm dependencies (frontend)
- Prepares dev image with both Uvicorn and Vite

3️⃣ Run backend locally (without Docker)
```bash
cd backend
poetry install
poetry run uvicorn server.main:app --reload
```

4️⃣ Run frontend locally (without Docker)
```bash
cd frontend
npm install
npm run dev
```

5️⃣ Run backend tests
```bash
cd backend
poetry install
poetry run pytest
```

Inside Docker (one-off):
```bash
docker exec -it illiterate_monkey_app bash
cd /app/backend
poetry run pytest
```

6️⃣ Run frontend tests
```bash
cd frontend
npm install
npm run test:run
```

With UI:
```bash
npm run test:ui
```

With coverage:
```bash
npm run test:coverage
```

Inside Docker (one-off):
```bash
docker exec -it illiterate_monkey_app bash
cd /app/frontend
npm run test:run
```

7️⃣ Database Migrations (Alembic)

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
docker exec -it illiterate_monkey_app bash
cd /app/backend
poetry run alembic upgrade head
```

8️⃣ Clean up Docker artifacts
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
