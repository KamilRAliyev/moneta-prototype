# Docker Development Environment

This document describes the Docker-based development environment architecture for Moneta.

## Overview

The development environment uses Docker Compose to orchestrate multiple services:
- **App**: Single container running both FastAPI backend and Vue 3 frontend with hot-reload
- **PostgreSQL**: Database server
- **pgAdmin**: Database administration tool

## Architecture Diagram

```mermaid
graph TB
    subgraph Host["Host Machine"]
        HostCode[Source Code<br/>/Users/.../illiterate_monkey]
        HostEnv[Environment Variables<br/>env/dev.env]
    end

    subgraph DockerNetwork["Docker Network: monkey_network"]
        subgraph AppContainer["App Container<br/>illiterate_monkey_app"]
            BackendApp[FastAPI App<br/>Port 8000<br/>Hot Reload]
            FrontendApp[Vite Dev Server<br/>Port 5173<br/>Hot Reload]
            BackendCode[Mounted Code<br/>/app/backend]
            FrontendCode[Mounted Code<br/>/app/frontend]
            AppEnv[Mounted Env<br/>/app/env]
        end

        subgraph PostgresContainer["PostgreSQL Container<br/>illiterate_monkey_db"]
            PostgresDB[(PostgreSQL 16<br/>Port 5432)]
            PostgresData[Persistent Data<br/>pgdata volume]
        end

        subgraph PgAdminContainer["pgAdmin Container<br/>illiterate_monkey_pgadmin"]
            PgAdminUI[pgAdmin 4<br/>Port 8080]
            PgAdminData[pgAdmin Data<br/>pgadmin_data volume]
        end
    end

    subgraph Volumes["Docker Volumes"]
        VolumePgData[(pgdata<br/>PostgreSQL Data)]
        VolumePgAdmin[(pgadmin_data<br/>pgAdmin Config)]
        VolumeMonetaData[(moneta_data<br/>/data Directory)]
    end

    subgraph External["External Access"]
        Browser[Developer Browser]
        LocalPort8000[localhost:8000<br/>API & Docs]
        LocalPort5173[localhost:5173<br/>Frontend Dev]
        LocalPort5432[localhost:5432<br/>PostgreSQL]
        LocalPort8080[localhost:8080<br/>pgAdmin]
    end

    %% Connections
    HostCode -.->|Volume Mount| BackendCode
    HostCode -.->|Volume Mount| FrontendCode
    HostEnv -.->|Volume Mount| AppEnv
    BackendCode --> BackendApp
    FrontendCode --> FrontendApp
    AppEnv --> BackendApp
    AppEnv --> FrontendApp
    BackendApp -->|Connects| PostgresDB
    FrontendApp -->|API Calls| BackendApp
    BackendApp -->|Writes| VolumeMonetaData
    PostgresDB --> PostgresData
    PostgresData --> VolumePgData
    PgAdminUI -->|Connects| PostgresDB
    PgAdminUI --> PgAdminData
    PgAdminData --> VolumePgAdmin

    Browser --> LocalPort8000
    Browser --> LocalPort5173
    Browser --> LocalPort8080
    LocalPort8000 --> BackendApp
    LocalPort5173 --> FrontendApp
    LocalPort8080 --> PgAdminUI
    LocalPort5432 --> PostgresDB

    %% Styling
    classDef host fill:#e0e7ff,stroke:#4f46e5,stroke-width:2px
    classDef container fill:#dbeafe,stroke:#2563eb,stroke-width:2px
    classDef volume fill:#fef3c7,stroke:#d97706,stroke-width:2px
    classDef external fill:#d1fae5,stroke:#059669,stroke-width:2px
    classDef service fill:#fce7f3,stroke:#db2777,stroke-width:2px

    class HostCode,HostEnv host
    class AppContainer,PostgresContainer,PgAdminContainer container
    class VolumePgData,VolumePgAdmin,VolumeMonetaData,PostgresData,PgAdminData volume
    class Browser,LocalPort8000,LocalPort5432,LocalPort8080 external
    class BackendApp,PostgresDB,PgAdminUI service
```

## Services

### App Service

**Container**: `illiterate_monkey_app`
**Image**: Built from `deploy/docker/Dockerfile`
**Ports**:
- `8000:8000` (host:container) - Backend API
- `5173:5173` (host:container) - Frontend Vite dev server

**Features**:
- Runs both FastAPI backend and Vue 3 frontend in a single container
- Hot-reload enabled for both services
- Source code mounted as volumes for live changes
- Environment variables loaded from `env/dev.env`
- Persistent data directory mounted at `/data`
- Frontend dependencies preserved in named volume

**Volume Mounts**:
- `../../backend:/app/backend` - Backend source code (read/write)
- `../../frontend:/app/frontend` - Frontend source code (read/write)
- `../../env:/app/env` - Environment files (read)
- `moneta_data:/data` - Persistent data directory
- `frontend_node_modules:/app/frontend/node_modules` - Preserves npm dependencies

**Processes**:
- **Backend**: Uvicorn with `--reload` watching `/app/backend/server`
- **Frontend**: Vite dev server with HMR on port 5173

**Dependencies**:
- Waits for PostgreSQL to be healthy before starting
- Installs frontend dependencies on startup if `node_modules` is missing

