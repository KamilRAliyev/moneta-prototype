**As a developer**,
I want database migrations wired in,
So that schema evolution is controlled from day one.

**Acceptance criteria**
- ✅ Alembic initialized
- ✅ alembic revision --autogenerate works
- ✅ alembic upgrade head runs inside container
- ✅ Empty baseline migration exists

## Implementation

### Setup Complete

Alembic has been configured with the following structure:

```
backend/
├── migrations/          # Alembic migration files
│   ├── versions/        # Migration version files
│   ├── env.py          # Alembic environment configuration
│   └── script.py.mako  # Migration template
├── server/
│   ├── models/         # SQLAlchemy models
│   │   ├── __init__.py # Base class for all models
│   │   └── example.py  # Example model (can be deleted)
│   ├── core/
│   │   ├── settings/   # Application settings
│   │   │   └── database.py # Database connection settings
│   │   └── database.py # Database connection utilities
└── alembic.ini         # Alembic configuration
```

### Database Configuration

Database settings are configured in `server/core/settings/database.py` and read from environment variables:

- `DB_HOST` (default: localhost)
- `DB_PORT` (default: 5432)
- `DB_USER` (default: postgres)
- `DB_PASSWORD` (default: empty)
- `DB_NAME` (default: moneta)

### Usage

1. **Create a migration:**
   ```bash
   poetry run alembic revision --autogenerate -m "Migration message"
   ```

2. **Apply migrations:**
   ```bash
   poetry run alembic upgrade head
   ```

3. **Rollback:**
   ```bash
   poetry run alembic downgrade -1
   ```

### Creating Models

1. Create model in `server/models/` inheriting from `Base`
2. Import model in `migrations/env.py` (see commented section)
3. Generate migration: `poetry run alembic revision --autogenerate -m "message"`
4. Apply: `poetry run alembic upgrade head`

### Using Database in FastAPI

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from server.core.database import get_db

@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    # Use db session here
    return {"items": []}
```

### Next Steps

- [x] Create empty baseline migration
- [x] Test migrations inside container
