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

### Accounts (v1)

#### `GET /api/v1/accounts`

List all accounts with pagination.

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum number of records to return (default: 100)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "My Checking Account",
    "institution": "Bank of Example",
    "currency": "USD",
    "account_type": "checking",
    "economic_area": "us",
    "datelock_from": "2023-01-01",
    "created_at": "2025-12-26T00:00:00Z",
    "updated_at": null
  }
]
```

#### `GET /api/v1/accounts/{id}`

Get account details by ID.

**Path Parameters:**
- `id` (integer): Account ID

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "My Checking Account",
  "institution": "Bank of Example",
  "currency": "USD",
  "account_type": "checking",
  "economic_area": "us",
  "datelock_from": "2023-01-01",
  "created_at": "2025-12-26T00:00:00Z",
  "updated_at": null
}
```

**Error Responses:**
- `404 Not Found`: Account not found

#### `POST /api/v1/accounts`

Create a new account.

**Request Body:**
```json
{
  "name": "My Checking Account",
  "institution": "Bank of Example",
  "currency": "USD",
  "account_type": "checking",
  "economic_area": "us",
  "datelock_from": "2023-01-01"
}
```

**Required Fields:**
- `name` (string): Account name
- `institution` (string): Financial institution name
- `currency` (string): ISO 4217 currency code (e.g., "USD", "EUR")
- `account_type` (string): Account type (checking, savings, credit_card, cash, investment, loan)

**Optional Fields:**
- `economic_area` (string): Economic area (eu, us, uk, cis, mena, apac, china, other)
- `datelock_from` (date): Date lock for ingestion (YYYY-MM-DD format)

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "My Checking Account",
  "institution": "Bank of Example",
  "currency": "USD",
  "account_type": "checking",
  "economic_area": "us",
  "datelock_from": "2023-01-01",
  "created_at": "2025-12-26T00:00:00Z",
  "updated_at": null
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input data (invalid currency, account type, or economic area)
- `500 Internal Server Error`: Database error

#### `PUT /api/v1/accounts/{id}`

Update an existing account.

**Path Parameters:**
- `id` (integer): Account ID

**Request Body:**
```json
{
  "name": "Updated Account Name",
  "institution": "Updated Bank",
  "currency": "EUR",
  "account_type": "savings",
  "economic_area": "eu",
  "datelock_from": "2024-01-01"
}
```

All fields are optional. Only provided fields will be updated.

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Updated Account Name",
  "institution": "Updated Bank",
  "currency": "EUR",
  "account_type": "savings",
  "economic_area": "eu",
  "datelock_from": "2024-01-01",
  "created_at": "2025-12-26T00:00:00Z",
  "updated_at": "2025-12-26T01:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Account not found
- `500 Internal Server Error`: Database error

#### `DELETE /api/v1/accounts/{id}`

Delete an account.

**Path Parameters:**
- `id` (integer): Account ID

**Response (204 No Content):**
No response body.

**Error Responses:**
- `404 Not Found`: Account not found
- `500 Internal Server Error`: Database error

### Statements (v1)

#### `POST /api/v1/statements`

Upload a CSV statement file for an account.

