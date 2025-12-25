**As the system**,
I want a persistent /data directory,
So that imported files survive container restarts.

**Acceptance criteria**
- ✅ /data mounted as volume
- ✅ App can read/write test files there
- ✅ Path configurable via env (DATA_DIR)

**Status:** ✅ Complete
- Added `/data` volume mount in docker-compose
- Created `data_dir` service with `ensure_data_dir()` and test utilities
- Added `DATA_DIR` environment variable (default: `/data`)
- Data directory initialized on app startup via lifespan handler
- Added `GET /api/system/data-dir/test` endpoint for verification
- Tests added and passing
- Documentation updated
