# Backend Package Structure

## Overview
The backend is a FastAPI application using Poetry for dependency management, SQLAlchemy for database operations, and Pydantic Settings for configuration management.

## Directory Structure

```
backend/
├── pyproject.toml          # Poetry project configuration and dependencies
├── poetry.lock              # Poetry lock file (dependency versions)
├── alembic.ini             # Alembic migration configuration
├── migrations/             # Alembic migration files
│   ├── versions/           # Migration version files
│   ├── env.py             # Alembic environment configuration
│   └── script.py.mako     # Migration template
├── server/                 # Main application package
│   ├── __init__.py         # Package initialization
│   ├── models/            # SQLAlchemy database models
│   │   ├── __init__.py    # Base class for all models
│   │   └── example.py     # Example model (can be deleted)
│   ├── core/              # Core application components
│   │   ├── __init__.py    # Package initialization
│   │   ├── database.py    # Database connection utilities
│   │   └── settings/      # Configuration and settings module
│   │       ├── __init__.py # Package initialization
│   │       ├── database.py # Database configuration settings
│   │       └── app.py     # Application configuration settings
│   ├── api/               # API routes
│   │   └── routers/       # API route handlers
│   │       ├── __init__.py # Router exports
│   │       └── system.py  # System information endpoints
│   │       ├── __init__.py # Router exports
│   │       └── system.py  # System information endpoints
│   ├── services/          # Business logic services
│   │   ├── __init__.py    # Service exports
│   │   ├── health.py      # Health check service
│   │   └── data_dir.py    # Data directory management service
│   └── main.py            # FastAPI application entry point
└── tests/                  # Test suite directory
    └── __init__.py         # Package initialization
```

## Package Details

### Root Level

#### `pyproject.toml`
- **Purpose**: Poetry project configuration
- **Key Dependencies**:
  - `fastapi` (>=0.124.4,<0.125.0) - Web framework
  - `sqlalchemy` (>=2.0.45,<3.0.0) - ORM and database toolkit
  - `pydantic-settings` (>=2.0.0,<3.0.0) - Settings management
  - `dateinfer` (>=0.2.0,<0.3.0) - Date inference utility
- **Python Version**: >=3.8

#### `poetry.lock`
- Locked dependency versions for reproducible builds

### `server/` Package

Main application package containing the FastAPI application code.

#### `server/__init__.py`
- Package initialization file (currently empty)

#### `server/main.py`
- FastAPI application entry point
- Application initialization and route registration
- Lifespan event handler for startup/shutdown (data directory initialization)

### `server/models/` Module

SQLAlchemy database models module.

#### `server/models/__init__.py`
- **Purpose**: Base class for all database models
- **Class**: `Base` (extends `DeclarativeBase`)
- All models should inherit from this base class

#### `server/models/example.py`
- Example model demonstrating the structure (can be deleted)

### `server/core/` Module

Core application components including database and settings.

#### `server/core/database.py`
- **Purpose**: Database connection and session management
- **Components**:
  - `engine`: SQLAlchemy engine instance with connection pooling
  - `SessionLocal`: SQLAlchemy session factory
  - `get_db()`: FastAPI dependency for database sessions (auto-closes)
  - `get_db_session()`: Context manager for manual session handling
  - `init_db()`: Initialize database tables (optional, Alembic preferred)

### `server/core/settings/` Module

Configuration and settings management module.

#### `server/core/settings/database.py`
- **Purpose**: Database configuration settings
- **Class**: `DatabaseSettings`
- **Environment Variables**:
  - `DB_HOST` (default: localhost)
  - `DB_PORT` (default: 5432)
  - `DB_USER` (default: postgres)
  - `DB_PASSWORD` (default: empty)
  - `DB_NAME` (default: moneta)
  - `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_PRE_PING`, `DB_ECHO`
- **Properties**:
  - `database_url`: Async PostgreSQL URL for SQLAlchemy
  - `database_url_sync`: Sync PostgreSQL URL for Alembic

