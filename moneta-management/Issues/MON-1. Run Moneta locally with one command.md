**As a developer,**
I want to start Moneta (API + frontend + Postgres) with a single command,
So that I can verify the system boots correctly.

**Acceptance criteria**

- docker compose up starts:
    - FastAPI on :8000
    - Vue 3 frontend (Vite dev server) on :5173
    - PostgreSQL
- GET /api/v1/health returns health status
- Container does **not crash** on startup

**Status:** ✅ Complete

**Implementation:**
- Single `app` container runs both backend and frontend
- Both services support hot-reload
- Frontend dependencies preserved in named volume
- All services start with `docker compose -f deploy/compose/docker-compose-dev.yml up`
