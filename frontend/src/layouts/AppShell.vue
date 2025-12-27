<script setup lang="ts">
import { RouterLink, useRoute } from "vue-router";

const route = useRoute();
</script>

<template>
  <div class="min-h-screen bg-white dark:bg-gray-900">
    <!-- Header -->
    <header class="bg-white dark:bg-gray-800 shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo/Brand -->
          <div class="flex items-center">
            <RouterLink
              to="/"
              class="text-xl font-bold text-gray-900 dark:text-white hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
            >
              Moneta
            </RouterLink>
          </div>

          <!-- Navigation -->
          <nav class="flex space-x-4">
            <RouterLink
              to="/"
              class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="
                route.path === '/'
                  ? 'bg-gray-900 text-white dark:bg-gray-700'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
              "
            >
              Home
            </RouterLink>
            <RouterLink
              to="/accounts"
              class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="
                route.path.startsWith('/accounts')
                  ? 'bg-gray-900 text-white dark:bg-gray-700'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
              "
            >
              Accounts
            </RouterLink>
            <RouterLink
              to="/statements"
              class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="
                route.path.startsWith('/statements')
                  ? 'bg-gray-900 text-white dark:bg-gray-700'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
              "
            >
              Statements
            </RouterLink>
            <RouterLink
              to="/transactions"
              class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="
                route.path.startsWith('/transactions')
                  ? 'bg-gray-900 text-white dark:bg-gray-700'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
              "
            >
              Transactions
            </RouterLink>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="w-full px-4 sm:px-6 lg:px-8 py-8">
      <router-view />
    </main>

    <!-- Footer -->
    <footer
      class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="text-center text-sm text-gray-600 dark:text-gray-400">
          © 2025 Moneta. All rights reserved.
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Additional component-specific styles if needed */
</style>
