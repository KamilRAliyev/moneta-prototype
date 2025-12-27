# MON-11: Transactions Ingestion + Transactions View

## Summary

This PR implements complete transaction ingestion and viewing functionality, allowing users to ingest CSV statement files into raw JSON transactions and view them in a dynamic table with sorting, filtering, and pagination.

## Status

✅ **Complete** - All acceptance criteria met, backend and frontend fully implemented

## What's Included

### Backend

- ✅ Transaction model with JSONB storage for dynamic content
- ✅ Transaction ingestion service with date lock support (two-sided: `datelock_from` and `datelock_to`)
- ✅ Bulk ingestion with idempotency (unique constraint on `statement_file_id + row_id`)
- ✅ Transaction hash calculation for change tracking
- ✅ List transactions API with pagination, sorting, and filtering
- ✅ Transaction metadata endpoint for dynamic column discovery
- ✅ Delete transactions endpoint with account filtering
- ✅ Comprehensive test coverage (33 tests: 8 model + 6 service + 12 edge cases + 7 API)

### Frontend

- ✅ Transactions view (`/transactions`) with dynamic table
- ✅ Column chooser with localStorage persistence (per account)
- ✅ Sorting on all columns (type-aware: numeric, date, text)
- ✅ Filtering with multiple operators (=, !=, >, >=, <, <=, contains, empty, not_empty)
- ✅ Pagination with page size selector
- ✅ Ingestion controls in statements table (per-row and bulk "Ingest All")
- ✅ Remove all transactions button with confirmation modal
- ✅ Status indicators showing ingestion progress

### Recent Bug Fixes

- ✅ **SQLAlchemy 2.0 compatibility**: Replaced deprecated `bulk_save_objects()` with `add_all()`
- ✅ **Transaction error handling**: Added proper rollback on database errors to prevent failed transaction state
- ✅ **Type-aware sorting**: Uses column metadata from `/meta` endpoint to properly sort numeric, date, and text fields

## Key Features

### Date Lock (Two-Sided)

- `datelock_from` and `datelock_to` mark date ranges that have already been ingested
- Transactions within the locked range are skipped (already ingested)
- Transactions outside the range are ingested (not yet ingested)
- Changing date locks does NOT delete existing transactions

### Idempotent Ingestion

- Re-ingesting the same statement file is safe
- Duplicate rows (same `statement_file_id` + `row_id`) are skipped, not updated
- Allows safe re-ingestion after changing date locks or fixing errors

### Dynamic Column Support

- Transactions stored as JSONB for flexibility
- Column metadata endpoint provides type information (number, date, string)
- UI dynamically renders columns based on ingested data
- Type-aware sorting ensures proper numeric and date sorting

## API Endpoints

- `POST /api/v1/statements/{statement_id}/ingest` - Ingest single statement
- `POST /api/v1/statements/ingest` - Bulk ingest multiple statements
- `GET /api/v1/transactions` - List transactions with pagination, sorting, filtering
- `GET /api/v1/transactions/meta` - Get column metadata for dynamic UI
- `DELETE /api/v1/transactions` - Delete transactions (with optional account filter)

## Testing

- ✅ 33 backend tests passing
- ✅ All edge cases covered (date lock variations, parsing failures, filtering, sorting, pagination)
- ✅ Frontend components tested

## Documentation

- ✅ Updated MON-11 issue document (marked complete)
- ✅ Updated Kanban Board (moved to Done)
- ✅ Updated Weekly Notes
- ✅ Updated Architecture docs (API Endpoints, Database)
- ✅ Added implementation notes about bug fixes

## Migration Notes

- Requires migration: `af4e2044a3bb_create_transactions_table.py`
- Requires migration: `8ea4075a28e2_add_datelock_to_to_accounts.py`
- Requires migration: `be9c3b99c92e_add_statementfile_extensions_ingested_.py`

## Out of Scope (Intentionally)

- ❌ Computed/enriched transactions logic
- ❌ Categorization
- ❌ Analytics/balances
- ❌ Metrics/charts

## Breaking Changes

None - this is a new feature addition.

## Checklist

- [x] All acceptance criteria met
- [x] Backend tests passing (33 tests)
- [x] Frontend components implemented and working
- [x] Documentation updated
- [x] SQLAlchemy 2.0 compatibility verified
- [x] Type-aware sorting working correctly
- [x] Error handling robust

## Related Issues

- Closes MON-11
- Depends on MON-9 (Accounts backend + UI)
- Depends on MON-10 (Statement Upload + List UI)
