# Backend Testing

This document describes the test suite for the backend application.

## Test Files

- `test_account_model.py` - Account model tests (enums, timestamps, queries)
- `test_accounts.py` - Accounts API endpoint tests (CRUD operations, validation, error handling)
- `test_health.py` - Health check endpoint tests
- `test_database_settings.py` - Database configuration settings tests
- `test_database_connection.py` - Database connection and session management tests
- `test_models.py` - Generic database models tests
- `test_alembic.py` - Alembic migrations configuration tests
- `test_system.py` - System information endpoints tests
- `test_uploads.py` - File upload endpoint tests
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
✅ System information endpoints
✅ Data directory management
✅ Account model (creation, enums, timestamps, queries)
✅ Accounts API endpoints (CRUD operations, pagination, validation)
✅ Account service layer (business logic, error handling)
✅ Meta options endpoint
✅ Error handling and exception mapping

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures (test database setup)
├── test_account_model.py    # Account model tests
├── test_accounts.py         # Accounts API endpoint tests
├── test_health.py           # Health endpoint tests
├── test_database_settings.py # Database settings tests
├── test_database_connection.py # Database connection tests
├── test_models.py           # Generic model tests
├── test_alembic.py          # Alembic configuration tests
├── test_system.py           # System endpoints tests
└── test_uploads.py          # Upload endpoint tests
```

## Account Model Tests

`test_account_model.py` covers:
- Model creation with required and optional fields
- Automatic timestamp handling (created_at, updated_at)
- Enum validations (AccountType, EconomicArea, Currency)
- Currency enum helper methods (name_full, exponent)
- Database queries and filtering

## Accounts API Tests

`test_accounts.py` covers:
- List accounts (empty, with data, pagination)
- Get account by ID (success and not found)
- Create account (success, minimal fields, invalid data)
- Update account (full and partial updates)
- Delete account (success and not found)
- Meta options endpoint
- Error handling and validation
- Database session patching for test isolation