**Request:**
- Content-Type: `multipart/form-data`
- Fields:
  - `file` (required): CSV file
  - `account_id` (required, query parameter): Account ID (integer)

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "account_id": 1,
  "account_name": "My Checking Account",
  "original_filename": "statement_2024_01.csv",
  "stored_filename": "550e8400-e29b-41d4-a716-446655440000.csv",
  "stored_path": "/data/statements/550e8400-e29b-41d4-a716-446655440000.csv",
  "format": "csv",
  "size_bytes": 10240,
  "content_hash": "a1b2c3d4e5f6...",
  "row_count": 150,
  "columns": ["Date", "Description", "Amount"],
  "date_from": "2024-01-01",
  "date_to": "2024-01-31",
  "status": "uploaded",
  "is_ingested": false,
  "ingested_at": null,
  "file_exists": true,
  "created_at": "2025-12-26T10:00:00Z",
  "updated_at": "2025-12-26T10:00:00Z"
}
```

**Response Fields:**
- `file_exists` (boolean): Whether the file exists on disk (checked on each request)

**Error Responses:**
- `400 Bad Request`: Invalid account_id, missing file, or invalid CSV
- `404 Not Found`: Account not found
- `409 Conflict`: Duplicate file (same account + content hash)
- `422 Unprocessable Entity`: File validation failed (size limit, wrong format)

**Notes:**
- Files are saved to `/data/statements/{uuid}.csv`
- CSV metadata is automatically extracted (row count, columns, date range)
- Duplicate detection is based on account_id + content_hash (SHA-256)
- Date format inference uses `dateinfer` library with fallback to `dateutil.parser`

#### `GET /api/v1/statements`

List statement files with optional filtering and pagination.

**Query Parameters:**
- `account_id` (integer, optional): Filter by account ID
- `skip` (integer, optional): Pagination offset (default: 0)
- `limit` (integer, optional): Max results (default: 100, max: 1000)

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "account_id": 1,
    "account_name": "My Checking Account",
    "original_filename": "statement_2024_01.csv",
    "size_bytes": 10240,
    "row_count": 150,
    "date_from": "2024-01-01",
    "date_to": "2024-01-31",
    "status": "uploaded",
    "is_ingested": false,
    "file_exists": true,
    "created_at": "2025-12-26T10:00:00Z"
  }
]
```

**Response Fields:**
- `file_exists` (boolean): Whether the file exists on disk (checked on each request)

**Notes:**
- Results ordered by `created_at DESC` (newest first)
- Includes account name in response for UI display
- Includes `file_exists` field indicating whether the file exists on disk (checked on each request)

#### `GET /api/v1/statements/{id}`

Get a single statement file by ID.

