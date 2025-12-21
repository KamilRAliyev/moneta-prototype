#architecture
___
# 1) High Level System Shape

**Single container** runs:
1. **FastAPI backend** (API, ingestion, rules, reporting endpoints)
2. Frontend (Vue3) served by the backend APIs

# 2) Repository Layout
```
moneta/
	backend/                  # FastAPI poetry module
		server/
	        __init__.py
	        main.py               # FastAPI entrypoint, mounts API + static
	        settings.py           # env + config
	        api/                  # routers
	          v1/
	            routes_*.py
	        domain/               # pure domain logic (no FastAPI imports)
	        services/             # orchestration, use-cases
	        adapters/             # IO boundaries (db, files, external)
	    db/
	        models.py
	        migrations/           # Alembic    
	    workers/                  # background jobs (optional v1)
	        observability/        # logging, metrics, tracing stubs
		tests/                    # tests
		pyproject.toml            # requeirements and other pypackage configs
		README.MD                 # empty docs file (requeired)
	env/
		dev.env                   # Development Environment Vars
		dev.template              # Template with needed vars to populate
	frontend/                     # Vue 3 app
      src/
      public/
      index.html
      vite.config.ts
      package.json
      tests/
  deploy/
    docker/
      Dockerfile
      entrypoint.sh
    compose/
      docker-compose.dev.yml
      docker-compose.prod.yml
```

# 3) **Container strategy (single image)**

## 3.1) Build  Steps (multi-staged Dockerfile)

- Stage A: build Vue -> frontend/src/dist
- Stage B: Install Python depth + mount backend folder
- Copy dist/ into backend package (or /static folder)
-  Run FastAPI with Gunicorn+Uvicorn workers

## 3.2) Serving frontend

FastAPI mounts:
- StaticFiles(directory=".../dist")
- SPA fallback: unknown routes return index.html

Example routing convention:

- /api/v1/... for API
- /assets/... for built assets
- /* for SPA

# 4) Runtime process model

- **Gunicorn** (master) + **UvicornWorker** (workers)
- No separate node server


# 5) CI/CD baseline (infra-first)
- PreCommit
- Linters:
    - Python: ruff + mypy (optional)
    - Vue: eslint + typecheck
- Test:
	- Pytest
- Build docker image
- Run smoke test

```mermaid
flowchart TB
    %% ========= Client =========
    User[User Browser]

    %% ========= Container =========
    subgraph C["Moneta Application Container"]
        direction TB

        FE[Vue 3 SPA<br/>Static Assets]

        API[FastAPI Application]

        subgraph BL["Backend Internal Architecture"]
            direction TB
            Routes[API Routes<br/>/api/v1]
            Services[Application Services<br/>Use-cases]
            Domain[Domain Layer<br/>Finance Logic<br/>Rules • Categorization]
            Adapters[Adapters<br/>DB • File • External APIs]
        end

        FE --> API
        API --> Routes
        Routes --> Services
        Services --> Domain
        Domain --> Adapters
    end

    %% ========= Infrastructure =========
    DB[(PostgreSQL)]
    FS[(Persistent Volume<br/>/data)]
    Ext[External Sources<br/>CSVs • Banks • Brokers]

    %% ========= Connections =========
    User --> FE
    Adapters --> DB
    Adapters --> FS
    Ext --> Adapters

    %% ========= Styling =========
    classDef client fill:#dbeafe,stroke:#1e40af,stroke-width:2px,color:#000;
    classDef frontend fill:#bfdbfe,stroke:#1d4ed8,stroke-width:2px,color:#000;
    classDef api fill:#bbf7d0,stroke:#15803d,stroke-width:2px,color:#000;
    classDef domain fill:#e9d5ff,stroke:#7e22ce,stroke-width:2px,color:#000;
    classDef adapter fill:#fed7aa,stroke:#c2410c,stroke-width:2px,color:#000;
    classDef infra fill:#e5e7eb,stroke:#374151,stroke-width:2px,color:#000;

    %% ========= Class Assignment =========
    class User client
    class FE frontend
    class API,Routes,Services api
    class Domain domain
    class Adapters adapter
    class DB,FS,Ext infra
```
