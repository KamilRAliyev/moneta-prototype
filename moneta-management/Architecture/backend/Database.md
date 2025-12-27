# Database Architecture

This document describes how database connections, models, and migrations work in the Moneta backend.

## Overview

The backend uses:
- **PostgreSQL** as the database
- **SQLAlchemy 2.0+** as the ORM
- **Alembic** for database migrations
- **psycopg** (v3) as the PostgreSQL driver

## Architecture Diagram

```mermaid
flowchart TB
    %% Environment Variables
    subgraph ENV["Environment Variables"]
        DB_HOST[DB_HOST]
        DB_PORT[DB_PORT]
        DB_USER[DB_USER]
        DB_PASSWORD[DB_PASSWORD]
        DB_NAME[DB_NAME]
        DB_POOL[DB_POOL_SIZE<br/>DB_MAX_OVERFLOW<br/>DB_POOL_PRE_PING]
    end

    %% Settings Layer
    subgraph SETTINGS["Settings Layer<br/>server/core/settings/database.py"]
        DB_SETTINGS[DatabaseSettings<br/>Reads env vars]
        ASYNC_URL[database_url<br/>postgresql+psycopg://]
        SYNC_URL[database_url_sync<br/>postgresql://]
    end

    %% Database Connection Layer
    subgraph CONN["Connection Layer<br/>server/core/database.py"]
        GET_ENGINE[get_engine<br/>Lazy initialization]
        GET_SESSION[get_session_local<br/>Session factory]
        ENGINE[SQLAlchemy Engine<br/>Connection Pool]
        SESSION_FACTORY[SessionLocal<br/>Session Factory]
    end

    %% Application Usage
    subgraph APP["Application Usage"]
        GET_DB[get_db<br/>FastAPI Dependency]
        GET_DB_CTX[get_db_session<br/>Context Manager]
        SESSION[Database Session]
    end

    %% Models Layer
    subgraph MODELS["Models Layer<br/>server/models/"]
        BASE[Base<br/>DeclarativeBase]
        MODEL1[Model 1]
        MODEL2[Model 2]
        MODELN[Model N]
    end

    %% Migrations
    subgraph MIGRATIONS["Migrations<br/>Alembic"]
        ALEMBIC_INI[alembic.ini]
        ENV_PY[migrations/env.py<br/>Uses db_settings]
        VERSIONS[migrations/versions/<br/>Migration files]
    end

    %% Database
    POSTGRES[(PostgreSQL<br/>Database)]

    %% Connections
    ENV --> DB_SETTINGS
    DB_SETTINGS --> ASYNC_URL
    DB_SETTINGS --> SYNC_URL

    ASYNC_URL --> GET_ENGINE
    GET_ENGINE --> ENGINE
    ENGINE --> GET_SESSION
    GET_SESSION --> SESSION_FACTORY

    SESSION_FACTORY --> GET_DB
    SESSION_FACTORY --> GET_DB_CTX
    GET_DB --> SESSION
    GET_DB_CTX --> SESSION

    BASE --> MODEL1
    BASE --> MODEL2
    BASE --> MODELN

    SESSION --> MODEL1
    SESSION --> MODEL2
    SESSION --> MODELN

    ENGINE --> POSTGRES
    SESSION --> POSTGRES

    SYNC_URL --> ENV_PY
    ALEMBIC_INI --> ENV_PY
    ENV_PY --> VERSIONS
    VERSIONS --> POSTGRES
    BASE -.->|Metadata| ENV_PY

    %% Styling
    classDef envStyle fill:#e0f2fe,stroke:#0369a1,stroke-width:2px
    classDef settingsStyle fill:#dbeafe,stroke:#1e40af,stroke-width:2px
    classDef connStyle fill:#d1fae5,stroke:#065f46,stroke-width:2px
    classDef appStyle fill:#fef3c7,stroke:#92400e,stroke-width:2px
    classDef modelStyle fill:#e9d5ff,stroke:#6b21a8,stroke-width:2px
    classDef migrationStyle fill:#fed7aa,stroke:#9a3412,stroke-width:2px
    classDef dbStyle fill:#f3f4f6,stroke:#374151,stroke-width:3px

    class DB_HOST,DB_PORT,DB_USER,DB_PASSWORD,DB_NAME,DB_POOL envStyle
    class DB_SETTINGS,ASYNC_URL,SYNC_URL settingsStyle
    class GET_ENGINE,GET_SESSION,ENGINE,SESSION_FACTORY connStyle
    class GET_DB,GET_DB_CTX,SESSION appStyle
    class BASE,MODEL1,MODEL2,MODELN modelStyle
    class ALEMBIC_INI,ENV_PY,VERSIONS migrationStyle
    class POSTGRES dbStyle
```

