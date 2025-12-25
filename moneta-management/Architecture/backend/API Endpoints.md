# API Endpoints

This document lists all available API endpoints in the Moneta backend.

## Base URL

All API endpoints are prefixed with `/api`.

## OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`
- OpenAPI JSON: `/api/openapi.json`

## Endpoints

All API endpoints are versioned under `/api/v1`.

### Health

#### `GET /api/v1/health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "server_time": "2025-12-25 00:00:00",
  "python_version": "3.13.7",
  "system": "Darwin",
  "hostname": "hostname",
  "process_id": 12345,
  "uptime_seconds": 123456,
  "app_version": "0.1.0"
}
```

### System

#### `GET /api/v1/system/info`

Get system information including app version, environment, and database connection status.

**Response:**
```json
{
  "app_version": "0.1.0",
  "environment": "development",
  "database_connected": true
}
```

**Fields:**
- `app_version` (string): Application version from `APP_VERSION` env var or default
- `environment` (string): Environment name from `ENVIRONMENT` env var or default
- `database_connected` (boolean): Whether database connection is available

#### `GET /api/v1/system/data-dir/test`

Test data directory read/write capabilities.

**Response (success):**
```json
{
  "status": "ok",
  "data_dir": "/data",
  "writable": true,
  "test_passed": true
}
```

**Response (error):**
```json
{
  "status": "error",
  "data_dir": "/data",
  "writable": false,
  "error": "Error message"
}
```

### Uploads (v1)

#### `POST /api/v1/uploads`

Upload a CSV file for ingestion. Files are saved without parsing or validation (placeholder implementation).

**Request:**
- Content-Type: `multipart/form-data`
- Body: File upload (form field: `file`)

**Response (201 Created):**
```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "path": "/data/uploads/550e8400-e29b-41d4-a716-446655440000.csv",
  "filename": "data.csv"
}
```

**Response Fields:**
- `file_id` (string): Unique UUID identifier for the uploaded file
- `path` (string): Full filesystem path where the file was saved
- `filename` (string): Original filename from the upload

**Notes:**
- Files are saved to `/data/uploads/{uuid}.csv`
- No file parsing or validation is performed (placeholder)
- File size limits are determined by FastAPI defaults

## Future Endpoints

The following endpoints are planned but not yet implemented:

- Reporting endpoints
- File processing and validation endpoints

## Notes

- All endpoints return JSON responses
- Error responses follow FastAPI's standard error format and include `request_id` for correlation
- All endpoints are versioned under `/api/v1/...` prefix
- OpenAPI documentation is available at `/api/docs`
