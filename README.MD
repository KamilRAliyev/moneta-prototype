# Moneta - Team Onboarding Guide

Welcome to the Moneta project! This guide will help you get started quickly.

## What is Moneta?

Moneta is a personal finance management application that helps you:
- Upload and manage bank statement files (CSV)
- Track transactions across multiple accounts
- Organize financial data with date locking and duplicate detection
- View and analyze transactions with filtering and sorting

## Setting Up a Similar Project from Scratch

If you want to understand how this project was initially scaffolded or create a similar project, here are the setup commands:

### Frontend Setup

1. **Create Vue 3 project with Vite and TypeScript:**
   ```bash
   npm create vite@latest frontend -- --template vue-ts
   cd frontend
   npm install
   ```

2. **Install recommended packages:**
   ```bash
   # State management
   npm install pinia

   # Routing
   npm install vue-router@4

   # HTTP client
   npm install axios

   # Styling
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p

   # UI component library
   npm install -D shadcn-vue
   npx shadcn-vue@latest init

   # Testing (optional)
   npm install -D vitest @vue/test-utils
   ```

3. **Key resources:**
   - [Vite](https://vite.dev/) - Build tool
   - [Pinia](https://pinia.vuejs.org/) - State management
   - [Vue Router](https://router.vuejs.org/) - Routing
   - [Axios](https://axios-http.com/docs/intro) - HTTP client
   - [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS
   - [shadcn-vue](https://www.shadcn-vue.com/) - Component library

### Backend Setup

1. **Create Poetry project:**
   ```bash
   poetry new --flat backend --name server
   cd backend
   ```

2. **Install core dependencies:**
   ```bash
   # Web framework
   poetry add fastapi uvicorn[standard]

   # Database
   poetry add sqlalchemy alembic psycopg2-binary

   # Environment management
   poetry add python-dotenv

   # Testing
   poetry add --group dev pytest pytest-asyncio
   ```

3. **Initialize Alembic (database migrations):**
   ```bash
   poetry run alembic init migrations
   ```

4. **Project structure:**
   ```
   backend/
   ├── server/          # Main application code
   │   ├── main.py      # FastAPI app entrypoint
   │   ├── api/         # API routes
   │   ├── models/      # SQLAlchemy models
   │   ├── services/    # Business logic
   │   └── core/        # Configuration (database, settings)
   ├── migrations/      # Alembic migrations
   ├── tests/           # Tests
   └── pyproject.toml   # Poetry dependencies
   ```

**Note**: The actual project uses FastAPI (not Flask) with Poetry for dependency management, SQLAlchemy for ORM, and Alembic for database migrations.

## Quick Start (Docker - Recommended)

The easiest way to get started is using Docker Compose, which sets up everything with one command.

### Prerequisites
- Docker & Docker Compose installed
- Git

### One-Command Setup

```bash
cd deploy/compose
docker compose -f docker-compose-dev.yml up --build
```

This starts:
- **PostgreSQL** database (port 5432)
- **pgAdmin** database admin UI (port 8080)
- **FastAPI backend** with hot reload (port 8000)
- **Vue 3 frontend** with HMR (port 5173)

### Access Points

Once running, access:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/api/docs
- **API Documentation (ReDoc)**: http://localhost:8000/api/redoc
- **pgAdmin**: http://localhost:8080
- **PostgreSQL**: localhost:5432

### Environment Variables

1. Copy the template: `cp env/dev.env.template env/dev.env`
2. Edit `env/dev.env` and configure:
   - Database credentials (`DB_*`, `POSTGRES_*`)
   - Application settings (`APP_VERSION`, `ENVIRONMENT`, etc.)

See [Environment Variables Documentation](./moneta-management/Architecture/Environment%20Variables.md) for all available options.

### Stopping the Environment

```bash
# Stop services (keeps data)
docker compose -f deploy/compose/docker-compose-dev.yml down

# Stop and remove volumes (⚠️ deletes all data)
docker compose -f deploy/compose/docker-compose-dev.yml down -v
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Package Manager**: Poetry
- **API Versioning**: `/api/v1/*`

### Frontend
- **Framework**: Vue 3 (Composition API with `<script setup>`)
- **Language**: TypeScript
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router 4
- **Styling**: Tailwind CSS 4 and shadcn-vue component library (https://www.shadcn-vue.com/)
- **HTTP Client**: Axios

## Development Workflow

### Running Locally (Docker - Recommended)

The Docker setup provides hot reload for both backend and frontend:
- **Backend**: Auto-reloads when files in `backend/server/` change
- **Frontend**: Hot Module Replacement (HMR) for instant updates

See [Dev Cheat Sheet](./moneta-management/Notes/Dev%20Cheat%20Sheet.md) for all commands.

### Running Locally (Native)

#### Backend
```bash
cd backend
poetry install
poetry run uvicorn server.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Running Tests

#### Backend Tests
```bash
cd backend
poetry run pytest
```

#### Frontend Tests
```bash
cd frontend
npm run test:run        # Run tests
npm run test:ui         # Run with UI
npm run test:coverage   # Run with coverage
```

### Database Migrations

#### Create a new migration
```bash
cd backend
poetry run alembic revision --autogenerate -m "Migration message"
```

#### Apply migrations
```bash
poetry run alembic upgrade head
```

#### Rollback one migration
```bash
poetry run alembic downgrade -1
```

#### Check current revision
```bash
poetry run alembic current
```

## Project Structure

```
illiterate_monkey/
├── backend/              # FastAPI backend (Poetry project)
│   ├── server/          # Application code
│   │   ├── api/         # API routes (versioned under /api/v1)
│   │   ├── models/      # SQLAlchemy models
│   │   ├── services/    # Business logic services
│   │   └── core/        # Core configuration (database, settings)
│   ├── migrations/      # Alembic migrations
│   └── tests/           # Backend tests
├── frontend/            # Vue 3 frontend
│   ├── src/
│   │   ├── views/       # Route-level pages
│   │   ├── components/  # Reusable components
│   │   ├── stores/      # Pinia state management
│   │   ├── services/    # API service layer
│   │   └── router/      # Vue Router configuration
│   └── tests/           # Frontend tests
├── deploy/              # Docker and deployment configs
│   ├── docker/         # Dockerfile and entrypoint
│   └── compose/         # Docker Compose files
├── env/                 # Environment variable files
│   ├── dev.env         # Development environment (not in git)
│   └── dev.env.template # Template for dev.env
└── moneta-management/   # Comprehensive documentation
    ├── Architecture/   # System architecture docs
    ├── Business Logic/  # Business logic documentation
    ├── Issues/          # Feature specifications
    └── Notes/           # Development notes
```

## Documentation

### Comprehensive Documentation

All detailed documentation is in the `moneta-management/` folder:

- **Architecture**: System design, API endpoints, database schema
  - [Architecture Overview](./moneta-management/Architecture/Moneta%20Code%20Architecture%20Document%20v0.1.md)
  - [Docker Development Environment](./moneta-management/Architecture/Docker%20Development%20Environment.md)
  - [API Endpoints](./moneta-management/Architecture/backend/API%20Endpoints.md)
  - [Frontend Architecture](./moneta-management/Architecture/frontend/Frontend%20Architecture.md)

- **Business Logic**: Complex business rules and flows
  - [Date Lock Logic](./moneta-management/Business%20Logic/Date%20Lock%20Logic.md)
  - [CSV Metadata Extraction](./moneta-management/Business%20Logic/CSV%20Metadata%20Extraction.md)
  - [Statement File Upload](./moneta-management/Business%20Logic/Statement%20File%20Upload.md)

- **Development Resources**:
  - [Dev Cheat Sheet](./moneta-management/Notes/Dev%20Cheat%20Sheet.md) - Quick reference for common commands
  - [Feature Implementation Checklist](./moneta-management/Notes/Feature%20Implementation%20Checklist.md) - Standards for new features
  - [Issues](./moneta-management/Issues/) - Feature specifications and requirements

### Quick Reference

- **API Docs**: http://localhost:8000/api/docs (when running)
- **Environment Variables**: [Environment Variables Documentation](./moneta-management/Architecture/Environment%20Variables.md)
- **All Commands**: [Dev Cheat Sheet](./moneta-management/Notes/Dev%20Cheat%20Sheet.md)

## Knowledge Base

### Vue.js Essentials

To work effectively with the frontend, understand:

1. **Vue Core Concepts**
   - [Vue 3 Tutorial](https://vuejs.org/tutorial/#step-1) - Official tutorial
   - Composition API with `<script setup>` syntax
   - Reactivity system (ref, reactive, computed)

2. **State Management (Pinia)**
   - [Pinia Documentation](https://pinia.vuejs.org/)
   - Why we use Pinia: Centralized state management across components
   - Composition API style stores (not Options API)

3. **Composables vs Stores**
   - **Composables**: Reusable logic functions (like React hooks)
   - **Stores**: Shared state that persists across components
   - Use composables for logic, stores for shared state

4. **Vue Router**
   - [Vue Router Documentation](https://router.vuejs.org/)
   - Route definitions and navigation
   - Layout components

### Backend Essentials

- **FastAPI**: Modern Python web framework with automatic API docs
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration tool
- **Poetry**: Python dependency management

**Note**: You don't need to memorize everything. The codebase is well-documented, and AI tools can help with implementation details. Focus on understanding the architecture and patterns.

## Common Tasks

### View API Documentation
When the backend is running, visit http://localhost:8000/api/docs for interactive Swagger UI.

### Access Database via pgAdmin
1. Open http://localhost:8080
2. Login with credentials from `env/dev.env` (`PGADMIN_DEFAULT_EMAIL` / `PGADMIN_DEFAULT_PASSWORD`)
3. Add server: Host = `postgres`, User = `postgres`, Password from `env/dev.env`

### Run Tests Inside Docker
```bash
# Backend tests
docker exec -it illiterate_monkey_app bash
cd /app/backend
poetry run pytest

# Frontend tests
docker exec -it illiterate_monkey_app bash
cd /app/frontend
npm run test:run
```

### Check Logs
```bash
# All services
docker compose -f deploy/compose/docker-compose-dev.yml logs

# Specific service
docker compose -f deploy/compose/docker-compose-dev.yml logs app
```

## Getting Help

1. **Check Documentation**: Start with `moneta-management/` folder
2. **API Docs**: Use Swagger UI at http://localhost:8000/api/docs
3. **Dev Cheat Sheet**: Quick reference for commands
4. **Architecture Docs**: Understand system design before making changes

## Next Steps

1. ✅ Get the project running with Docker Compose
2. ✅ Explore the API documentation at http://localhost:8000/api/docs
3. ✅ Review the [Architecture Overview](./moneta-management/Architecture/Moneta%20Code%20Architecture%20Document%20v0.1.md)
4. ✅ Read the [Dev Cheat Sheet](./moneta-management/Notes/Dev%20Cheat%20Sheet.md) for common commands
5. ✅ Check [Feature Implementation Checklist](./moneta-management/Notes/Feature%20Implementation%20Checklist.md) before starting new features

---

**Remember**: This README is a quick start guide. For detailed information, see the comprehensive documentation in `moneta-management/`.
