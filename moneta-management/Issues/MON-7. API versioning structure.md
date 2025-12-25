**As a developer**,
I want a clean API routing structure,
So that future features don't create routing chaos.

**Acceptance criteria**
- ✅ /api/v1 router exists
- ✅ Routers split by concern (health, system, uploads/ingestion)
- ✅ OpenAPI docs available at /api/docs

## Status: ✅ Completed

**Implementation Details:**
- All API endpoints are now versioned under `/api/v1/`
- Routers organized by concern in `server/api/routers/v1/`:
  - `health.py` - Health check endpoint (`GET /api/v1/health`)
  - `system.py` - System information endpoints (`GET /api/v1/system/*`)
  - `uploads.py` - File upload endpoints (`POST /api/v1/uploads`)
- OpenAPI documentation configured at:
  - Swagger UI: `/api/docs`
  - ReDoc: `/api/redoc`
  - OpenAPI JSON: `/api/openapi.json`
- Clean router structure with v1 prefix for all endpoints
- All tests updated to use v1 endpoints

**Related Files:**
- `backend/server/api/routers/v1/` - Version 1 API routers directory
- `backend/server/main.py` - Router registration with v1 prefix
- `backend/tests/` - All tests updated to use `/api/v1/` endpoints

**Documentation:**
- Updated `API Endpoints.md` with v1 endpoint paths
- Updated `Backend Package Structure.md` with new v1 router structure
