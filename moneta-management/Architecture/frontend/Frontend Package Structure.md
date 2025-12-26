# Frontend Package Structure

## Overview
The frontend is a Vue 3 Single Page Application (SPA) using TypeScript, Vite for build tooling, Tailwind CSS for styling, Vue Router for routing, and Pinia for state management.

## Directory Structure

```
frontend/
├── package.json              # npm project configuration and dependencies
├── package-lock.json          # npm lock file (dependency versions)
├── vite.config.ts            # Vite build configuration
├── vitest.config.ts           # Vitest test configuration
├── tsconfig.json              # TypeScript root configuration
├── tsconfig.app.json          # TypeScript configuration for app code
├── tsconfig.node.json         # TypeScript configuration for Vite config
├── index.html                 # HTML entry point
├── public/                    # Static assets (copied as-is)
│   └── vite.svg               # Vite logo
└── src/                       # Source code directory
    ├── main.ts                # Application entry point
    ├── App.vue                # Root Vue component
    ├── App.vue.spec.ts        # App component test
    ├── style.css              # Global styles and Tailwind imports
    ├── assets/                # Assets processed by Vite
    │   └── vue.svg            # Vue logo
    ├── components/            # Reusable Vue components
    │   ├── HelloWorld.vue     # Example component
    │   └── __tests__/         # Component tests
    │       └── HelloWorld.spec.ts
    ├── layouts/               # Layout components
    │   ├── AppShell.vue       # Main application shell layout
    │   └── __tests__/         # Layout tests
    │       └── AppShell.spec.ts
    ├── views/                 # Route-level page components
    │   ├── Home.vue           # Home page view
    │   └── __tests__/         # View tests
    │       └── Home.spec.ts
    ├── router/                # Vue Router configuration
    │   └── index.ts           # Router setup and route definitions
    ├── services/              # API service layer
    │   ├── api.ts             # Axios API client wrapper
    │   ├── health.ts          # Health check service
    │   ├── system.ts          # System information service
    │   ├── index.ts           # Service exports (barrel file)
    │   └── __tests__/         # Service tests
    │       ├── api.spec.ts
    │       ├── health.spec.ts
    │       └── system.spec.ts
    ├── stores/                # Pinia state management stores
    │   ├── index.ts           # Store exports (barrel file)
    │   ├── app.ts             # Example app store
    │   └── __tests__/         # Store tests
    │       └── app.spec.ts
    └── test/                  # Test utilities and setup
        ├── setup.ts           # Test setup and cleanup
        └── utils.ts           # Test utilities (router, pinia helpers)
```

## Package Details

### Root Level

#### `package.json`
- **Purpose**: npm project configuration and dependency management
- **Key Dependencies**:
  - `vue` (^3.5.24) - Vue 3 framework
  - `vue-router` (^4.6.4) - Client-side routing
  - `pinia` (^3.0.4) - State management
  - `axios` (^1.13.2) - HTTP client for API requests
  - `tailwindcss` (^4.1.18) - Utility-first CSS framework
  - `@tailwindcss/vite` (^4.1.18) - Tailwind Vite plugin
- **Dev Dependencies**:
  - `vite` (^7.2.4) - Build tool and dev server
  - `@vitejs/plugin-vue` (^6.0.1) - Vue plugin for Vite
  - `typescript` (~5.9.3) - TypeScript compiler
  - `vue-tsc` (^3.1.4) - TypeScript type checking for Vue
  - `@vue/tsconfig` (^0.8.1) - Vue TypeScript configurations
  - `@types/node` (^24.10.1) - Node.js type definitions
  - `vitest` (^2.1.8) - Test runner
  - `@vue/test-utils` (^2.4.6) - Vue component testing utilities
  - `@vitest/ui` (^2.1.8) - Vitest UI
  - `jsdom` (^25.0.1) - DOM environment for tests
- **Scripts**:
  - `dev`: Start Vite development server
  - `build`: Type check and build for production
  - `preview`: Preview production build locally
  - `test`: Run tests in watch mode
  - `test:ui`: Run tests with UI
  - `test:run`: Run tests once (for CI/pre-commit)
  - `test:coverage`: Run tests with coverage report

#### `vite.config.ts`
- **Purpose**: Vite build tool configuration
- **Plugins**:
  - `vue()`: Vue SFC (Single File Component) support
  - `tailwindcss()`: Tailwind CSS processing
- **Features**:
  - Hot Module Replacement (HMR) in development
  - Optimized production builds
  - TypeScript support

#### `vitest.config.ts`
- **Purpose**: Vitest test runner configuration
- **Features**:
  - Uses jsdom environment for DOM testing
  - Globals enabled (no need to import test functions)
  - Test setup file: `./src/test/setup.ts`
  - Coverage reporting with v8 provider
  - Separate from `vite.config.ts` for better separation of concerns