#### `server/core/settings/app.py`
- **Purpose**: Application configuration settings
- **Class**: `AppSettings`
- **Environment Variables**:
  - `APP_VERSION` (default: 0.1.0) - Application version
  - `ENVIRONMENT` (default: development) - Environment name (dev, staging, prod)
  - `DATA_DIR` (default: /data) - Path to persistent data directory

### `server/api/routers/` Module

API route handlers organized by feature.

#### `server/api/routers/system.py`
- **Purpose**: System information endpoints
- **Endpoints**:
  - `GET /api/system/info` - System information (version, environment, database status)
  - `GET /api/system/data-dir/test` - Test data directory read/write

### `server/services/` Module

Business logic and utility services.

#### `server/services/health.py`
- **Purpose**: Health check service
- **Functions**:
  - `get_health_info()` - Returns health information

#### `server/services/data_dir.py`
- **Purpose**: Data directory management service
- **Functions**:
  - `ensure_data_dir()` - Creates and verifies data directory is writable
  - `test_data_dir_write()` - Tests read/write capabilities

### `migrations/` Directory

Alembic migration files and configuration.

#### `alembic.ini`
- Alembic configuration file
- Points to `migrations/` as script location

#### `migrations/env.py`
- Alembic environment configuration
- Imports database settings and models
- Configures database URL dynamically from settings

#### `migrations/versions/`
- Directory containing migration version files
- Generated by `alembic revision` commands

### `tests/` Directory

Test suite directory for unit and integration tests.

#### `tests/__init__.py`
- Package initialization file (currently empty)

#### Test Files
- `conftest.py` - Pytest fixtures and test database setup
- `test_health.py` - Health endpoint tests
- `test_database_settings.py` - Database settings tests
- `test_database_connection.py` - Database connection tests
- `test_models.py` - Model tests
- `test_alembic.py` - Alembic configuration tests
- `test_system.py` - System endpoints tests

For detailed testing documentation, see [Testing.md](./Testing.md).

## Technology Stack

- **Web Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0+
- **Database Migrations**: Alembic
- **Dependency Management**: Poetry
- **Database**: PostgreSQL (via psycopg)

## Environment Variables

### Database Configuration
- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `DB_USER`: Database user (default: postgres)
- `DB_PASSWORD`: Database password (default: empty)
- `DB_NAME`: Database name (default: moneta)
- `DB_POOL_SIZE`: Connection pool size (default: 5)
- `DB_MAX_OVERFLOW`: Max overflow connections (default: 10)
- `DB_POOL_PRE_PING`: Enable connection health checks (default: true)
- `DB_ECHO`: Echo SQL queries (default: false)

### Application Configuration
- `APP_VERSION`: Application version (default: 0.1.0)
- `ENVIRONMENT`: Environment name (default: development)
- `DATA_DIR`: Path to persistent data directory (default: /data)

For complete environment variable documentation, see [Environment Variables.md](../Environment%20Variables.md).

## Initial State

This is the current structure of the backend package. The following components are in place:

- ✅ Project configuration (Poetry)
- ✅ Database configuration and connection management
- ✅ Application settings (version, environment, data directory)
- ✅ Alembic migrations setup
- ✅ Models structure with base class
- ✅ Database session utilities for FastAPI
- ✅ API routers (health, system)
- ✅ Services (health, data directory management)
- ✅ Test directory structure

## Database Migrations

Migrations are managed using Alembic:

- **Create migration**: `poetry run alembic revision --autogenerate -m "message"`
- **Apply migrations**: `poetry run alembic upgrade head`
- **Rollback**: `poetry run alembic downgrade -1`

Models should be imported in `migrations/env.py` for autogenerate to work.

## Future Expansion Areas

The following areas are ready for expansion:

- API routes and endpoints
- Additional database models
- Business logic/services layer
- Authentication and authorization
- API documentation configuration
- Middleware setup
- Error handling and logging configuration
- Test implementations