## Connection Flow

```mermaid
sequenceDiagram
    participant App as FastAPI App
    participant Route as API Route
    participant GetDB as get_db()
    participant Session as Database Session
    participant Engine as SQLAlchemy Engine
    participant Pool as Connection Pool
    participant PG as PostgreSQL

    App->>Route: Request arrives
    Route->>GetDB: Depends(get_db)
    GetDB->>Engine: get_engine() (lazy init)
    Engine->>Pool: Create connection pool
    Pool->>PG: Establish connections
    GetDB->>Session: Create session
    Route->>Session: Execute query
    Session->>Pool: Get connection
    Pool->>PG: Execute SQL
    PG-->>Pool: Return results
    Pool-->>Session: Return connection
    Session-->>Route: Return data
    Route-->>App: Response
    GetDB->>Session: Close session (finally)
    Session->>Pool: Return connection
```

## Database Connection

### Connection Settings

Database configuration is managed through `server/core/settings/database.py` using the `DatabaseSettings` class. All settings are read from environment variables with sensible defaults.

### Connection Architecture

The database connection uses **lazy initialization**:

1. **Engine Creation**: The SQLAlchemy engine is created only when first needed (not at import time)
2. **Session Factory**: Session factory is created lazily, bound to the engine
3. **Connection Pooling**: Configured with pool size, max overflow, and connection health checks

### Key Components

#### `server/core/settings/database.py`
- `DatabaseSettings` class: Reads environment variables and generates database URLs
- Properties:
  - `database_url`: Async PostgreSQL URL (`postgresql+psycopg://...`)
  - `database_url_sync`: Sync PostgreSQL URL (`postgresql://...`) for Alembic

#### `server/core/database.py`
- `get_engine()`: Returns the database engine (lazy initialization)
- `get_session_local()`: Returns the session factory (lazy initialization)
- `get_db()`: FastAPI dependency for database sessions (auto-closes)
- `get_db_session()`: Context manager for manual session handling
- `init_db()`: Creates tables from models (not recommended, use Alembic instead)

## Models

### Base Class

All models inherit from `Base` defined in `server/models/__init__.py`:

```python
from server.models import Base

class MyModel(Base):
    __tablename__ = "my_table"
    # ... columns
```

### Model Structure

Models are stored in `server/models/` directory:
- Each model should be in its own file or logically grouped
- Models must be imported in `migrations/env.py` for Alembic autogenerate to work

### Example Model

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from server.models import Base

class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Account Model

The `Account` model represents financial accounts in the system.

**Table:** `accounts`

**Fields:**
- `id` (Integer, Primary Key): Unique identifier
- `name` (String(255), Required): Account name
- `institution` (String(255), Required): Financial institution name
- `currency` (Enum, Required): ISO 4217 currency code (using `iso4217` library)
- `type` (Enum, Required): Account type (checking, savings, credit_card, cash, investment, loan)
- `economic_area` (Enum, Optional): Economic region classification (eu, us, uk, cis, mena, apac, china, other)
- `datelock_from` (Date, Optional): Date lock start (marks dates >= this as already ingested)
- `datelock_to` (Date, Optional): Date lock end (marks dates <= this as already ingested)
- `created_at` (DateTime, Auto): Record creation timestamp
- `updated_at` (DateTime, Auto): Record last update timestamp

**Enums:**
- `AccountType`: checking, savings, credit_card, cash, investment, loan
- `Currency`: All ISO 4217 currency codes (dynamically generated from `iso4217` library)
- `EconomicArea`: eu, us, uk, cis, mena, apac, china, other

**Date Lock (`datelock_from`, `datelock_to`):**
- Per-account ingestion guardrail (two-sided date lock)
- Marks date ranges that have **already been ingested**
- Transactions **within** `[datelock_from, datelock_to]` (inclusive) → **skipped** (already ingested)
- Transactions **outside** this range → **ingested** (not yet ingested)
- Either field can be `null`:
  - `datelock_from` only: Skip dates >= from, ingest dates < from
  - `datelock_to` only: Skip dates <= to, ingest dates > to
  - Both `null`: No lock (ingest all transactions)
- Validation: `datelock_from <= datelock_to` if both are set
- Affects future ingestion only (does not delete existing data)

**Model File:** `server/models/account.py`

**Migration:** `60f2323257db_add_accounts_table.py`

### StatementFile Model