#### `tsconfig.json`
- **Purpose**: TypeScript root configuration
- **Extends**: `@vue/tsconfig/tsconfig.json`
- **References**: `tsconfig.app.json` and `tsconfig.node.json`

#### `tsconfig.app.json`
- **Purpose**: TypeScript configuration for application code
- **Extends**: `@vue/tsconfig/tsconfig.dom.json`
- **Includes**: `src/**/*.ts`, `src/**/*.tsx`, `src/**/*.vue`
- **Types**: `["vite/client", "vitest/globals"]` - Includes Vitest global types
- **Compiler Options**:
  - Strict mode enabled
  - Unused locals/parameters checking
  - Erasable syntax only
  - No fallthrough cases in switch
  - No unchecked side effect imports

#### `tsconfig.node.json`
- **Purpose**: TypeScript configuration for Vite config and build tools
- **Includes**: `vite.config.ts`
- **Compiler Options**:
  - Target: ES2023
  - Module: ESNext
  - Module resolution: bundler
  - Allow importing TypeScript extensions
  - Verbatim module syntax

#### `index.html`
- **Purpose**: HTML entry point
- **Features**:
  - Root `<div id="app">` for Vue mounting
  - Script tag loading `main.ts` as module
  - Global stylesheet link

### `src/` Directory

#### `src/main.ts`
- **Purpose**: Application entry point
- **Responsibilities**:
  - Import global styles
  - Create Vue application instance
  - Initialize Pinia store
  - Initialize Vue Router
  - Mount application to DOM

#### `src/App.vue`
- **Purpose**: Root Vue component
- **Features**:
  - Contains `<router-view />` for route rendering
  - Base layout wrapper

#### `src/style.css`
- **Purpose**: Global styles
- **Features**:
  - Tailwind CSS directives (`@tailwind base`, `@tailwind components`, `@tailwind utilities`)
  - Custom global styles

### `src/components/` Module

Reusable Vue components used across the application.

#### `src/components/HelloWorld.vue`
- Example component demonstrating component structure
- Can be removed or repurposed

### `src/views/` Module

Route-level page components. Each route typically has a corresponding view component.

#### `src/views/Home.vue`
- Home page view component
- Currently contains example content from the original App.vue

### `src/router/` Module

Vue Router configuration and route definitions.

#### `src/router/index.ts`
- **Purpose**: Router setup and route definitions
- **Features**:
  - Creates router instance with web history mode
  - Defines application routes
  - Exports router for use in `main.ts`
- **Current Routes**:
  - `/` - Home page (renders `Home.vue`)

### `src/stores/` Module

Pinia state management stores using Composition API style.

#### `src/stores/index.ts`
- **Purpose**: Barrel export file for easier imports
- **Exports**: All store modules

#### `src/stores/app.ts`
- **Purpose**: Example application store
- **State**:
  - `count`: Counter value (number)
  - `name`: Application name (string)
- **Getters**:
  - `doubleCount`: Computed value (count * 2)
- **Actions**:
  - `increment()`: Increment counter
  - `decrement()`: Decrement counter
  - `reset()`: Reset counter to 0
  - `setName(newName: string)`: Update application name

#### `src/stores/__tests__/app.spec.ts`
- **Purpose**: Unit tests for the app store
- **Tests**: Store initialization, state mutations, getters, and actions

### `src/test/` Module

Test utilities and setup files.

#### `src/test/setup.ts`
- **Purpose**: Test setup and cleanup
- **Features**:
  - Runs before each test file
  - Handles cleanup after tests

#### `src/test/utils.ts`
- **Purpose**: Test utility functions
- **Functions**:
  - `createTestRouter()`: Creates a test Vue Router instance
  - `setupPinia()`: Sets up Pinia for testing
  - Global test configuration for Vue Test Utils

## Technology Stack

- **Framework**: Vue 3 (Composition API)
- **Language**: TypeScript
- **Build Tool**: Vite
- **Routing**: Vue Router 4
- **State Management**: Pinia
- **Styling**: Tailwind CSS 4
- **Package Manager**: npm

## Development Workflow

### Development Server
```bash
npm run dev
```
- Starts Vite dev server with HMR
- Typically runs on `http://localhost:5173`

### Production Build
```bash
npm run build
```
- Type checks with `vue-tsc`
- Builds optimized production bundle to `dist/`
- Assets are hashed for cache busting

### Preview Production Build
```bash
npm run preview
```
- Serves the production build locally for testing

