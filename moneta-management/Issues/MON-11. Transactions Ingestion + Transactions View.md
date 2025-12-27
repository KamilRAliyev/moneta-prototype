---

## **User Story — Ingestion**

**As a user**, I want to ingest transactions from uploaded statement files, so that raw transaction data becomes available for review and later computation.

---

## **User Story — Transactions View**

**As a user**, I want to view ingested transactions in a table with sorting, filtering, and pagination, so that I can inspect and work with transaction data regardless of statement structure.

---

## **Scope**

✅ Ingest CSV rows as raw transactions
✅ Store transactions in a generic JSON-based structure
✅ Transactions table UI with pagination, sorting, filtering
✅ Re-ingestion support
❌ Computed/enriched transactions logic
❌ Categorization, analytics, balances

---

## **Acceptance Criteria**

### **1) Statements → Ingestion Controls (UI)**

#### **Statement Table Actions**

In the **Statements table**, each row must have:

- **Ingest button**
  - Visible only if `is_ingested = false`
  - Disabled if ingestion is already in progress (future-proof)
- **Status indicator**
  - Uploaded / Ingested

#### **Global Actions**

At the top of the statements table:

- **"Ingest all" button**
  - Ingests all non-ingested statements in the current filter scope

---

### **2) Re-ingestion Controls**

**As a user**, I want to remove all ingested transactions and reset statement ingestion state, so that I can re-ingest data after changing date locks or logic.

#### **UI**

- Button at top of Transactions view: **"Remove all transactions"**
- Confirmation modal required

#### **Behavior**

- Deletes transactions **respecting account filter** (safer approach)
- Sets `statement_files.is_ingested = false` for affected statements
- Does NOT delete statement files

**API:**
- `DELETE /api/v1/transactions?account_id=...` (account_id recommended for safety)
- If account_id provided: deletes transactions for that account only
- If account_id not provided: requires explicit confirmation (global delete)

---

### **3) Date Lock (Extended)**

#### **Requirement**

Date lock must support **two-sided locking** to mark dates that have **already been ingested**:

- `datelock_from` → marks dates >= this date as already ingested
- `datelock_to` → marks dates <= this date as already ingested

#### **Behavior**

- Transactions **within** `[datelock_from, datelock_to]` (inclusive range): ❌ **skipped** (already ingested)
- Transactions **outside** this range: ✅ **ingested** (not yet ingested)
- Range validation: `datelock_from <= datelock_to` (if both set)
- If `datelock_from = datelock_to`, only that exact date is marked as already ingested

#### **Notes**

- Either field may be null
- If `datelock_from` is null → no lower bound (ingest all dates <= datelock_to)
- If `datelock_to` is null → no upper bound (ingest all dates >= datelock_from)
- If both null → no date lock (ingest all transactions)
- **Example:** If you've ingested Feb 1-28, 2025, set `datelock_from = 2025-02-01` and `datelock_to = 2025-02-28`. This means:
  - Feb 1-28 transactions → skipped (already ingested)
  - Jan 2024 or March 2025 transactions → ingested (not yet ingested)
- Changing date lock:
  - does NOT delete transactions
  - affects next ingestion run only

**Required Changes:**
- Account model currently only has `datelock_from`. Must add `datelock_to` column.
- **Migration Strategy:** Add `datelock_to` in a **separate migration before transactions ingestion** (MON-11a or subtask)
- **Validation:** Validate in account update endpoint (Pydantic) that `datelock_from <= datelock_to` if both set → 400 error

---

### **4) Database Model — Transactions**

**Table:** `transactions`

> DB should be normalized; JSON is allowed only where structure is truly dynamic.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| account_id | FK | Yes | Redundant but intentional |
| statement_file_id | FK | Yes | Source statement |
| row_id | int | Yes | Row index in statement |
| ingested_content | JSONB | Yes | Raw row data as-is |
| transaction_hash | string | Yes | SHA-256 hash of (row_id + normalized JSON of ingested_content) |
| computed_content | JSONB | No | Empty for now |
| computed_content_hash | string | No | Hash of (row_id + computed_content) |
| inserted_at | datetime | Yes | Ingestion time |
| updated_at | datetime | Yes | Updated time |
| computed_at | datetime | No | Null (out of scope) |