**Path Parameters:**
- `id` (UUID): Statement file ID

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "account_id": 1,
  "account_name": "My Checking Account",
  "original_filename": "statement_2024_01.csv",
  "stored_filename": "550e8400-e29b-41d4-a716-446655440000.csv",
  "stored_path": "/data/statements/550e8400-e29b-41d4-a716-446655440000.csv",
  "format": "csv",
  "size_bytes": 10240,
  "content_hash": "a1b2c3d4e5f6...",
  "row_count": 150,
  "columns": ["Date", "Description", "Amount"],
  "date_from": "2024-01-01",
  "date_to": "2024-01-31",
  "status": "uploaded",
  "is_ingested": false,
  "ingested_at": null,
  "file_exists": true,
  "created_at": "2025-12-26T10:00:00Z",
  "updated_at": "2025-12-26T10:00:00Z"
}
```

**Response Fields:**
- `file_exists` (boolean): Whether the file exists on disk (checked on each request)

**Error Responses:**
- `404 Not Found`: Statement not found

#### `DELETE /api/v1/statements/{id}`

Delete a statement file and its associated file on disk.

**Path Parameters:**
- `id` (UUID): Statement file ID

**Response (204 No Content):**
No response body.

**Behavior:**
- Deletes DB record
- Deletes file from disk (`/data/statements/{uuid}.csv`)
- Atomic operation: if file deletion fails, rollback DB deletion

**Error Responses:**
- `404 Not Found`: Statement not found
- `500 Internal Server Error`: File deletion failed

### Meta (v1)

#### `GET /api/v1/meta/accounts/options`

Get all static option data for Accounts UI. This endpoint provides account types, economic areas, and currencies. The UI must not hardcode these values.

**Response (200 OK):**
```json
{
  "account_types": [
    { "value": "checking", "label": "Checking" },
    { "value": "savings", "label": "Savings" },
    { "value": "credit_card", "label": "Credit Card" },
    { "value": "cash", "label": "Cash" },
    { "value": "investment", "label": "Investment" },
    { "value": "loan", "label": "Loan" }
  ],
  "economic_areas": [
    { "value": "eu", "label": "European Union" },
    { "value": "us", "label": "United States" },
    { "value": "uk", "label": "United Kingdom" },
    { "value": "cis", "label": "Commonwealth of Independent States" },
    { "value": "mena", "label": "Middle East and North Africa" },
    { "value": "apac", "label": "Asia-Pacific (excluding China)" },
    { "value": "china", "label": "China" },
    { "value": "other", "label": "Other regions" }
  ],
  "currencies": [
    { "code": "USD", "name": "US Dollar", "digits": 2 },
    { "code": "EUR", "name": "Euro", "digits": 2 },
    { "code": "GBP", "name": "British Pound Sterling", "digits": 2 },
    { "code": "JPY", "name": "Japanese Yen", "digits": 0 }
    // ... all ISO 4217 currencies
  ]
}
```

**Notes:**
- Currencies are sourced from the `iso4217` Python library
- All ISO 4217 currency codes are included
- `digits` field indicates decimal precision (exponent)

#### `POST /api/v1/meta/statements/infer-date-format`

Analyze a CSV file to detect date column and infer date format. Useful for validation before upload or troubleshooting date parsing issues.

**Request:**
- Content-Type: `multipart/form-data`
- Fields:
  - `file` (required): CSV file to analyze

**Response (200 OK):**
```json
{
  "date_column_detected": true,
  "date_column_name": "Date",
  "date_column_index": 0,
  "inferred_format": {
    "strptime_format": "%Y-%m-%d",
    "human_readable": "YYYY-MM-DD",
    "confidence": 0.95,
    "matches": 142,
    "total_tested": 150
  },
  "date_range": {
    "earliest": "2024-01-01",
    "latest": "2024-12-31"
  },
  "total_rows_analyzed": 150,
  "parsing_errors": 8,
  "sample_dates": ["2024-01-15", "2024-02-20", "2024-03-10"]
}
```

**Response Fields:**
- `date_column_detected` (boolean): Whether a date-like column was found
- `date_column_name` (string, nullable): Name of detected date column
- `date_column_index` (integer, nullable): Zero-based index of date column
- `inferred_format` (object, nullable): Format inferred by `dateinfer` library
  - `strptime_format` (string): Python `strptime` format string (e.g., `"%Y-%m-%d"`)
  - `human_readable` (string): Human-readable format name (e.g., `"YYYY-MM-DD"`)
  - `confidence` (float): Confidence score 0.0-1.0 (calculated as `matches / total_tested`)
  - `matches` (integer): Number of dates that successfully parse with this format
  - `total_tested` (integer): Total number of dates tested
- `date_range` (object, nullable): Earliest and latest dates found
- `total_rows_analyzed` (integer): Number of rows checked
- `parsing_errors` (integer): Number of rows that couldn't be parsed
- `sample_dates` (array): Sample date strings from the CSV (first 10)

**Error Responses:**
- `400 Bad Request`: Invalid file or not a CSV
- `422 Unprocessable Entity`: File is empty or unparseable

**Notes:**
- Uses `dateinfer` library for format inference
- Analyzes first 100 rows (or all rows if < 100) to collect sample date strings
- Uses `dateutil.parser` as fallback if `dateinfer` fails or confidence is too low

#### `GET /api/v1/meta/statements/date-formats`

Get list of all date formats supported by the system. Useful for UI dropdowns or documentation.

**Response (200 OK):**
```json
{
  "supported_formats": [
    {
      "format": "YYYY-MM-DD",
      "pattern": "%Y-%m-%d",
      "description": "ISO 8601 format (e.g., 2024-01-15)",
      "example": "2024-01-15"
    },
    {
      "format": "MM/DD/YYYY",
      "pattern": "%m/%d/%Y",
      "description": "US format (e.g., 01/15/2024)",
      "example": "01/15/2024"
    },
    {
      "format": "DD/MM/YYYY",
      "pattern": "%d/%m/%Y",
      "description": "European format (e.g., 15/01/2024)",
      "example": "15/01/2024"
    },
    {
      "format": "DD-MM-YYYY",
      "pattern": "%d-%m-%Y",
      "description": "European format with dashes (e.g., 15-01-2024)",
      "example": "15-01-2024"
    },
    {
      "format": "YYYY/MM/DD",
      "pattern": "%Y/%m/%d",
      "description": "ISO-like with slashes (e.g., 2024/01/15)",
      "example": "2024/01/15"
    }
  ]
}
```

**Response Fields:**
- `supported_formats` (array): List of supported date formats
  - `format` (string): Human-readable format name
  - `pattern` (string): Python strftime pattern
  - `description` (string): Format description
  - `example` (string): Example date in this format

**Notes:**
- This is a static list of formats the system can parse
- Used for UI documentation or format selection
- Actual parsing uses flexible `dateutil.parser` which handles more variations

### Transactions (v1)

#### `GET /api/v1/transactions`

List transactions with pagination, sorting, and filtering.

**Query Parameters:**
- `account_id` (integer, optional): Filter by account ID
- `statement_file_id` (UUID, optional): Filter by statement file ID
- `page` (integer, optional): Page number (1-based, default: 1)
- `page_size` (integer, optional): Items per page (default: 50, max: 100)
- `sort_by` (string, optional): Field to sort by (default: "inserted_at")
  - Regular fields: `inserted_at`, `row_id`, `statement_file_id`
  - Dynamic fields: `ingested_content.<field>` (e.g., `ingested_content.date`, `ingested_content.amount`)
  - **Type-aware sorting**: Dynamic fields are sorted using column metadata (numeric fields as numbers, date fields as dates, text fields as text)
- `sort_dir` (string, optional): Sort direction - `asc` or `desc` (default: "desc")
- `filters` (string, optional): Filter string (format: `field1:operator:value,field2:operator:value`)

**Filter Format:**
- Format: `field:operator:value`
- Multiple filters: comma-separated (AND logic)
- Supported operators: `=`, `!=`, `>`, `>=`, `<`, `<=`, `contains`, `empty`, `not_empty`
- Examples:
  - `ingested_content.date:>=:2024-01-01` - Date >= 2024-01-01
  - `ingested_content.amount:>:100` - Amount > 100
  - `ingested_content.description:contains:Coffee` - Description contains "Coffee"

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "row_id": 0,
      "statement_file": {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "original_filename": "statement.csv",
        "columns": ["Date", "Description", "Amount"]
      },
      "account": {
        "id": 1,
        "name": "My Checking Account",
        "institution": "Bank of Example",
        "currency": "USD",
        "type": "checking",
        "economic_area": "us",
        "datelock_from": "2023-01-01",
        "datelock_to": "2024-12-31"
      },
      "ingested_content": {
        "date": "2024-01-01",
        "amount": "-4.50",
        "description": "Coffee"
      },
      "computed_content": {},
      "inserted_at": "2025-12-26T10:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 50,
    "total": 150,
    "total_pages": 3
  }
}
```