### PostgreSQL Service

**Container**: `illiterate_monkey_db`
**Image**: `postgres:16-alpine`
**Port**: `5432:5432` (host:container)

**Features**:
- Health check configured (`pg_isready`)
- Persistent data stored in `pgdata` volume
- Environment variables from `env/dev.env`
- **Custom `pg_hba.conf`** allows connections from the Docker network (app, pgAdmin) and from the host (e.g. `poetry run alembic upgrade head` or `psql` to `localhost:5432`). See `deploy/postgres/pg_hba.conf`.

**Volume Mounts**:
- `pgdata:/var/lib/postgresql/data` - Database files
- `../postgres/pg_hba.conf:/var/lib/postgresql/data/pg_hba.conf` - Client authentication (Docker + host)
- `../postgres/pg_hba.conf` and `../postgres/01-setup-pg_hba.sh` in `docker-entrypoint-initdb.d` - Apply same config on first DB init

**Health Check**:
- Command: `pg_isready -U $POSTGRES_USER`
- Interval: 30s
- Timeout: 10s
- Retries: 5

### pgAdmin Service

**Container**: `illiterate_monkey_pgadmin`
**Image**: `dpage/pgadmin4:latest`
**Port**: `8080:80` (host:container)

**Features**:
- Web-based database administration
- Persistent configuration in `pgadmin_data` volume
- Connects to PostgreSQL service

**Volume Mounts**:
- `pgadmin_data:/var/lib/pgadmin` - Configuration and data

**Dependencies**:
- Depends on PostgreSQL service

## Volumes

### Persistent Volumes

1. **pgdata**: PostgreSQL database files
   - Location: Docker managed volume
   - Purpose: Persist database across container restarts

2. **pgadmin_data**: pgAdmin configuration
   - Location: Docker managed volume
   - Purpose: Persist pgAdmin settings and server configurations

3. **moneta_data**: Application data directory
   - Location: Docker managed volume
   - Mounted at: `/data` in app container
   - Purpose: Persist uploaded files and application data

4. **frontend_node_modules**: Frontend npm dependencies
   - Location: Docker managed volume
   - Mounted at: `/app/frontend/node_modules` in app container
   - Purpose: Preserve npm dependencies when frontend code is mounted as volume

## Network

**Network Name**: `monkey_network`
**Driver**: `bridge`

All services communicate through this isolated Docker network. Services can reference each other by service name (e.g., `postgres`, `app`).

## Environment Variables

All services load environment variables from `env/dev.env`:

- Database configuration (`DB_*`, `POSTGRES_*`)
- Application settings (`APP_VERSION`, `ENVIRONMENT`, `DATA_DIR`)
- pgAdmin credentials (`PGADMIN_*`)

## Development Workflow

### Starting the Environment

```bash
cd deploy/compose
docker-compose -f docker-compose-dev.yml up
```

### Accessing Services

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Frontend Dev Server**: http://localhost:5173 (Vite with HMR)
- **pgAdmin**: http://localhost:8080
- **PostgreSQL**: localhost:5432

**Note**: Both backend and frontend run in the same container in development mode with hot-reload enabled. Changes to code in VS Code are automatically reflected in both services.

### Hot Reload

Both services support hot-reload:
- **Backend**: Uvicorn runs with `--reload` flag, automatically restarting when code changes are detected in the mounted `/app/backend/server` directory
- **Frontend**: Vite dev server provides Hot Module Replacement (HMR), instantly updating the browser when code changes are detected in the mounted `/app/frontend` directory

### Stopping the Environment

```bash
docker-compose -f docker-compose-dev.yml down
```

To remove volumes (⚠️ deletes data):
```bash
docker-compose -f docker-compose-dev.yml down -v
```

## File Structure

```
illiterate_monkey/
├── backend/                    # Backend source code (mounted to container)
├── frontend/                   # Frontend source code (mounted to container)
├── env/
│   └── dev.env                # Environment variables (mounted to container)
└── deploy/
    ├── docker/
    │   ├── Dockerfile         # App container image (Python + Node.js)
    │   └── entrypoint.sh      # Container startup script (runs both services)
    ├── postgres/
    │   ├── pg_hba.conf        # PostgreSQL client auth (Docker network + host)
    │   └── 01-setup-pg_hba.sh # Init script to apply pg_hba on first DB init
    └── compose/
        └── docker-compose-dev.yml  # Service definitions
```

## Data Persistence

- **Database**: Survives container restarts via `pgdata` volume
- **Application Data**: Survives container restarts via `moneta_data` volume
- **Source Code**: Changes on host are immediately reflected in container (volume mount)
- **pgAdmin Config**: Survives container restarts via `pgadmin_data` volume

## Notes

- The app container uses Python 3.11 with Poetry for backend dependencies and Node.js 20.x for frontend dependencies
- Both backend and frontend run in the same container for development convenience
- Hot-reload is enabled for both services
- Frontend dependencies are preserved in a named volume to avoid reinstalling on every container restart
- All services share the same environment file for consistency
- Network isolation ensures services can only communicate through defined interfaces
- Volume mounts allow live code editing without rebuilding containers
- The entrypoint script manages both processes and handles graceful shutdown