#### **Constraints**

- Unique: `(statement_file_id, row_id)`
- Indexes:
  - `(account_id, inserted_at DESC)`
  - `(statement_file_id)`
  - `(transaction_hash)` - for change tracking

#### **Transaction Hash Calculation**

```python
import hashlib
import json

def calculate_transaction_hash(row_id: int, ingested_content: dict) -> str:
    """Calculate SHA-256 hash for change tracking."""
    # Normalize content by sorting keys
    normalized_content = json.dumps(ingested_content, sort_keys=True)
    hash_input = f"{row_id}:{normalized_content}"
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
```

**Purpose:**
- **Change tracking / diagnostics:** Detect if transaction content changed between ingestion runs
- **Future "diff" logic:** Compare hashes to see what changed
- **NOT used for duplicate detection** - that's handled by unique constraint `(statement_file_id, row_id)`
- Stored in DB for indexed lookup performance

---

### **5) API — Ingestion** ✅

#### **Ingest Single Statement** ✅

```
POST /api/v1/statements/{statement_id}/ingest
```

**Behavior:**
- Applies date lock rules (two-sided: datelock_from and datelock_to) - skips transactions within the locked range (already ingested), ingests transactions outside the range
- Uses persisted `date_column` from statement (if present)
- Re-infers date format using `dateinfer` during ingestion
- Creates transactions (skips rows with existing `(statement_file_id, row_id)` - idempotent via unique constraint)
- Uses bulk insert for performance (batches of 1000)
- Collects errors but continues processing
- Sets `statement_files.is_ingested = true` if ingestion completed (even if 0 rows ingested)
- Updates `ingested_rows_count`, `ingestion_errors_count`, `ingested_at` on statement

**Response:**
```json
{
  "statement_id": "uuid",
  "status": "completed" | "partial" | "failed",
  "summary": {
    "total_rows": 1000,
    "ingested": 850,
    "skipped": 150,
    "errors": 0
  },
  "errors": [
    {
      "row_id": 5,
      "reason": "date_lock",
      "message": "Transaction date 2022-12-01 is before datelock_from 2023-01-01"
    },
    {
      "row_id": 42,
      "reason": "parse_error",
      "message": "Failed to parse date: 'invalid-date'"
    }
  ]
}
```

#### **Ingest All** ✅

```
POST /api/v1/statements/ingest
```

- Body: `List[uuid.UUID]` - List of statement file IDs to ingest
- Ingests all provided statements (synchronous, one statement at a time)
- Returns list of `IngestionResponse` for each statement

---

### **6) API — Transactions** ✅

#### **List Transactions** ✅

```
GET /api/v1/transactions
```

**Query params:**

- `account_id` (optional) - Filter by account
- `statement_file_id` (optional) - Filter by statement file
- `page` (default: 1) - Page number
- `page_size` (default: 50) - Items per page
- `sort_by` (default: "inserted_at") - Field to sort by
  - Regular fields: `inserted_at`, `row_id`, `statement_file_id`
  - Dynamic fields: `ingested_content.date`, `ingested_content.amount`, etc.
- `sort_dir` (default: "desc") - Sort direction: `asc` or `desc`
- `filters` (optional) - Filter string with operators

**Filter Format:**
```
filters=field1:operator:value,field2:operator:value
```

**Supported Operators:**
- `=` - Equal
- `!=` or `not_equal` - Not equal
- `>` - Greater than
- `>=` - Greater than or equal
- `<` - Less than
- `<=` - Less than or equal
- `contains` - String contains (for string fields)
- `empty` - Field is empty/null
- `not_empty` - Field is not empty/null

