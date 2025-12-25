# Backend Testing

This document describes the test suite for the backend application.

## Test Files

- `test_health.py` - Health check endpoint tests
- `test_database_settings.py` - Database configuration settings tests
- `test_database_connection.py` - Database connection and session management tests
- `test_models.py` - Database models tests
- `test_alembic.py` - Alembic migrations configuration tests
- `conftest.py` - Pytest fixtures and configuration

## Running Tests

### Run all tests:
```bash
poetry run pytest
```

### Run specific test file:
```bash
poetry run pytest tests/test_database_settings.py
```

### Run with verbose output:
```bash
poetry run pytest -v
```

### Run with coverage:
```bash
poetry run pytest --cov=server --cov-report=html
```

## Test Database

Tests use an in-memory SQLite database (configured in `conftest.py`) to avoid requiring a running PostgreSQL instance. This makes tests fast and isolated.

## Fixtures

- `test_db` - Provides a test database session factory (SQLite in-memory)
- `db_session` - Provides a database session for individual tests

## Test Coverage

The test suite covers:

✅ Database settings configuration
✅ Environment variable handling
✅ Database URL generation
✅ Database session management
✅ Model inheritance and metadata
✅ Alembic configuration
✅ Migration folder structure

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── test_health.py           # Health endpoint tests
├── test_database_settings.py # Database settings tests
├── test_database_connection.py # Database connection tests
├── test_models.py           # Model tests
└── test_alembic.py          # Alembic configuration tests
```
