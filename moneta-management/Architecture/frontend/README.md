# Frontend Architecture Documentation

This directory contains documentation for the Moneta frontend application.

## Documents

### [Frontend Package Structure](./Frontend%20Package%20Structure.md)
Comprehensive documentation of the frontend directory structure, package configuration, and file organization. Includes:
- Directory structure overview
- Package.json dependencies
- TypeScript configuration
- Component organization
- Router setup
- Store structure

### [Frontend Architecture](./Frontend%20Architecture.md)
High-level architecture documentation covering:
- Architecture principles
- Application flow and initialization
- State management patterns
- Routing architecture
- Component patterns
- API communication (future)
- Build and deployment
- Performance considerations

### [Testing](./Testing.md)
Testing setup and documentation covering:
- Vitest configuration
- Test file structure
- Component testing examples
- Store testing examples
- Pre-commit integration

## Quick Reference

### Technology Stack
- **Framework**: Vue 3 (Composition API)
- **Language**: TypeScript
- **Build Tool**: Vite
- **Routing**: Vue Router 4
- **State Management**: Pinia
- **Styling**: Tailwind CSS 4

### Key Directories
- `src/views/` - Route-level page components
- `src/components/` - Reusable UI components
- `src/stores/` - Pinia state management
- `src/router/` - Vue Router configuration
- `src/test/` - Test utilities and setup
- `src/**/__tests__/` - Test files (co-located with source)

### Development Commands
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run test` - Run tests in watch mode
- `npm run test:run` - Run tests once
- `npm run test:ui` - Run tests with UI
- `npm run test:coverage` - Run tests with coverage

## Related Documentation

- [Main Architecture Document](../Moneta%20Code%20Architecture%20Document%20v0.1.md) - Overall system architecture
- [Backend Package Structure](../backend/Backend%20Package%20Structure.md) - Backend structure
- [API Endpoints](../backend/API%20Endpoints.md) - Backend API documentation
- [Docker Development Environment](../Docker%20Development%20Environment.md) - Development setup