**Filter Examples:**
- `filters=ingested_content.date:>=:2023-01-01` - Date >= 2023-01-01
- `filters=ingested_content.amount:>:100` - Amount > 100
- `filters=ingested_content.description:contains:Coffee` - Description contains "Coffee"
- `filters=ingested_content.description:empty:` - Description is empty
- `filters=account_id:=:1,ingested_content.date:>=:2023-01-01` - Multiple filters (AND logic)

---

### **7) Transactions API Response Shape**

#### **Transaction Response**

```json
{
  "id": "uuid",
  "row_id": 12,
  "statement_file": {
    "id": "uuid",
    "original_filename": "statement.csv",
    "columns": ["date", "amount", "description"]
  },
  "account": {
    "id": 1,
    "name": "Checking",
    "institution": "Bank of America",
    "currency": "USD",
    "type": "checking",
    "economic_area": "us",
    "datelock_from": "2023-01-01",
    "datelock_to": "2024-12-31"
  },
  "ingested_content": {
    "date": "2023-01-01",
    "amount": "-4.50",
    "description": "Coffee"
  },
  "computed_content": {},
  "inserted_at": "2024-01-01T10:00:00Z"
}
```

> ⚠️ `statement_file` and `account` are **NOT JSON in DB** — only composed in API response. Account includes all fields for frontend display without additional API calls.

---

### **8) Transactions View (UI)**

#### **Route**

```
/transactions
```

#### **Table Requirements**

- **Pagination** - Page number and page size selector
- **Column chooser:**
  - Checkbox UI to show/hide columns
  - Ingested fields (from meta endpoint)
  - Computed fields (disabled / empty for now)
  - Persist selected columns in localStorage
  - Default: show all ingested columns
- **Sorting:**
  - Clickable column headers
  - Sort by any ingested_content field
  - Default: `inserted_at DESC` (newest first)
- **Filtering:**
  - Filter UI with operator dropdown (contains, equal, >, >=, <, <=, empty, not_empty)
  - Field autocomplete from meta endpoint
  - Show active filters as chips with remove button
  - Filter on any ingested_content field based on type (string/number/date)

#### **Meta Endpoint** ✅

```
GET /api/v1/transactions/meta?account_id=...
```

**Purpose:** Provides column metadata for dynamic table UI (column chooser, filtering, sorting)