The `StatementFile` model represents uploaded CSV statement files associated with accounts.

**Table:** `statement_files`

**Fields:**
- `id` (UUID, Primary Key): Unique identifier (UUID v4)
- `account_id` (Integer, Foreign Key → accounts.id, Required): Account this statement belongs to
- `original_filename` (String(255), Required): Original uploaded filename
- `stored_filename` (String(255), Required): Renamed filename (`{uuid}.csv`)
- `stored_path` (String(512), Required): Full path: `/data/statements/{uuid}.csv`
- `format` (Enum, Required): File format: `csv` (v1 only, extensible for future formats)
- `size_bytes` (Integer, Required): File size in bytes
- `content_hash` (String(64), Required): SHA-256 hash (hex string, 64 chars) for duplicate detection
- `row_count` (Integer, Required): Number of data rows (excluding header)
- `columns` (JSON, Optional): CSV header column names as JSON array (nullable if parsing fails)
- `date_from` (Date, Optional): Inferred earliest transaction date (nullable)
- `date_to` (Date, Optional): Inferred latest transaction date (nullable)
- `status` (Enum, Required): Current status: `uploaded` (v1 only, extensible)
- `is_ingested` (Boolean, Required, Default: false): Whether transactions have been ingested
- `ingested_at` (DateTime(timezone=True), Optional): Timestamp when ingestion completed (nullable)
- `ingested_rows_count` (Integer, Required, Default: 0): Number of rows successfully ingested
- `ingestion_errors_count` (Integer, Required, Default: 0): Number of errors encountered during ingestion
- `date_column` (String(255), Optional): Detected date column name (for deterministic ingestion)
- `created_at` (DateTime(timezone=True), Auto): Record creation timestamp
- `updated_at` (DateTime(timezone=True), Auto): Record last update timestamp

**Enums:**
- `StatementFormat`: csv
- `StatementStatus`: uploaded

**Constraints:**
- Unique constraint: `(account_id, content_hash)` - prevents duplicate uploads per account
- Index: `(account_id, created_at DESC)` - optimize list queries by account
- Foreign key: `account_id` → `accounts.id` (CASCADE on delete)

**Duplicate Detection:**
- Content-based deduplication using SHA-256 hash
- Same file can be uploaded to different accounts (different `account_id`)
- Duplicate uploads to the same account return `409 Conflict` with existing statement details

**CSV Metadata Extraction:**
- Row count: Counts data rows (excluding header)
- Columns: Extracts header row as JSON array
- Date range: Infers date column and extracts earliest/latest dates using `dateinfer` library with fallback to `dateutil.parser`
- Metadata extraction failures are non-fatal (nullable fields)

**File Storage:**
- Files stored at `/data/statements/{uuid}.csv`
- Atomic operation: File write + DB insert must succeed or fail together
- On DB failure, file is deleted (rollback)
- On file write failure, no DB record is created

**Model File:** `server/models/statement_file.py`

**Migrations:**
- `0a1430f21d66_add_statement_files_table.py` - Initial table creation
- `be9c3b99c92e_add_statementfile_extensions_ingested_.py` - Added `ingested_rows_count`, `ingestion_errors_count`, `date_column`

### Transaction Model

The `Transaction` model represents ingested transaction data from statement files.

**Table:** `transactions`

**Fields:**
- `id` (UUID, Primary Key): Unique identifier (UUID v4)
- `account_id` (Integer, Foreign Key → accounts.id, Required): Account this transaction belongs to
- `statement_file_id` (UUID, Foreign Key → statement_files.id, Required): Source statement file
- `row_id` (Integer, Required): Row index in the statement file (0-based)
- `ingested_content` (JSONB, Required): Raw row data as-is (JSONB for PostgreSQL, JSON for SQLite)
- `transaction_hash` (String(64), Required): SHA-256 hash of `(row_id + normalized JSON)` for change tracking
- `computed_content` (JSONB, Optional): Computed/enriched data (empty for now, out of scope)
- `computed_content_hash` (String(64), Optional): Hash of computed content
- `inserted_at` (DateTime(timezone=True), Auto): Ingestion timestamp
- `updated_at` (DateTime(timezone=True), Auto): Last update timestamp
- `computed_at` (DateTime(timezone=True), Optional): Computation timestamp (null, out of scope)

