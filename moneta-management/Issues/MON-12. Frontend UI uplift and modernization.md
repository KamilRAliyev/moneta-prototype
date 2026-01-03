# MON-12: Frontend UI Uplift & Modernization

## Overview

Transform Moneta's frontend into a **modern, production-grade SaaS dashboard** with improved navigation, theming, UX patterns, and visual polish. This ticket focuses exclusively on frontend improvements—no backend or business logic changes.

---

## Current State

- **Tech Stack**: Vue 3 + Composition API + Tailwind CSS
- **Layout**: Top navbar only, no sidebar
- **Visual State**: Functional but visually outdated
- **UX Gaps**:
  - No loading skeletons (blank states during data fetch)
  - No global notification/toast system
  - No logs viewer panel
  - Limited visual hierarchy
  - Inconsistent component styling

some V0 generated (which i liked UI ) [sample.zip](file:///Users/kamilraliyev/Projects/illiterate_monkey/moneta-management/attachments/sample.zip)

---

## Target State

A modern dashboard inspired by **shadcn/ui** and contemporary SaaS platforms (Linear, Vercel, Stripe):

- **Navigation**: Sticky sidebar with collapsible state
- **Theming**: Full dark/light mode support with smooth transitions
- **UX Patterns**: Skeletons, empty states, error handling, toast notifications
- **Visual Design**: Consistent design system with cards, badges, and polished components
- **Developer Experience**: Reusable component library for future features

---

## Requirements

### 1. Layout System

#### Sidebar
- **Position**: Left side, sticky (always visible)
- **Content**:
  - Navigation items with Lucide icons + labels
  - Collapsible to icon-only mode
- **Behavior**:
  - Smooth collapse/expand animation (200-300ms)
  - Collapsed state shows icons only
  - Expanded state shows icons + text labels
  - State persisted in localStorage

#### Header
- **Position**: Top, sticky (always visible)
- **Left Section**:
  - Sidebar collapse toggle button (top-right of content area)
  - Page title/breadcrumbs (optional)
- **Right Section**:
  - Theme switcher (sun/moon icon)
  - API health indicator (with tooltip)
  - Logs viewer toggle button
- **Styling**: Clean, minimal, consistent height

#### Content Area
- Scrolls independently of sidebar/header
- Proper padding/margins for all screen sizes
- Responsive breakpoints (mobile sidebar becomes drawer)

---

### 2. Navigation

#### Sidebar Routes
- **Home** (`/`) - Dashboard overview
- **Accounts** (`/accounts`) - Account management
- **Statements** (`/statements`) - Statement file uploads
- **Transactions** (`/transactions`) - Transaction list & filters

#### Navigation Behavior
- Active route highlighted (background color + accent border)
- Hover states for all nav items
- Smooth transitions between routes
- Mobile: Sidebar converts to slide-out drawer

---

### 3. Theme System

#### Implementation
- **Modes**: `light` and `dark`
- **Toggle**: Animated sun/moon icon in header
- **Persistence**: localStorage key `moneta-theme`
- **Transition**: Smooth color transitions (150-200ms)
- **Scope**: All components, pages, and UI elements

#### Color Palette
- Define semantic color tokens (background, foreground, border, accent, etc.)
- Ensure sufficient contrast ratios (WCAG AA minimum)
- Support both themes with consistent visual hierarchy

---

### 4. Header Actions

#### Theme Switcher
- Icon button with tooltip
- Click toggles between light/dark
- Smooth icon animation (rotate/fade)

#### API Health Indicator
- Small status dot/icon
- Color-coded: green (healthy), yellow (degraded), red (down)
- Tooltip shows last check time and status details
- Auto-refreshes every 30 seconds

#### Logs Viewer Toggle
- Icon button to open/close log panel
- Badge indicator if new logs available (optional)

---

### 5. Log Viewer Panel

#### Design
- **Position**: Right-side slide-in panel (overlay)
- **Width**: ~400px (responsive)
- **Animation**: Slide in from right (300ms ease-out)

#### Features
- **Display**: Chronological list of log entries
- **Formatting**: Timestamp, level (info/warn/error), message
- **Actions**:
  - Clear all logs
  - Force refresh
  - Filter by level (optional)
- **Auto-scroll**: Scroll to bottom on new logs (toggleable)

#### Data Source
- Integrate with existing logging system or create client-side log store
- Support console logs, API errors, user actions

---

### 6. Notification System

#### Toast/Alert Component
- **Types**: `success`, `error`, `warning`, `info`
- **Position**: Top-right (or configurable)
- **Behavior**:
  - Auto-dismiss after 5 seconds (configurable)
  - Manual dismiss button
  - Stack multiple toasts
  - Smooth slide-in animation

#### Usage Examples
- **Success**: "Account saved successfully", "Statement uploaded"
- **Error**: "Failed to delete transaction", "API connection error"
- **Warning**: "Date lock will prevent future edits"
- **Info**: "Ingestion in progress..."

---

### 7. Page-Level UX Patterns

All pages must implement consistent UX patterns:

#### Loading States
- **Skeleton loaders** replace blank screens
- Match the structure of actual content (cards, tables, lists)
- Shimmer animation for visual feedback

#### Empty States
- **Illustration/icon** + descriptive text
- **Call-to-action** button when applicable
- Examples:
  - "No accounts yet" → "Create Account"
  - "No statements uploaded" → "Upload Statement"
  - "No transactions found" → "Adjust Filters"

#### Error States
- **User-friendly error messages** (not raw API errors)
- **Retry actions** where applicable
- **Fallback UI** for network failures

---

### 8. Page-Specific Designs

#### Home Page (`/`)
- **Welcome header** with user greeting
- **Stats cards**: Total accounts, statements, transactions
- **Quick actions**: Links to common tasks
- **Recent activity** feed (optional)

#### Accounts Page (`/accounts`)
- **Card-based layout** or table view (toggleable)
- **Account cards** show:
  - Account name, type, balance
  - Date lock badge (if locked)
  - Action buttons: Edit, Delete
- **Empty state**: "No accounts" with "Create Account" CTA
- **Skeleton loading**: 3-4 card skeletons

#### Statements Page (`/statements`)
- **Upload section**:
  - Drag & drop zone
  - File input button
  - Accepted formats indicator
- **Statements table**:
  - Columns: Filename, Upload Date, Status, Actions
  - Status badges: `pending`, `ingested`, `error`
  - Ingest button per row (if pending)
- **Skeleton loading**: Table row skeletons

#### Transactions Page (`/transactions`)
- **Filter bar**:
  - Date range picker
  - Account selector
  - Search input
  - Clear filters button
- **Data table**:
  - Sortable columns
  - Pagination controls
  - Column visibility toggle
  - Row count display
- **Actions**:
  - "Remove all transactions" button (with confirmation modal)
- **Empty state**: "No transactions match your filters"

---

### 9. Component Library

Create reusable components in `frontend/src/components/`:

#### Layout Components
- **`AppSidebar.vue`** - Main navigation sidebar
- **`AppHeader.vue`** - Top header with actions
- **`AppLayout.vue`** - Main layout wrapper

#### UI Components
- **`BaseButton.vue`** - Button with variants (primary, secondary, danger, ghost)
- **`Card.vue`** - Container card with optional header/footer
- **`Badge.vue`** - Status badges with color variants
- **`ModalConfirm.vue`** - Confirmation dialog
- **`Toast.vue`** / **`ToastContainer.vue`** - Notification system
- **`Skeleton.vue`** - Loading skeleton (text, card, table variants)
- **`DatePicker.vue`** - Date range picker (shadcn-style)
- **`LogViewerPanel.vue`** - Log viewer slide-in panel

#### Component Standards
- TypeScript props with proper types
- Tailwind classes (no inline styles)
- Accessible (ARIA labels, keyboard navigation)
- Responsive design
- Dark/light theme support

---

### 10. Animations & Transitions

#### Principles
- **Subtle and purposeful** - Enhance UX, don't distract
- **Performance-first** - Use CSS transforms/opacity (GPU-accelerated)
- **Respect preferences** - Honor `prefers-reduced-motion`

#### Specific Animations
- **Hover states**: 150ms color/scale transitions
- **Sidebar collapse**: 200-300ms width transition
- **Panel slide-in**: 300ms transform transition
- **Theme switch**: 150ms color transition
- **Toast appearance**: 200ms slide + fade
- **Page transitions**: Optional, minimal (fade only)

---

## Technical Implementation Notes

### Styling Approach
- Use Tailwind CSS utility classes
- Define custom color tokens in `tailwind.config.js` for theme support
- Create reusable component variants (e.g., `btn-primary`, `btn-secondary`)

### State Management
- Theme state: Pinia store or composable
- Toast notifications: Pinia store with queue
- Logs: Pinia store or composable
- Sidebar collapse state: localStorage + reactive state

### Dependencies
- **Lucide Vue** - Icon library
- **VueUse** - Composable utilities (useLocalStorage, useMediaQuery, etc.)
- Consider **Headless UI** or **Radix Vue** for accessible primitives

---

## Out of Scope

- Backend API changes
- Business logic modifications
- Database schema changes
- New feature development (only UI improvements)
- Mobile app development
- Performance optimizations beyond UI (backend caching, etc.)

---

## Acceptance Criteria

### Must Have
- [ ] Sidebar navigation implemented and sticky
- [ ] Header with all actions (theme, health, logs) functional
- [ ] Dark/light theme works across all pages and components
- [ ] All main pages (Home, Accounts, Statements, Transactions) visually upgraded
- [ ] Loading skeletons replace blank loading states
- [ ] Empty states with CTAs on all data pages
- [ ] Error states with retry actions
- [ ] Toast notification system functional
- [ ] Log viewer panel opens/closes and displays logs
- [ ] All components support both themes
- [ ] Responsive design works on mobile/tablet/desktop
- [ ] No regressions in existing functionality

### Nice to Have
- [ ] Smooth page transitions
- [ ] Keyboard shortcuts (sidebar toggle, theme toggle)
- [ ] Log filtering by level
- [ ] Toast notification queue management

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Code reviewed and approved
- [ ] Visual design matches modern SaaS standards
- [ ] No console errors or warnings
- [ ] Accessibility basics covered (keyboard nav, ARIA labels)
- [ ] Tested in both light and dark themes
- [ ] Tested on multiple screen sizes
- [ ] Documentation updated (component usage, theming guide)

---

## Optional Enhancements (Future Iterations)

These are **high-impact, low-effort** improvements that can be added later:

1. **Command Palette (⌘K)**
   - Quick navigation to Accounts/Statements/Transactions
   - Search functionality

2. **Breadcrumbs**
   - Show current page hierarchy in header
   - Example: "Accounts → Chase Card"

3. **Table Row Hover Actions**
   - Actions appear on row hover (better mobile UX)

4. **Typed Confirmation for Danger Actions**
   - Require typing "DELETE" to confirm destructive actions

5. **Status Color System**
   - Centralized mapping file for status → color
   - Consistent across all components

6. **URL-Synced Filters**
   - Filters persist in URL query params
   - Shareable filtered views
   - Browser back/forward support

---

## Next Steps

Once this ticket is approved, consider:

1. **Breaking into sub-tickets** for incremental delivery
2. **Creating component skeletons** for parallel development
3. **Defining design tokens** (colors, spacing, typography) in Tailwind config
4. **Setting up Storybook** (optional) for component documentation

---

## What's Done

### ✅ Completed Implementation (2025-01-27)

#### 1. shadcn-vue Installation & Configuration
- Installed and configured shadcn-vue component library
- Added all required dependencies (radix-vue, reka-ui, class-variance-authority, etc.)
- Configured TypeScript path aliases (`@` for `src` directory)
- Set up Tailwind CSS v4 with animation plugin
- Initialized Button, Tooltip, ScrollArea, Card, Badge, and Skeleton components

#### 2. Layout System
- ✅ **Sidebar**: Implemented sticky sidebar with collapsible state (w-56 width)
  - Navigation items with Lucide icons + labels
  - Smooth collapse/expand animation (200-300ms)
  - State persisted in localStorage
  - Active route highlighting
- ✅ **Header**: Implemented with all required actions
  - Sidebar collapse toggle button
  - Theme switcher (sun/moon icon) with smooth animation
  - API health indicator with tooltip (auto-refreshes every 30 seconds)
  - Logs viewer toggle button (UI ready, backend integration pending)
- ✅ **Content Area**: Proper padding/margins, scrolls independently

#### 3. Theme System
- ✅ Full dark/light mode support with smooth transitions (150ms)
- ✅ Theme toggle with animated icon
- ✅ Persistence in localStorage (`moneta-theme` key)
- ✅ Semantic color tokens defined (background, foreground, border, accent, etc.)
- ✅ All components support both themes
- ✅ WCAG AA contrast ratios maintained

#### 4. Component Library
- ✅ **Button Component**: shadcn-vue Button with all variants (default, destructive, outline, secondary, ghost, link)
- ✅ **Card Components**: Card, CardHeader, CardTitle, CardDescription, CardContent
- ✅ **Badge Component**: Status badges with color variants
- ✅ **Tooltip Component**: TooltipProvider, TooltipTrigger, TooltipContent
- ✅ **ScrollArea Component**: For smooth scrolling
- ✅ **Skeleton Component**: Loading skeleton with pulse animation
- ✅ All components migrated from native HTML to shadcn-vue components

#### 5. Page-Level UX Patterns
- ✅ **Loading States**: Skeleton loaders implemented for:
  - Home view cards (API Status, Quick Stats, Recent Activity)
  - Transactions table (5 skeleton rows)
  - Accounts table (5 skeleton rows)
  - Statements table (5 skeleton rows)
- ⚠️ **Empty States**: Partially implemented (basic empty states exist, but need CTAs and illustrations)
- ⚠️ **Error States**: Basic error messages exist, but need retry actions

#### 6. Page-Specific Designs
- ✅ **Home Page (`/`)**:
  - Card-based layout with 3 cards (API Status, Quick Stats, Recent Activity)
  - Real-time health monitoring with auto-refresh (20 seconds)
  - Fetches and displays real data (accounts count, statements count, transactions count)
  - Recent activity shows latest statement upload
  - Welcome header with proper typography (Inter font)
- ✅ **Accounts Page (`/accounts`)**:
  - Table view implemented
  - Skeleton loading states
  - Basic empty state
- ✅ **Statements Page (`/statements`)**:
  - Upload section with drag & drop
  - Statements table with all required columns
  - Status badges with semantic colors
  - Skeleton loading states
  - Table optimized to fit without horizontal scroll
- ✅ **Transactions Page (`/transactions`)**:
  - Filter bar with account selector
  - Sortable columns
  - Pagination controls
  - Column visibility toggle
  - Skeleton loading states
  - "Remove all transactions" button with confirmation modal

#### 7. Animations & Transitions
- ✅ Hover states with 150ms transitions
- ✅ Sidebar collapse animation (200-300ms)
- ✅ Theme switch color transitions (150ms)
- ✅ Animation keyframes defined (fade, zoom, slide)
- ⚠️ Panel slide-in animation (LogViewerPanel UI ready, but not fully functional)
- ⚠️ Toast appearance animation (Toast system not yet implemented)

#### 8. Color System Migration
- ✅ Replaced all hardcoded colors with semantic color tokens
- ✅ Fixed button text colors for theme adaptability
- ✅ Consistent color system across all components
- ✅ All text colors adapt automatically to theme changes

#### 9. UI Refinements
- ✅ Sidebar width optimized (reduced from w-64 to w-56)
- ✅ Statements table optimized (no horizontal scroll, proper truncation)
- ✅ All blue colors replaced with semantic colors
- ✅ Typography improved (Inter font, proper sizing)
- ✅ Card styling matches reference design

#### 10. System Improvements
- ✅ Timestamp formatting fixed (ISO 8601 with timezone)
- ✅ Health check auto-refresh implemented
- ✅ Python version and uptime added to health status
- ✅ Font updated to Inter (similar to Geist)

---

## What's Left

### ❌ Not Yet Implemented

#### 1. Notification System (Toast)
- [ ] Toast/Alert component implementation
- [ ] Toast container with positioning (top-right)
- [ ] Auto-dismiss after 5 seconds
- [ ] Manual dismiss button
- [ ] Stack multiple toasts
- [ ] Smooth slide-in animation
- [ ] Integration with Pinia store for queue management

#### 2. Log Viewer Panel (Backend Integration)
- [ ] Backend API endpoint for fetching logs
- [ ] Real-time log streaming (optional)
- [ ] Filter by log level (info/warn/error)
- [ ] Auto-scroll to bottom toggle
- [ ] Full panel functionality (currently UI only, hidden)

#### 3. Empty States Enhancement
- [ ] Add illustrations/icons to empty states
- [ ] Add call-to-action buttons to empty states
- [ ] Improve empty state messaging
- [ ] Examples needed:
  - "No accounts yet" → "Create Account" button
  - "No statements uploaded" → "Upload Statement" button
  - "No transactions found" → "Adjust Filters" button

#### 4. Error States Enhancement
- [ ] User-friendly error messages (not raw API errors)
- [ ] Retry actions for failed API calls
- [ ] Fallback UI for network failures
- [ ] Better error handling across all pages

#### 5. Responsive Design
- [ ] Mobile sidebar becomes drawer (slide-out)
- [ ] Tablet breakpoint optimizations
- [ ] Mobile-specific UI adjustments
- [ ] Touch-friendly interactions

#### 6. Accessibility
- [ ] ARIA labels for all interactive elements
- [ ] Keyboard navigation improvements
- [ ] Focus management
- [ ] Screen reader support

#### 7. Nice to Have Features
- [ ] Smooth page transitions
- [ ] Keyboard shortcuts (sidebar toggle, theme toggle)
- [ ] Log filtering by level (in LogViewerPanel)
- [ ] Toast notification queue management

#### 8. Component Library Gaps
- [ ] ModalConfirm component (currently using basic modals)
- [ ] DatePicker component (date range picker)
- [ ] Enhanced empty state components

---

## Progress Summary

### Acceptance Criteria Status

**Must Have:**
- ✅ Sidebar navigation implemented and sticky
- ✅ Header with all actions (theme, health, logs UI) functional
- ✅ Dark/light theme works across all pages and components
- ✅ All main pages (Home, Accounts, Statements, Transactions) visually upgraded
- ✅ Loading skeletons replace blank loading states
- ⚠️ Empty states with CTAs on all data pages (basic empty states exist, need enhancement)
- ⚠️ Error states with retry actions (basic error messages exist, need retry actions)
- ❌ Toast notification system functional (not implemented)
- ⚠️ Log viewer panel opens/closes and displays logs (UI ready, backend integration needed)
- ✅ All components support both themes
- ⚠️ Responsive design works on mobile/tablet/desktop (desktop done, mobile needs work)
- ✅ No regressions in existing functionality

**Nice to Have:**
- ❌ Smooth page transitions
- ❌ Keyboard shortcuts (sidebar toggle, theme toggle)
- ❌ Log filtering by level
- ❌ Toast notification queue management

### Completion Estimate
- **Completed**: ~75% of core requirements
- **Remaining**: Toast system, Log viewer backend integration, Empty/Error state enhancements, Mobile responsiveness, Accessibility improvements
