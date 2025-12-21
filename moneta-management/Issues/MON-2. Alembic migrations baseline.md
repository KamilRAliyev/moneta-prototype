**As a developer**,
I want database migrations wired in,
So that schema evolution is controlled from day one.

**Acceptance criteria**
- Alembic initialized
- alembic revision --autogenerate works
- alembic upgrade head runs inside container
- Empty baseline migration exists