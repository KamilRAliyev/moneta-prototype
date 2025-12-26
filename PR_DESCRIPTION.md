# MON-9: Accounts Backend + UI Implementation

## Summary

This PR implements the complete Accounts feature for the Moneta application, including backend API endpoints, database model, and frontend UI with Vue 3 + Tailwind CSS. The feature allows users to manage financial accounts with support for currency codes (ISO 4217), account types, economic areas, and date-based ingestion locks.

## 🎯 What's Changed

### Backend
- ✅ Account SQLAlchemy model with enums (AccountType, Currency, EconomicArea)
- ✅ Database migration for accounts table
- ✅ CRUD API endpoints (`/api/v1/accounts`)
- ✅ Meta options endpoint (`/api/v1/meta/accounts/options`)
- ✅ Service layer with business logic (AccountService, MetaService)
- ✅ Comprehensive error handling with custom exceptions
- ✅ Pydantic schemas for request/response validation
- ✅ Full test coverage (58 tests passing)

### Frontend
- ✅ TypeScript types for all Account DTOs
- ✅ Accounts service with CRUD operations
- ✅ Meta options composable with in-memory caching
- ✅ Three views: AccountsList, AccountCreate, AccountDetail
- ✅ Three reusable components: AccountForm, AccountTable, DateLockField
- ✅ Router configuration with Accounts routes
- ✅ Navigation link in AppShell
- ✅ Full test coverage (84 tests passing)

### Documentation
- ✅ Updated API Endpoints documentation
- ✅ Updated Database architecture documentation
- ✅ Updated Backend Package Structure
- ✅ Updated Frontend Package Structure
- ✅ Updated Testing documentation (backend and frontend)
- ✅ Updated MON-9 issue document

## 📋 Detailed Changes

### Backend Changes

#### Database Model
- **File**: `backend/server/models/account.py`
- Account model with fields: `id`, `name`, `institution`, `currency`, `type`, `economic_area`, `datelock_from`, `created_at`, `updated_at`
- Three enums:
  - `AccountType`: checking, savings, credit_card, cash, investment, loan
  - `Currency`: All ISO 4217 currency codes (using `iso4217` library)
  - `EconomicArea`: eu, us, uk, cis, mena, apac, china, other
- Migration: `60f2323257db_add_accounts_table.py`

#### API Endpoints
- **File**: `backend/server/api/routers/v1/accounts.py`
- `GET /api/v1/accounts` - List accounts (with pagination)
- `GET /api/v1/accounts/{id}` - Get account by ID
- `POST /api/v1/accounts` - Create account
- `PUT /api/v1/accounts/{id}` - Update account
- `DELETE /api/v1/accounts/{id}` - Delete account

#### Meta Options Endpoint
- **File**: `backend/server/api/routers/v1/meta.py`
- `GET /api/v1/meta/accounts/options` - Returns account types, economic areas, and currencies
- All dropdown options come from this endpoint (no hardcoded values in frontend)

#### Service Layer
- **File**: `backend/server/services/account.py`
- `AccountService` class with business logic for all CRUD operations
- Enum validation methods
- Database error handling with rollback

- **File**: `backend/server/services/meta.py`
- `MetaService` class for static option data

- **File**: `backend/server/services/exceptions.py`
- Custom exception hierarchy for service errors

#### Error Handling
- **File**: `backend/server/api/routers/v1/error_handlers.py`
- `@handle_service_errors` decorator for consistent error responses
- Maps service exceptions to appropriate HTTP status codes

#### Schemas
- **File**: `backend/server/api/schemas/account.py`
- Pydantic V2 schemas: `AccountBase`, `AccountCreate`, `AccountUpdate`, `AccountResponse`
- Meta option schemas: `AccountTypeOption`, `EconomicAreaOption`, `CurrencyOption`, `MetaOptionsResponse`
- Proper field aliasing for `account_type` ↔ `type` mapping

#### Tests
- **Files**:
  - `backend/tests/test_account_model.py` (8 tests)
  - `backend/tests/test_accounts.py` (16 tests)
- All 58 backend tests passing

### Frontend Changes

#### Types
- **File**: `frontend/src/types/accounts.ts`
- TypeScript interfaces matching backend DTOs
- `Account`, `AccountCreateRequest`, `AccountUpdateRequest`, `MetaOptionsResponse`

#### Services
- **File**: `frontend/src/services/accounts.ts`
- Accounts service with all CRUD methods
- Uses existing `apiClient` from `api.ts`

#### Composables
- **File**: `frontend/src/composables/useAccountMeta.ts`
- In-memory caching for meta options
- Prevents repeated API calls
- Loading and error state management

#### Views
- **Files**:
  - `frontend/src/views/accounts/AccountsList.vue` - List page with table and delete confirmation
  - `frontend/src/views/accounts/AccountCreate.vue` - Create account form
  - `frontend/src/views/accounts/AccountDetail.vue` - Edit account form

#### Components
- **Files**:
  - `frontend/src/components/accounts/AccountForm.vue` - Shared form for create/edit
  - `frontend/src/components/accounts/AccountTable.vue` - Table view with actions
  - `frontend/src/components/accounts/DateLockField.vue` - Date picker with clear button