#### `GET /api/v1/transactions/meta`

Get transaction column metadata for dynamic table UI.

**Query Parameters:**
- `account_id` (integer, optional): Filter by account ID (per-account metadata)

**Response (200 OK):**
```json
{
  "ingested_columns": [
    {
      "name": "date",
      "type": "date",
      "sample_values": ["2024-01-01", "2024-01-15", "2024-02-01"],
      "nullable": false,
      "min": "2024-01-01",
      "max": "2024-12-31"
    },
    {
      "name": "amount",
      "type": "number",
      "sample_values": ["-4.50", "100.00", "2500.00"],
      "nullable": false,
      "min": -1000.00,
      "max": 10000.00
    },
    {
      "name": "description",
      "type": "string",
      "sample_values": ["Coffee", "Salary", "Rent"],
      "nullable": true
    }
  ],
  "computed_columns": []
}
```

**Response Fields:**
- `ingested_columns` (array): Column metadata from `ingested_content` JSONB
  - `name` (string): Column name
  - `type` (string): Inferred type - `date`, `number`, or `string`
  - `sample_values` (array): Sample values (up to 10)
  - `nullable` (boolean): Whether column can be null
  - `min` (any, optional): Minimum value (for date/number types)
  - `max` (any, optional): Maximum value (for date/number types)
