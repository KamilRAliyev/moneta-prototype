# MON-9: Accounts Backend + UI (Vue + Tailwind)

## Progress Summary

**Status:** ✅ Completed
**Completed:** Backend model, database migration, API endpoints, and Frontend UI
**Next:** Ready for production use

- ✅ **Backend Model** - Account model with enums and migration created
- ✅ **Backend API** - CRUD endpoints and meta options endpoint completed
- ✅ **Frontend UI** - Vue components and pages completed

---

## User Story

**As a user**,
I want to manage accounts visually,
So that I can configure ingestion behavior per account.

---

## Acceptance Criteria

### ✅ Backend Model (Completed)

- [x] Account model created with all required fields
- [x] AccountType enum: checking, savings, credit_card, cash, investment, loan
- [x] Currency enum using ISO 4217 library (`iso4217`) with all currency codes
- [x] EconomicArea enum: eu, us, uk, cis, mena, apac, china, other
- [x] Database migration created and ready to apply
- [x] Model includes timestamps (created_at, updated_at)

### ✅ Backend API (Completed)

- [x] Accounts CRUD endpoints implemented
  - [x] `GET /api/v1/accounts` - List all accounts
  - [x] `POST /api/v1/accounts` - Create new account
  - [x] `GET /api/v1/accounts/{id}` - Get account details
  - [x] `PUT /api/v1/accounts/{id}` - Update account
  - [x] `DELETE /api/v1/accounts/{id}` - Delete account
- [x] Meta options endpoint: `GET /api/v1/meta/accounts/options`
  - [x] Returns account_types with value and label
  - [x] Returns economic_areas with value and label
  - [x] Returns currencies with code, name, and digits
- [x] Pydantic schemas for request/response validation
- [x] Service layer with business logic (AccountService, MetaService)
- [x] Comprehensive error handling with custom exceptions
- [x] Database error handling with rollback support

### ✅ Frontend UI (Completed)

- [x] Accounts list page available at `/accounts`
  - [x] Display accounts in table layout
  - [x] Show: Name, Institution, Currency, Type, Economic Area, Date Lock
  - [x] Date Lock display format (if set: "Locked before: YYYY-MM-DD", else: "No date lock")
  - [x] Actions: Create, View, Edit, Delete buttons
  - [x] Clicking row navigates to `/accounts/:id`
  - [x] Delete confirmation modal
- [x] Account detail page at `/accounts/:id`
  - [x] Display all account fields
  - [x] Editable form for all fields including date lock
  - [x] Date picker for `datelock_from`
  - [x] Help text for date lock explanation
  - [x] Save/Cancel buttons
- [x] Create account page at `/accounts/new`
  - [x] Form with all required fields
  - [x] Dropdowns populated from `/api/v1/meta/accounts/options`
  - [x] Client-side validation
  - [x] Error handling and display
- [x] TypeScript types for all Account DTOs
- [x] Accounts service with CRUD operations
- [x] Meta options composable with caching
- [x] Reusable components (AccountForm, AccountTable, DateLockField)
- [x] Navigation link in AppShell
- [x] Loading states and error handling

### Account Fields

| Field | Type | Required | Description | Status |
|-------|------|----------|-------------|--------|
| `name` | string | Yes | Account name | ✅ Model defined |
| `institution` | string | Yes | Financial institution name | ✅ Model defined |
| `currency` | enum (ISO 4217) | Yes | Currency code (e.g., USD, EUR) | ✅ Model defined |
| `account_type` | enum | Yes | Account type (checking, savings, etc.) | ✅ Model defined |
| `economic_area` | enum | No | Economic region classification | ✅ Model defined |
| `datelock_from` | date | No | Date lock for ingestion (nullable) | ✅ Model defined |

### Date Lock Behavior

**Date Lock (`datelock_from`)** is a per-account ingestion guardrail that defines the earliest date from which transactions/statements are allowed to be ingested or re-processed.

**Rules:**
- Transactions **before** `datelock_from`: ❌ must NOT be ingested, overwritten, or re-parsed
- Transactions **on or after** `datelock_from`: ✅ ingestion and reprocessing allowed
- Changing `datelock_from` affects **future ingestion only** (does not retroactively delete data)
- `null` value means no lock (full historical ingestion allowed)

**Purpose:**
- Prevent accidental re-imports of historical data
- Lock down reconciled or audited periods
- Allow partial re-ingestion without duplicating history
- Support "cutover" moments when switching data sources

**Non-Goals:**
- Does NOT delete existing transactions
- Does NOT freeze balances
- Does NOT affect reporting or analytics
- Does NOT act as a permissions or security mechanism

---

## Backend Requirements

### Database Model

**Table:** `accounts`

```python
class Account(Base):
    id: int (primary key)
    name: str (required, max 255)
    institution: str (required, max 255)
    currency: Currency enum (required, ISO 4217)
    account_type: AccountType enum (required)
    economic_area: EconomicArea enum (nullable)
    datelock_from: date (nullable)
    created_at: datetime (auto)
    updated_at: datetime (auto)
```

**Enums:**
- `AccountType`: checking, savings, credit_card, cash, investment, loan
- `EconomicArea`: eu, us, uk, cis, mena, apac, china, other
- `Currency`: ISO 4217 codes (using `iso4217` library)