### Testing
```bash
npm run test        # Watch mode
npm run test:run    # Run once (for CI/pre-commit)
npm run test:ui     # Run with UI
npm run test:coverage  # Run with coverage
```
- Uses Vitest with jsdom environment
- Tests located in `__tests__/` directories
- Configuration in `vitest.config.ts`
- Pre-commit hook runs tests automatically

## Component Architecture

### Component Types

1. **Layouts** (`src/layouts/`): Layout wrapper components (e.g., AppShell)
2. **Views** (`src/views/`): Route-level page components
3. **Components** (`src/components/`): Reusable UI components
4. **Stores** (`src/stores/`): State management modules
5. **Services** (`src/services/`): API service layer

### Component Structure

Vue Single File Components (SFC) follow this structure:
```vue
<script setup lang="ts">
// TypeScript script with Composition API
</script>

<template>
  <!-- HTML template -->
</template>

<style scoped>
/* Scoped CSS styles */
</style>
```

## State Management

### Pinia Stores

Stores use the Composition API style with `defineStore`:
- **State**: Reactive refs
- **Getters**: Computed properties
- **Actions**: Functions that modify state

### Using Stores

```typescript
import { useAppStore } from "@/stores";

const store = useAppStore();
// Access state: store.count, store.name
// Use getters: store.doubleCount
// Call actions: store.increment(), store.decrement()
```

## Routing

### Route Definition

Routes are defined in `src/router/index.ts`:
```typescript
{
  path: "/",
  name: "home",
  component: Home,
}
```

### Navigation

Use Vue Router's `router-link` component or programmatic navigation:
```typescript
import { useRouter } from "vue-router";
const router = useRouter();
router.push("/");
```

## Styling

### Tailwind CSS

- Utility-first CSS framework
- Configured via `@tailwindcss/vite` plugin
- Global styles in `src/style.css`
- Component-scoped styles in `<style>` blocks

### CSS Organization

- **Global styles**: `src/style.css`
- **Component styles**: Scoped `<style scoped>` blocks in components
- **Tailwind utilities**: Used directly in templates

## TypeScript Configuration

### Type Checking

- Strict mode enabled
- Unused variables/parameters checked
- Type checking runs during build (`vue-tsc -b`)

### Path Aliases

Currently using relative imports. Can be extended with path aliases in `vite.config.ts`:
```typescript
resolve: {
  alias: {
    "@": path.resolve(__dirname, "./src"),
  },
}
```

## Initial State

This is the current structure of the frontend package. The following components are in place:

- ✅ Vue 3 application with TypeScript
- ✅ Vite build configuration
- ✅ Vitest test configuration (separate config file)
- ✅ Tailwind CSS setup
- ✅ Vue Router configuration with nested routes
- ✅ Pinia state management
- ✅ Layout structure (AppShell layout)
- ✅ Component structure (components, views)
- ✅ Store structure
- ✅ API service layer (axios-based client, health, system services)
- ✅ Test structure (test files, utilities, setup)
- ✅ TypeScript strict mode configuration
- ✅ Pre-commit integration for tests

### `src/layouts/` Module

Layout components that wrap route-level views.

#### `src/layouts/AppShell.vue`
- **Purpose**: Main application shell layout
- **Features**:
  - Header with logo and navigation
  - Main content area with router-view
  - Footer
  - Tailwind CSS styling with dark mode support
- **Usage**: Wraps routes in router configuration

#### `src/layouts/__tests__/AppShell.spec.ts`
- **Purpose**: Unit tests for AppShell layout
- **Tests**: Header, navigation, footer, router-view rendering

### `src/services/` Module

API service layer for backend communication.

#### `src/services/api.ts`
- **Purpose**: Axios-based API client wrapper
- **Features**:
  - Base URL configuration (`http://localhost:8000/api/v1`)
  - Request/response interceptors
  - Error handling for HTTP status codes
  - Timeout configuration (10 seconds)
  - Type-safe exports

#### `src/services/health.ts`
- **Purpose**: Health check service
- **Methods**:
  - `getHealth()`: Get health status from backend

#### `src/services/system.ts`
- **Purpose**: System information service
- **Methods**:
  - `getSystemInfo()`: Get system information from backend

#### `src/services/index.ts`
- **Purpose**: Barrel export for services
- **Exports**: All service modules

#### `src/services/__tests__/`
- **Purpose**: Service unit tests
- **Tests**: API client configuration, service methods, error handling

## Future Expansion Areas

The following areas are ready for expansion:

- Additional routes and views
- More Pinia stores for different domains
- Additional API services (uploads, accounts, etc.)
- Component library expansion
- Form validation
- Error handling and loading states
- Authentication/authorization
- Path aliases configuration
- Environment variable configuration
- API endpoint constants
- Additional test utilities and helpers
