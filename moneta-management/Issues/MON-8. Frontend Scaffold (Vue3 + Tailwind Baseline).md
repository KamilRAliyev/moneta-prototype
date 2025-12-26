
**As a developer**,
I want a clean Vue 3 app with Tailwind, routing, and state management, So that all UI features can be built consistently.

**Acceptance Criteria**
	• 	✅ Vue 3 + Vite + TypeScript initialized
	•	✅ Tailwind CSS installed and working
		•	✅ Tailwind classes apply correctly in components
	•	✅ Vue Router configured
	•	✅ Pinia store configured
	•	✅ AppShell layout exists
	•	✅ API client wrapper exists
	•	✅ Frontend runs locally
	•	✅ Frontend runs within the container

**Out of Scope**
	•	Backend integration
	•	Styling polish

**Status:** ✅ Complete

**Implementation Details:**
- Vue 3 + Vite + TypeScript: Configured and working
- Tailwind CSS: Installed with @tailwindcss/vite plugin, classes working in components
- Vue Router: Configured with nested routes using AppShell layout
- Pinia: Store configured with example app store
- AppShell Layout: Created at `src/layouts/AppShell.vue` with header, navigation, main content area, and footer
- API Client: Axios-based wrapper at `src/services/api.ts` with interceptors and error handling
- Services: Health and System service modules created
- Tests: Comprehensive test coverage for all new components and services (31 tests passing)
- Docker: Frontend runs in app container alongside backend with hot-reload

**Files Created:**
- `frontend/src/layouts/AppShell.vue` - Main layout component
- `frontend/src/services/api.ts` - API client wrapper
- `frontend/src/services/health.ts` - Health service
- `frontend/src/services/system.ts` - System service
- `frontend/src/services/index.ts` - Service barrel export
- `frontend/src/layouts/__tests__/AppShell.spec.ts` - Layout tests
- `frontend/src/services/__tests__/api.spec.ts` - API client tests
- `frontend/src/services/__tests__/health.spec.ts` - Health service tests
- `frontend/src/services/__tests__/system.spec.ts` - System service tests
- `frontend/src/views/__tests__/Home.spec.ts` - Home view tests

**Files Updated:**
- `frontend/src/router/index.ts` - Updated to use AppShell layout
- `frontend/src/views/Home.vue` - Updated with Tailwind classes and API integration
- `frontend/package.json` - Added axios dependency