### API Endpoints

#### Accounts CRUD

- `GET /api/v1/accounts` - List all accounts
- `POST /api/v1/accounts` - Create new account
- `GET /api/v1/accounts/{id}` - Get account details
- `PUT /api/v1/accounts/{id}` - Update account
- `DELETE /api/v1/accounts/{id}` - Delete account

#### Meta Options Endpoint

**Endpoint:** `GET /api/v1/meta/accounts/options`

**Purpose:** Provides all static option data required by the Accounts UI. UI must not hardcode enum values or currency lists.

**Response Schema:**
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
    { "code": "GBP", "name": "British Pound Sterling", "digits": 2 }
    // ... all ISO 4217 currencies
  ]
}
```

---

## Frontend Requirements

### Pages

1. **Accounts List (`/accounts`)**
   - Display accounts in table or card layout
   - Columns/fields: Name, Institution, Currency, Type, Economic Area, Date Lock
   - Date Lock display:
     - If set: "Locked before: YYYY-MM-DD"
     - If not set: "No date lock"
   - Actions: Create, View, Edit, Delete
   - Clicking row navigates to `/accounts/:id`

2. **Account Detail (`/accounts/:id`)**
   - Display all account fields
   - Editable form for all fields including date lock
   - Date picker for `datelock_from`
   - Help text for date lock:
     > **Date Lock:** Transactions before this date will not be ingested or reprocessed for this account.
   - Save/Cancel buttons

3. **Create Account (`/accounts/new`)**
   - Form with all required fields
   - Dropdowns populated from `/api/v1/meta/accounts/options`
   - Validation and error handling

### UI Guidelines

- Use Tailwind CSS for layout and spacing
- Simple table or card layout is sufficient
- All dropdowns must be populated via `/api/v1/meta/accounts/options`
- No hardcoded enum values or currency lists in frontend
- Responsive design for mobile/desktop

### Components Structure

```
src/
├── views/
│   ├── AccountsList.vue
│   └── AccountDetail.vue
├── components/
│   └── accounts/
│       ├── AccountForm.vue
│       ├── AccountTable.vue
│       └── DateLockField.vue
└── services/
    └── accounts.ts (API client)
```

---

## Example Scenarios

### Scenario 1: No Date Lock
```
datelock_from = null
→ Full historical ingestion allowed
```

### Scenario 2: Date Lock Set
```
datelock_from = 2023-01-01
→ ❌ Transactions dated 2022-12-31: blocked
→ ✅ Transactions dated 2023-01-01: allowed
```

---

## Out of Scope

- Statement upload
- Transaction ingestion
- Deduplication logic
- Metrics or charts
- Account balance tracking
- Transaction history display

---

## Implementation Status

### ✅ Backend Model (Completed)
- [x] Account model created with SQLAlchemy
- [x] Enums implemented: AccountType, Currency (ISO 4217), EconomicArea
- [x] Using `iso4217` library for currency codes with helper methods
- [x] Database migration created (`60f2323257db_add_accounts_table.py`)
- [x] Model exported in `server/models/__init__.py`
- [x] Model imported in `migrations/env.py` for Alembic detection
- [x] Database URL fixed to use `postgresql+psycopg://` for Alembic compatibility

### ✅ Backend API (Completed)
- [x] API router created: `server/api/routers/v1/accounts.py`
- [x] CRUD operations implemented with proper validation
- [x] Meta options endpoint created: `server/api/routers/v1/meta.py`
- [x] Request/response schemas (Pydantic models) added
- [x] Service layer with class-based services (AccountService, MetaService)
- [x] Comprehensive error handling with custom exceptions
- [x] Database error handling with automatic rollback
- [x] Error handler decorator for consistent error responses
- [x] All endpoints registered in main.py
- [x] Write API tests (completed - see `tests/test_account_model.py` and `tests/test_accounts.py`)

### ✅ Frontend (Completed)
- [x] Create Vue components structure
- [x] Implement API service (`services/accounts.ts`)
- [x] Create views: AccountsList, AccountCreate, AccountDetail
- [x] Create components: AccountForm, AccountTable, DateLockField
- [x] Add routing configuration
- [x] Implement form validation
- [x] Add loading states and error handling
- [x] Cache meta options to reduce API calls (composable: `useAccountMeta.ts`)
- [x] Use TypeScript for type safety
- [x] Fix CSS styling issues (removed gray backgrounds, full-width layout)
- [x] Write frontend tests (completed - 84 tests passing)

### ✅ Testing (Completed)
- [x] Backend tests: 58 tests passing
  - [x] Account model tests (`test_account_model.py`)
  - [x] Accounts API tests (`test_accounts.py`)
- [x] Frontend tests: 84 tests passing
  - [x] Accounts service tests (`services/__tests__/accounts.spec.ts`)
  - [x] Meta composable tests (`composables/__tests__/useAccountMeta.spec.ts`)
  - [x] Component tests (AccountForm, AccountTable, DateLockField)
  - [x] View tests (AccountsList, AccountCreate, AccountDetail)

---

## One-Line Summary

> **Accounts UI consumes all enums and currency options from `/api/v1/meta/accounts/options`; no values are hardcoded in the frontend.**
