As a developer,
I want structured logs,
So that debugging and later monitoring are easy.

Acceptance criteria
- ✅ JSON logs
- ✅ Each request has request_id
- ✅ Errors include stack traces in dev

## Status: ✅ Completed

**Implementation Details:**
- **Dual logging system:**
  - Standard logger (stdout): Human-readable format for development
  - JSON logger (stderr): Structured format for Loki/monitoring
- **Environment variable control:**
  - `LOGGING_STANDARD_ENABLED` (default: true)
  - `LOGGING_JSON_ENABLED` (default: true)
  - `LOGGING_LEVEL` (default: INFO)
- **Request ID middleware:**
  - Generates or extracts `X-Request-ID` header
  - Adds request_id to all log entries for correlation
  - Includes request_id in HTTP response headers
- **Error handling:**
  - Exception handlers with structured logging
  - Stack traces included in dev mode (`ENVIRONMENT=development`)
  - Request ID included in error responses

**Related Files:**
- `backend/server/core/logging.py` - Logging factory with dual output
- `backend/server/core/middleware.py` - Request ID middleware
- `backend/server/core/settings/app.py` - Logging configuration
- `backend/server/main.py` - Integrated logging, middleware, error handlers
- `backend/tests/test_logging.py` - Comprehensive test suite (11 tests)

**Documentation:**
- New `Logging.md` - Comprehensive architecture documentation with mermaid diagrams
- Updated `Backend Package Structure.md` with logging modules
- Updated `Environment Variables.md` with logging configuration
