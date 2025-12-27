<script setup lang="ts">
import { computed } from "vue";
import type { Account } from "../../types/accounts";

interface Props {
  accounts: Account[];
  isLoading?: boolean;
}

interface Emits {
  (e: "view", account: Account): void;
  (e: "edit", account: Account): void;
  (e: "delete", account: Account): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const formatDateLock = (from: string | null, to: string | null): string => {
  if (!from && !to) return "No date lock";
  if (from && to) return `${from} to ${to}`;
  if (from) return `From: ${from}`;
  if (to) return `To: ${to}`;
  return "No date lock";
};

const formatAccountType = (type: string): string => {
  return type
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};
</script>

<template>
  <div class="overflow-x-auto -mx-4 sm:mx-0">
    <!-- Desktop Table View -->
    <table
      class="min-w-full divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-800 shadow rounded-lg"
    >
      <thead
        class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700"
      >
        <tr>
          <th
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
          >
            Name
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
          >
            Institution
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
          >
            Currency
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
          >
            Type
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
          >
            Economic Area
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
          >
            Date Lock
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
          >
            Actions
          </th>
        </tr>
      </thead>
      <tbody
        class="bg-white dark:bg-gray-800 divide-y divide-gray-100 dark:divide-gray-700"
      >
        <tr v-if="props.isLoading" class="text-center">
          <td
            colspan="7"
            class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400"
          >
            Loading accounts...
          </td>
        </tr>
        <tr v-else-if="props.accounts.length === 0" class="text-center">
          <td
            colspan="7"
            class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400"
          >
            No accounts found. Create your first account to get started.
          </td>
        </tr>
        <tr
          v-for="account in props.accounts"
          :key="account.id"
          class="hover:bg-blue-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
          @click="emit('view', account)"
        >
          <td
            class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white"
          >
            {{ account.name }}
          </td>
          <td
            class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
          >
            {{ account.institution }}
          </td>
          <td
            class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
          >
            {{ account.currency }}
          </td>
          <td
            class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
          >
            {{ formatAccountType(account.account_type) }}
          </td>
          <td
            class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
          >
            {{ account.economic_area || "-" }}
          </td>
          <td
            class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
          >
            {{ formatDateLock(account.datelock_from, account.datelock_to) }}
          </td>
          <td
            class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
            @click.stop
          >
            <div class="flex justify-end gap-2">
              <button
                @click="emit('edit', account)"
                class="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300 transition-colors"
              >
                Edit
              </button>
              <button
                @click="emit('delete', account)"
                class="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300 transition-colors"
              >
                Delete
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