**Returns:**
```json
{
  "ingested_columns": [
    {
      "name": "date",
      "type": "date",
      "sample_values": ["2023-01-01", "2023-01-15", "2023-02-01"],
      "nullable": false,
      "min": "2023-01-01",
      "max": "2023-12-31"
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

**Implementation:**
- **Per-account aggregation** (not global) - `GET /api/v1/transactions/meta?account_id=...`
- Reason: Different banks have different columns; global meta becomes noisy
- Samples N transactions (e.g., 200) rather than scanning entire table
- Extracts unique column names from `ingested_content` JSONB
- Infers field types (date/number/string) from sample values
- Calculates min/max for date/number types (for filter UI)
- Returns empty array for `computed_columns` (out of scope)
- Future: allow `statement_file_id` override for statement-specific meta

---

### **9) Tests**

#### **Backend** ✅

- ✅ Transaction model tests (8 tests: creation, fields, timestamps, constraints, cascades, unique constraint, queries)
- ✅ Transaction service tests (6 tests: ingestion, date lock, idempotency, list, meta, delete)
- ✅ Transaction service edge cases (12 tests: date lock variations, date parsing failures, filtering, sorting, pagination, empty metadata, delete edge cases)
- ✅ Transaction API endpoint tests (7 tests: list with pagination/filtering, meta, delete, ingestion endpoints)
- ✅ **Total: 33 tests passing**

#### **Frontend** ✅

- ✅ Ingest button behavior (per row, visible when is_ingested = false)
- ✅ Ingest all flow (button at top, processes all non-ingested statements)
- ✅ Transactions table renders dynamic columns (based on visible columns from meta)
- ✅ Pagination + sorting (clickable headers, page size selector)
- ✅ Filtering UI (account dropdown, filter builder with operators)
- ✅ Column chooser with localStorage persistence (per account)
- ✅ Remove all transactions button with confirmation modal

---

## **Out of Scope**

- Computed/enriched logic
- Categorization
- Balance calculations
- Metrics/charts

---

## **Implementation Decisions**

### **1. Partial Ingestion** ✅

**Decision:** Mark statement as `is_ingested = true` if ingestion **completed successfully** (even if 0 rows ingested due to date lock)

**Rationale:**
- Prevents statements from remaining "not ingested" forever after an attempted ingestion that produced 0 rows
- Allows re-ingestion to pick up previously blocked rows if date lock changes later
- Track ingestion details with: `ingested_rows_count`, `ingestion_errors_count`, `ingested_at`

**Required Changes to StatementFile Model:**
- Add `ingested_rows_count` (int, default 0)
- Add `ingestion_errors_count` (int, default 0)
- Add `ingested_at` (datetime, nullable)
- Keep existing `is_ingested` boolean

**UI Display:**
- "Ingested (850/1000)" - shows progress
- "Ingested (0/1000) – blocked by date lock" - explains why
- "Partial (850/1000) – 10 errors" - shows errors

---

### **2. Ingestion Idempotency** ✅

**Decision:** Use unique constraint `(statement_file_id, row_id)` as the idempotency mechanism. `transaction_hash` is stored for diagnostics/change tracking, not for uniqueness.

**Implementation:**
- Unique constraint `(statement_file_id, row_id)` prevents duplicates
- Before inserting, check if `(statement_file_id, row_id)` exists
- If exists → skip row (no update, no error) - idempotent
- If not exists → insert new transaction
- `transaction_hash` is still calculated and stored for:
  - Diagnostics/debugging
  - Future "diff" logic to detect content changes
  - Change tracking (but not used for duplicate prevention)

---

### **3. Date Detection & Parsing** ✅

**Decision:**
- Persist detected date column per statement for deterministic ingestion
- Use persisted `date_column` during ingestion (if present)
- Re-infer date format using `dateinfer` during ingestion (more robust)
- If date parsing fails for a row → skip row and log error

**Required Changes to StatementFile Model:**
- Add `date_column` (string, nullable) - stores detected date column name

**Date Column Detection:**
- During upload metadata extraction: detect date column → store in `date_column`
- Uses hardcoded names: `["Date", "Transaction Date", "Posted Date", "date", "transaction_date"]`
- During ingestion: use `statement.date_column` if present
- If `date_column` is null → ingest all rows (no date lock applied), log warning
- This avoids "metadata inferred 'Date', ingestion inferred 'Posted Date'" inconsistencies

---

### **4. Error Handling** ✅

**Decision:** Collect errors, log them, continue processing, return summary with option to continue/ignore

**Behavior:**
- Continue processing all rows even if some fail
- Collect errors per row with reason (date_lock, parse_error, validation_error)
- Log all errors to structured logger
- Return response with error summary
- Frontend can display errors and ask user to continue or review

---

### **5. Performance / Large Statements** ✅

**Decision:** Synchronous at statement level (process one statement at a time, but can queue multiple)

**Implementation:**
- Synchronous processing (simpler for v1)
- Use bulk insert (`bulk_insert_mappings`) in batches of 1000 rows
- Commit after each batch (allows partial progress if error)
- Log progress: "Processing row 5000 of 10000..."
- If timeout occurs, return partial results with status "partial"

**Future (v2):** Background job queue if needed for very large statements (>100k rows)

---

### **6. Remove All Transactions** ✅

**Decision:** Remove transactions **respecting account filter** (safer approach)

**Behavior:**
- UI has Account filter dropdown in Transactions view
- "Remove all transactions" respects current `account_id` filter
- If no account selected, button text becomes "Remove ALL transactions (global)" and requires extra confirmation
- Deletes transactions for filtered account(s)
- Sets `statement_files.is_ingested = false` for affected statements
- Does NOT delete statement files
- Requires confirmation modal in UI

---

### **7. Date Lock Range** ✅

**Decision:** Date lock marks dates that have **already been ingested**. Transactions within the range are skipped, transactions outside are ingested.

**Logic:**
- If transaction is within `[datelock_from, datelock_to]` (inclusive): ❌ **skip** (already ingested)
- If transaction is outside the range: ✅ **ingest** (not yet ingested)
- Condition: `transaction_date >= datelock_from AND transaction_date <= datelock_to` → skip

**Edge Cases:**
- If `datelock_from = datelock_to` → only that exact date is marked as already ingested
- If `datelock_from > datelock_to` → validation error (invalid range)
- If `datelock_from` is null → no lower bound (ingest all dates <= datelock_to)
- If `datelock_to` is null → no upper bound (ingest all dates >= datelock_from)
- If both null → no date lock (ingest all transactions)

---

### **8. Account Details in Response** ✅

**Decision:** Include **all account fields** in transaction response

**Rationale:** Allows frontend to display account details without additional API calls.

---

### **9. Filtering** ✅

**Decision:** Full operator support: `contains`, `equal`, `not_equal`, `empty`, `not_empty`, `>`, `>=`, `<`, `<=`, `=`

**Format:** `filters=field1:operator:value,field2:operator:value` (AND logic)

---

### **10. Sorting** ✅

**Decision:** Support sorting by **all content fields** (ingested_content.*)

**Default:** `inserted_at DESC` (newest first)

**Implementation:** Use JSONB extraction for dynamic fields: `ingested_content->>'date'::date`

---

### **11. Column Chooser** ✅

**Decision:** Checkbox UI with localStorage persistence

**Implementation:**
- Show all ingested columns by default
- "Column Settings" button opens modal with checkboxes
- Persist selected columns in localStorage
- Show column count badge: "Showing 5 of 12 columns"

---

## **Additional Implementation Notes**

### **StatementFile Model Extensions**

Add to `statement_files` table:
- `ingested_rows_count` (int, default 0) - Number of rows successfully ingested
- `ingestion_errors_count` (int, default 0) - Number of errors encountered
- `ingested_at` (datetime, nullable) - Timestamp when ingestion completed
- `date_column` (string, nullable) - Detected date column name (for deterministic ingestion)

**Rationale:**
- Tracks ingestion progress and errors for better UX
- Persists date column to avoid inconsistencies between metadata extraction and ingestion
- Allows UI to show meaningful status: "Ingested (850/1000) – 10 errors"

---

### **Migration Sequencing**

1. **MON-11a (or subtask):** Add `datelock_to` to Account model ✅
   - ✅ Separate migration before transactions work
   - ✅ Update account schemas, forms, validation
   - ✅ Test date lock UI changes

2. **MON-11b:** Add StatementFile extensions ✅
   - ✅ Add `ingested_rows_count`, `ingestion_errors_count`, `ingested_at`, `date_column`
   - ✅ Migration completed

3. **MON-11c:** Create transactions table + ingestion logic ✅ (Complete)
   - ✅ Transaction model + migration
   - ✅ Transaction hash calculation utility
   - ✅ Ingestion service (with date lock, hash calculation, bulk insert)
   - ✅ Transaction service (list, meta, delete methods)
   - ✅ Transaction schemas (response, list, meta, ingestion)
   - ✅ API endpoints (list, meta, delete, ingestion)
   - ✅ Comprehensive tests (33 tests: 8 model + 6 service + 12 edge cases + 7 API)
   - ✅ Frontend integration (complete)
   - ✅ Bug fixes: SQLAlchemy 2.0 compatibility (bulk_save_objects → add_all), transaction error handling, type-aware sorting

---

### **Open Decisions**

- **DELETE /transactions:** ✅ Implemented with optional `account_id` parameter
  - If `account_id` provided: deletes transactions for that account only
  - If `account_id` not provided: allows global delete (requires confirmation in UI)
  - Implementation matches acceptance criteria

---

## **One-Line Summary**

> **User can ingest statement files into raw JSON transactions, view them in a dynamic table, and re-ingest safely after changing date locks.**