#### Routing
- **File**: `frontend/src/router/index.ts`
- Added routes: `/accounts`, `/accounts/new`, `/accounts/:id`

#### Navigation
- **File**: `frontend/src/layouts/AppShell.vue`
- Added "Accounts" link to navigation with active state

#### Styling
- **File**: `frontend/src/style.css`
- Fixed gray background issues
- Removed width constraints for full-width layout

#### Tests
- **Files**:
  - `frontend/src/services/__tests__/accounts.spec.ts` (7 tests)
  - `frontend/src/composables/__tests__/useAccountMeta.spec.ts` (4 tests)
  - `frontend/src/components/accounts/__tests__/DateLockField.spec.ts` (7 tests)
  - `frontend/src/components/accounts/__tests__/AccountTable.spec.ts` (10 tests)
  - `frontend/src/components/accounts/__tests__/AccountForm.spec.ts` (9 tests)
  - `frontend/src/views/accounts/__tests__/AccountsList.spec.ts` (6 tests)
  - `frontend/src/views/accounts/__tests__/AccountCreate.spec.ts` (4 tests)
  - `frontend/src/views/accounts/__tests__/AccountDetail.spec.ts` (6 tests)
- All 84 frontend tests passing

## 🧪 Testing

### Backend Tests
- **Total**: 58 tests passing
- **Coverage**:
  - Account model (creation, enums, timestamps, queries)
  - Accounts API endpoints (CRUD, pagination, validation, error handling)
  - Meta options endpoint
  - Service layer business logic
  - Error handling and exception mapping

### Frontend Tests
- **Total**: 84 tests passing
- **Coverage**:
  - Service layer (API calls, error handling)
  - Composable (caching, error handling)
  - Components (rendering, interactions, validation)
  - Views (loading states, error handling, navigation)

### Running Tests
```bash
# Backend
cd backend && poetry run pytest -v

# Frontend
cd frontend && npm run test:run
```

## 📚 Documentation Updates

- ✅ `moneta-management/Architecture/backend/API Endpoints.md` - Added Accounts endpoints
- ✅ `moneta-management/Architecture/backend/Database.md` - Added Account model documentation
- ✅ `moneta-management/Architecture/backend/Backend Package Structure.md` - Updated with Accounts files
- ✅ `moneta-management/Architecture/backend/Testing.md` - Added Account tests
- ✅ `moneta-management/Architecture/frontend/Frontend Package Structure.md` - Added Accounts structure
- ✅ `moneta-management/Architecture/frontend/Testing.md` - Added Accounts tests
- ✅ `moneta-management/Issues/MON-9 — Accounts backend + UI (Vue + Tailwind).md` - Updated status

## 🎨 UI Features

- **Accounts List Page** (`/accounts`)
  - Table view with all account fields
  - Create account button
  - Row click navigation to detail page
  - Edit and Delete action buttons
  - Delete confirmation modal
  - Loading and error states

- **Create Account Page** (`/accounts/new`)
  - Form with all required and optional fields
  - Dropdowns populated from meta endpoint
  - Client-side validation
  - Error handling and display
  - Navigation to account detail after creation

- **Account Detail Page** (`/accounts/:id`)
  - Pre-filled form for editing
  - All fields editable
  - Date lock field with help text and clear button
  - Save and Cancel buttons
  - Loading and error states

## 🔑 Key Features

1. **No Hardcoded Values**: All enum values and currency lists come from `/api/v1/meta/accounts/options`
2. **Meta Options Caching**: In-memory cache prevents repeated API calls
3. **Date Lock Feature**: Per-account ingestion guardrail with clear UI explanation
4. **Type Safety**: Full TypeScript coverage on frontend
5. **Error Handling**: Comprehensive error handling on both backend and frontend
6. **Test Coverage**: 142 total tests (58 backend + 84 frontend)

## 🚀 How to Test

1. **Start Backend**:
   ```bash
   cd backend
   poetry run uvicorn server.main:app --reload
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Navigate to**: `http://localhost:5173/accounts`

4. **Test Scenarios**:
   - Create a new account
   - View account details
   - Edit account fields
   - Set/clear date lock
   - Delete account (with confirmation)
   - Verify all dropdowns are populated from API

## 📝 Migration Required

Before deploying, apply the database migration:
```bash
cd backend
poetry run alembic upgrade head
```

## ✅ Checklist

- [x] Backend model created with all fields
- [x] Database migration created and tested
- [x] Backend API endpoints implemented
- [x] Service layer with business logic
- [x] Error handling implemented
- [x] Backend tests written and passing
- [x] Frontend types defined
- [x] Frontend service implemented
- [x] Frontend composable for meta caching
- [x] Frontend views created
- [x] Frontend components created
- [x] Routing configured
- [x] Navigation updated
- [x] CSS styling fixed
- [x] Frontend tests written and passing
- [x] Documentation updated
- [x] All tests passing (142 total)

## 🔗 Related Issues

- Closes MON-9

## 📸 Screenshots

_Add screenshots of the Accounts UI here if needed_

---

**Ready for Review** ✅
