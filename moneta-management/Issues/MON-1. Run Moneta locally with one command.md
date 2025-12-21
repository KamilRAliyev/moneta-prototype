**As a developer,**
I want to start Moneta (API + frontend + Postgres) with a single command,
So that I can verify the system boots correctly.

**Acceptance criteria**

- docker compose up starts:
    - FastAPI on :8000
    - PostgreSQL
- GET /healthz returns { ok: true }
- Container does **not crash** on startup