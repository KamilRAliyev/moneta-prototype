**As a user**,
I want to upload a CSV file,
So that ingestion plumbing can be tested.

**Acceptance criteria**
- ✅ POST /api/v1/uploads
- ✅ File saved to /data/uploads/{uuid}.csv
- ✅ No parsing or validation yet
- ✅ Response returns file ID + path

## Status: ✅ Completed

**Implementation Details:**
- Endpoint: `POST /api/v1/uploads`
- Files are saved with UUID-based naming: `/data/uploads/{uuid}.csv`
- Uploads directory is auto-created if it doesn't exist
- Response includes:
  - `file_id`: Unique UUID identifier
  - `path`: Full filesystem path
  - `filename`: Original filename from upload
- Request ID middleware adds `X-Request-ID` header to responses
- Comprehensive test coverage (5 tests)

**Related Files:**
- `backend/server/api/routers/uploads.py` - Upload endpoint implementation
- `backend/server/services/data_dir.py` - Added `ensure_uploads_dir()` function
- `backend/tests/test_uploads.py` - Test suite

**Documentation:**
- Updated `API Endpoints.md` with endpoint documentation
- Updated `Backend Package Structure.md` with router details
