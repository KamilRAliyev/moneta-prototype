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

## Future Endpoints

The following endpoints are planned but not yet implemented:

- Reporting endpoints
- File processing and validation endpoints

## Notes

- All endpoints return JSON responses
- Error responses follow FastAPI's standard error format and include `request_id` for correlation
- All endpoints are versioned under `/api/v1/...` prefix
- OpenAPI documentation is available at `/api/docs`
