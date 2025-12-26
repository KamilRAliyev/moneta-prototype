# Vue Testing Setup

## Overview

Vitest and Vue Test Utils are fully configured and working for testing Vue components and Pinia stores. Tests run automatically on pre-commit and can be run manually during development.

## Setup Complete

### 1. Package.json Configuration
- **Test Scripts**:
  - `npm run test` - Run tests in watch mode
  - `npm run test:ui` - Run tests with UI
  - `npm run test:run` - Run tests once (for CI/pre-commit)
  - `npm run test:coverage` - Run tests with coverage report
- **Dependencies** (installed):
  - `vitest` (^2.1.8) - Test runner
  - `@vue/test-utils` (^2.4.6) - Vue component testing utilities
  - `@vitest/ui` (^2.1.8) - Vitest UI
  - `jsdom` (^25.0.1) - DOM environment for tests

### 2. Test Configuration
- **`vitest.config.ts`**: Separate Vitest configuration file
  - Uses jsdom environment for DOM testing
  - Configured with globals enabled
  - Coverage reporting with v8 provider
- **`src/test/setup.ts`**: Test setup and cleanup
- **`src/test/utils.ts`**: Test utilities (router, pinia helpers)

### 3. Test Files
- `src/components/__tests__/HelloWorld.spec.ts` - Component test example
- `src/components/accounts/__tests__/` - Accounts component tests
  - `AccountForm.spec.ts` - Form component tests (validation, submit, edit mode)
  - `AccountTable.spec.ts` - Table component tests (display, actions, formatting)
  - `DateLockField.spec.ts` - Date lock field tests (date input, clear button, errors)
- `src/components/statements/__tests__/` - Statements component tests
  - `StatementUpload.spec.ts` - Upload component tests (drag & drop, validation, file selection)
  - `StatementTable.spec.ts` - Table component tests (display, formatting, file existence)
- `src/stores/__tests__/app.spec.ts` - Pinia store test example
- `src/App.vue.spec.ts` - App component test example
- `src/services/__tests__/accounts.spec.ts` - Accounts service tests (CRUD, meta options)
- `src/services/__tests__/statements.spec.ts` - Statements service tests (upload, list, delete, meta)
- `src/composables/__tests__/useAccountMeta.spec.ts` - Meta caching composable tests
- `src/views/accounts/__tests__/` - Accounts view tests
  - `AccountsList.spec.ts` - List page tests (loading, error handling, delete)
  - `AccountCreate.spec.ts` - Create page tests (form submission, navigation)
  - `AccountDetail.spec.ts` - Detail page tests (loading, error handling, update)
- `src/views/statements/__tests__/` - Statements view tests
  - `Statements.spec.ts` - Statements page tests (upload, list, delete, error handling)

### 4. TypeScript Configuration
- `tsconfig.app.json` includes `vitest/globals` types

### 5. Pre-commit Integration
- Vitest hook configured in `.pre-commit-config.yaml`
- Tests run automatically on commit for frontend files

## Running Tests

### Development Mode (Watch)
```bash
npm run test
```

### Run Once
```bash
npm run test:run
```

### With UI
```bash
npm run test:ui
```

### With Coverage
```bash
npm run test:coverage
```

## Writing Tests

### Component Tests

Example component test structure:

```typescript
import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import MyComponent from "../MyComponent.vue";

describe("MyComponent", () => {
  it("renders correctly", () => {
    const wrapper = mount(MyComponent, {
      props: { msg: "Hello" },
    });
    expect(wrapper.text()).toContain("Hello");
  });
});
```

### Store Tests

Example store test structure:

```typescript
import { describe, it, expect, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useMyStore } from "../myStore";

describe("MyStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("initializes correctly", () => {
    const store = useMyStore();
    expect(store.count).toBe(0);
  });
});
```

## Test File Naming

Tests should be named with `.spec.ts` or `.test.ts` suffix:
- `ComponentName.spec.ts`
- `ComponentName.test.ts`
- `storeName.spec.ts`

## Test Coverage

The test suite currently covers:

✅ Component rendering and user interactions
✅ Service layer API calls and error handling
✅ Composable caching behavior
✅ View components (loading states, error handling, navigation)
✅ Form validation and submission
✅ Router navigation
✅ Pinia store functionality

**Current Status**: 119 tests passing (including Accounts and Statements feature tests)

## Pre-commit Integration

Tests will automatically run on pre-commit for frontend files. The hook runs `npm run test:run` when Vue, TypeScript, or JavaScript files are changed in the `frontend/` directory.

## Test Configuration Details

### Vitest Config (`vitest.config.ts`)

The test configuration is in a separate `vitest.config.ts` file (not in `vite.config.ts`):

```typescript
import { defineConfig } from "vitest/config";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    include: ["src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: [
        "node_modules/",
        "src/test/",
        "**/*.d.ts",
        "**/*.config.*",
        "**/mockData/**",
      ],
    },
  },
});
```

### Test Setup File

`src/test/setup.ts` handles test initialization and cleanup:

```typescript
import { afterEach } from "vitest";

// Cleanup after each test (if needed)
// Vue Test Utils handles cleanup automatically when using mount/shallowMount
afterEach(() => {
  // Add any custom cleanup here if needed
});
```

## Troubleshooting

### Type Errors
If you see type errors, make sure:
1. Dependencies are installed: `npm install`
2. TypeScript can find vitest types (check `tsconfig.app.json` has `vitest/globals`)

### Tests Not Running
1. Check that `vitest.config.ts` exists and has the test configuration
2. Verify test files are in the correct location
3. Check that test files match the pattern: `*.spec.ts` or `*.test.ts`

### Pre-commit Not Running Tests
1. Verify pre-commit is installed: `pre-commit install`
2. Check `.pre-commit-config.yaml` has the vitest hook
3. Run pre-commit manually: `pre-commit run --all-files`