- `computed_columns` (array): Empty for now (out of scope)

**Notes:**
- Samples up to 200 transactions for metadata extraction
- Per-account aggregation (not global) - different banks have different columns
- Type inference: date > number > string (prioritized)

#### `DELETE /api/v1/transactions`

Delete transactions with optional account filter.

**Query Parameters:**
- `account_id` (integer, optional): Delete transactions for specific account only

**Response (200 OK):**
```json
{
  "deleted_count": 150
}
```

**Behavior:**
- If `account_id` provided: Deletes transactions for that account only
- If `account_id` not provided: Deletes all transactions (global delete)
- Sets `statement_files.is_ingested = false` for affected statements
- Does NOT delete statement files

**Error Responses:**
- `500 Internal Server Error`: Database error

### Statement Ingestion (v1)

#### `POST /api/v1/statements/{statement_id}/ingest`

Ingest a single statement file into transactions.

**Path Parameters:**
- `statement_id` (UUID): Statement file ID to ingest

**Response (200 OK):**
```json
{
  "statement_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "summary": {
    "total_rows": 1000,
    "ingested": 850,
    "skipped": 150,
    "errors": 0
  },
  "errors": []
}
```

**Response Fields:**
- `status` (string): `completed` | `partial` | `failed`
- `summary` (object): Ingestion summary
  - `total_rows` (integer): Total rows in statement
  - `ingested` (integer): Number of rows successfully ingested
  - `skipped` (integer): Number of rows skipped (duplicates or date lock)
  - `errors` (integer): Number of errors encountered
- `errors` (array): List of error details (if any)
  - `row_id` (integer): Row index that failed
  - `reason` (string): Error reason (`date_lock`, `parse_error`, etc.)
  - `message` (string): Error message

**Behavior:**
- Applies date lock rules (two-sided: `datelock_from` and `datelock_to`)
- Uses persisted `date_column` from statement (if present)
- Re-infers date format using `dateinfer` during ingestion
- Creates transactions (skips rows with existing `(statement_file_id, row_id)` - idempotent)
- Uses bulk insert for performance (batches of 1000, using `add_all()` for SQLAlchemy 2.0+)
- Collects errors but continues processing
- Sets `statement_files.is_ingested = true` if ingestion completed
- Updates `ingested_rows_count`, `ingestion_errors_count`, `ingested_at` on statement

**Error Responses:**
- `404 Not Found`: Statement file not found
- `500 Internal Server Error`: Database or file system error

#### `POST /api/v1/statements/ingest`

Bulk ingest multiple statement files.

**Request Body:**
```json
[
  "550e8400-e29b-41d4-a716-446655440000",
  "660e8400-e29b-41d4-a716-446655440001"
]
```

**Response (200 OK):**
```json
[
  {
    "statement_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "summary": {
      "total_rows": 1000,
      "ingested": 850,
      "skipped": 150,
      "errors": 0
    },
    "errors": []
  },
  {
    "statement_id": "660e8400-e29b-41d4-a716-446655440001",
    "status": "partial",
    "summary": {
      "total_rows": 500,
      "ingested": 450,
      "skipped": 0,
      "errors": 50
    },
    "errors": [
      {
        "row_id": 5,
        "reason": "parse_error",
        "message": "Failed to parse date: 'invalid-date'"
      }
    ]
  }
]
```

**Behavior:**
- Ingests all provided statement files (synchronous, one at a time)
- Returns list of `IngestionResponse` for each statement
- Each statement is processed independently

**Error Responses:**
- `404 Not Found`: Any statement file not found
- `500 Internal Server Error`: Database or file system error

## Future Endpoints

The following endpoints are planned but not yet implemented:

- Reporting endpoints
- File processing and validation endpoints

## Notes

- All endpoints return JSON responses
- Error responses follow FastAPI's standard error format and include `request_id` for correlation
- All endpoints are versioned under `/api/v1/...` prefix
- OpenAPI documentation is available at `/api/docs`
