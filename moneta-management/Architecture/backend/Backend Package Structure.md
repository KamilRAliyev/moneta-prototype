# Backend Package Structure

## Overview
The backend is a FastAPI application using Poetry for dependency management, SQLAlchemy for database operations, and Pydantic Settings for configuration management.

## Directory Structure

```
backend/
├── pyproject.toml          # Poetry project configuration and dependencies
├── poetry.lock              # Poetry lock file (dependency versions)
├── README.md               # Project documentation
├── server/                 # Main application package
│   ├── __init__.py         # Package initialization
│   └── settings/           # Configuration and settings module
│       ├── __init__.py     # Package initialization
│       ├── cors.py         # CORS middleware settings
│       └── database.py    # Database configuration and session management
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

### `server/settings/` Module

Configuration and settings management module using Pydantic Settings.

#### `server/settings/cors.py`
- **Purpose**: CORS middleware configuration
- **Class**: `CorsSettings` (extends `BaseSettings`)
- **Default Configuration**:
  - Origins: `["http://localhost:3000", "http://localhost:5173"]`
  - Allow credentials: `True`
  - Allow methods: `["*"]` (all methods)
  - Allow headers: `["*"]` (all headers)

#### `server/settings/database.py`
- **Purpose**: Database configuration and session management
- **Components**:
  - `DATABASE_URL`: Retrieved from environment variable (required)
  - `engine`: SQLAlchemy engine instance
  - `SessionLocal`: SQLAlchemy session factory
  - `get_db()`: FastAPI dependency for database sessions
- **Error Handling**: Raises `ValueError` if `DATABASE_URL` is not set
- **Session Management**: Automatic rollback on errors, proper cleanup

### `tests/` Directory

Test suite directory for unit and integration tests.

#### `tests/__init__.py`
- Package initialization file (currently empty)

## Technology Stack

- **Web Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0+
- **Configuration**: Pydantic Settings
- **Dependency Management**: Poetry
- **Database**: Configurable via `DATABASE_URL` environment variable

## Environment Variables

- `DATABASE_URL` (required): Database connection string for SQLAlchemy

## Initial State

This is the initial structure of the backend package. The following components are currently in place:

- ✅ Project configuration (Poetry)
- ✅ CORS settings module
- ✅ Database configuration module
- ✅ Test directory structure

## Future Expansion Areas

The following areas are ready for expansion:

- API routes and endpoints
- Database models (SQLAlchemy models)
- Business logic/services layer
- Authentication and authorization
- API documentation configuration
- Middleware setup
- Error handling and logging configuration
- Test implementations