**Constraints:**
- Unique constraint: `(statement_file_id, row_id)` - Prevents duplicate rows from same statement (idempotency)
- Index: `(account_id, inserted_at DESC)` - Optimize list queries by account, ordered by newest first
- Index: `(statement_file_id)` - Optimize queries by statement file
- Index: `(transaction_hash)` - For change tracking and diagnostics
- Foreign key: `account_id` → `accounts.id` (CASCADE on delete)
- Foreign key: `statement_file_id` → `statement_files.id` (CASCADE on delete)

**Transaction Hash:**
- Calculated as: `SHA-256(row_id + normalized JSON of ingested_content)`
- Used for change tracking/diagnostics (detect if content changed between ingestion runs)
- **NOT used for duplicate detection** - that's handled by unique constraint `(statement_file_id, row_id)`
- Normalized JSON: keys sorted for consistent hashing regardless of dict order

**Idempotency:**
- Re-ingesting the same statement file is idempotent
- Duplicate rows (same `statement_file_id` + `row_id`) are skipped, not updated
- Allows safe re-ingestion after changing date locks or fixing errors

**Implementation Notes:**
- Uses `add_all()` for bulk inserts (SQLAlchemy 2.0+ compatible)
- Transaction error handling with proper rollback on database errors
- Type-aware sorting uses column metadata from `/meta` endpoint for proper numeric/date/text sorting

**Model File:** `server/models/transaction.py`

**Migration:** `af4e2044a3bb_create_transactions_table.py`

## Migrations (Alembic)

### Migration Structure

```
backend/
├── alembic.ini              # Alembic configuration
└── migrations/
    ├── env.py              # Migration environment (connects to DB settings)
    ├── script.py.mako      # Migration template
    └── versions/           # Migration files
        └── 0001_baseline.py
```

### How Migrations Work

1. **Configuration**: `alembic.ini` points to `migrations/` folder
2. **Environment**: `migrations/env.py` imports database settings and models
3. **Database URL**: Set dynamically from `db_settings.database_url_sync`
4. **Model Detection**: Uses `Base.metadata` to detect model changes

### Creating Migrations

1. **Create/Modify Models**: Add or update models in `server/models/`
2. **Import Models**: Add model imports to `migrations/env.py` (commented section)
3. **Generate Migration**:
   ```bash
   poetry run alembic revision --autogenerate -m "description"
   ```
4. **Review Migration**: Check the generated file in `migrations/versions/`
5. **Apply Migration**:
   ```bash
   poetry run alembic upgrade head
   ```

### Migration Commands

- **Create empty migration**: `poetry run alembic revision -m "message"`
- **Auto-generate migration**: `poetry run alembic revision --autogenerate -m "message"`
- **Apply migrations**: `poetry run alembic upgrade head`
- **Rollback one migration**: `poetry run alembic downgrade -1`
- **Show current revision**: `poetry run alembic current`
- **Show history**: `poetry run alembic history`

## Using Database in FastAPI

### Dependency Injection (Recommended)

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from server.core.database import get_db

@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return items
```

The `get_db()` dependency:
- Creates a session
- Yields it to the route handler
- Automatically closes the session when done
- Handles rollback on exceptions

### Context Manager (Manual Control)

```python
from server.core.database import get_db_session

with get_db_session() as db:
    item = Item(name="test")
    db.add(item)
    # Automatically commits on success, rolls back on error
```

## Connection Pooling

The database uses connection pooling with the following settings:

- **Pool Size**: Number of connections to maintain (default: 5)
- **Max Overflow**: Additional connections allowed beyond pool size (default: 10)
- **Pool Pre-ping**: Checks connection health before use (default: true)
- **Echo**: Logs SQL queries (default: false, enable for debugging)

## Best Practices

1. **Always use migrations** - Never use `init_db()` in production
2. **Import models in env.py** - Required for autogenerate to work
3. **Review generated migrations** - Always check autogenerated migrations before applying
4. **Use dependency injection** - Prefer `get_db()` over manual session management
5. **Handle transactions** - Use context managers or ensure proper commit/rollback
6. **Don't run migrations in entrypoint** - Run migrations separately, not on every container start

## Testing

Tests use an in-memory SQLite database to avoid requiring PostgreSQL. See [Testing.md](./Testing.md) for details.

## Troubleshooting

### Connection Issues
- Verify environment variables are set correctly
- Check PostgreSQL is running and accessible
- Verify network connectivity (in containers, use service names)

### Migration Issues
- Ensure models are imported in `migrations/env.py`
- Check database URL is correct in settings
- Verify database user has CREATE/ALTER permissions

### Session Issues
- Always use `get_db()` or `get_db_session()` - don't create sessions manually
- Ensure sessions are properly closed (automatic with dependencies)
- Check for uncommitted transactions
