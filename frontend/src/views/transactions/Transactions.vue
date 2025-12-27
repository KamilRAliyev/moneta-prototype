<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { useTransactionsStore } from "../../stores/transactions";
import { accountsService } from "../../services/accounts";
import type { Account } from "../../types/accounts";

const transactionsStore = useTransactionsStore();

const accounts = ref<Account[]>([]);
const showColumnChooser = ref(false);
const showDeleteConfirm = ref(false);
const showFilterDialog = ref(false);
const currentFilter = ref<{
  field: string;
  operator: string;
  value: string;
} | null>(null);

// Load accounts for filter dropdown
onMounted(async () => {
  try {
    accounts.value = await accountsService.listAccounts();
    await transactionsStore.loadMeta();
    await transactionsStore.loadTransactions();
  } catch (err) {
    console.error("Failed to load data:", err);
  }
});

const formatValue = (value: unknown, type: string): string => {
  if (value === null || value === undefined) return "-";
  if (type === "date") {
    try {
      return new Date(value as string).toLocaleDateString();
    } catch {
      return String(value);
    }
  }
  if (type === "number") {
    return Number(value).toLocaleString();
  }
  return String(value);
};

const formatDateTime = (dateString: string): string => {
  return new Date(dateString).toLocaleString();
};

const visibleIngestedColumns = computed(() => {
  return transactionsStore.ingestedColumns.filter((col) =>
    transactionsStore.visibleColumns.has(col.name),
  );
});

const getColumnType = (columnName: string): string => {
  const col = transactionsStore.allColumns.find((c) => c.name === columnName);
  return col?.type ?? "string";
};

const handleSort = (field: string) => {
  const newDir =
    transactionsStore.sortBy === field && transactionsStore.sortDir === "desc"
      ? "asc"
      : "desc";
  transactionsStore.setSort(field, newDir);
};

const sortIcon = (field: string): string => {
  if (transactionsStore.sortBy !== field) return "⇅";
  return transactionsStore.sortDir === "asc" ? "↑" : "↓";
};

const handleAddFilter = () => {
  showFilterDialog.value = true;
  currentFilter.value = {
    field: "",
    operator: "=",
    value: "",
  };
};

const applyFilter = () => {
  if (!currentFilter.value || !currentFilter.value.field) return;

  const filterStr = `ingested_content.${currentFilter.value.field}:${currentFilter.value.operator}:${currentFilter.value.value}`;
  const existingFilters = transactionsStore.filters
    ? transactionsStore.filters.split(",")
    : [];
  existingFilters.push(filterStr);
  transactionsStore.setFilters(existingFilters.join(","));
  showFilterDialog.value = false;
  currentFilter.value = null;
};

const removeFilter = (index: number) => {
  const filters = transactionsStore.filters.split(",");
  filters.splice(index, 1);
  transactionsStore.setFilters(filters.join(","));
};

const activeFilters = computed(() => {
  return transactionsStore.filters ? transactionsStore.filters.split(",") : [];
});

const handleDeleteAll = async () => {
  try {
    const deleted = await transactionsStore.deleteTransactions(
      transactionsStore.selectedAccountId,
    );
    alert(`Deleted ${deleted} transactions`);
    showDeleteConfirm.value = false;
  } catch (err) {
    console.error("Delete failed:", err);
  }
};

const operators = [
  { value: "=", label: "Equals" },
  { value: "!=", label: "Not equals" },
  { value: ">", label: "Greater than" },
  { value: ">=", label: "Greater than or equal" },
  { value: "<", label: "Less than" },
  { value: "<=", label: "Less than or equal" },
  { value: "contains", label: "Contains" },
  { value: "empty", label: "Is empty" },
  { value: "not_empty", label: "Is not empty" },
];
</script>

<template>
  <div class="space-y-6 w-full">
    <!-- Header -->
    <div class="flex justify-between items-start">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          Transactions
        </h1>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          View and manage ingested transaction data
        </p>
      </div>
      <div class="flex gap-2">
        <button
          @click="showColumnChooser = true"
          class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
        >
          Column Settings
        </button>
        <button
          @click="showDeleteConfirm = true"
          class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
        >
          Remove All Transactions
        </button>
      </div>
    </div>

    <!-- Error Message -->
    <div
      v-if="transactionsStore.error"
      class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md"
    >
      <p class="text-sm text-red-800 dark:text-red-200">
        {{ transactionsStore.error }}
      </p>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-4">
      <div class="flex flex-wrap gap-4 items-center">
        <div>
          <label
            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Account
          </label>
          <select
            v-model="transactionsStore.selectedAccountId"
            @change="
              transactionsStore.setAccount(transactionsStore.selectedAccountId)
            "
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option :value="undefined">All Accounts</option>
            <option
              v-for="account in accounts"
              :key="account.id"
              :value="account.id"
            >
              {{ account.name }}
            </option>
          </select>
        </div>

        <div class="flex-1">
          <label
            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Filters
          </label>
          <div class="flex gap-2 items-center flex-wrap">
            <span
              v-for="(filter, index) in activeFilters"
              :key="index"
              class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded text-sm flex items-center gap-1"
            >
              {{ filter }}
              <button
                @click="removeFilter(index)"
                class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
              >
                ×
              </button>
            </span>
            <button
              @click="handleAddFilter"
              class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              + Add Filter
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Transactions Table -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800"
                @click="handleSort('inserted_at')"
              >
                Inserted At {{ sortIcon("inserted_at") }}
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
              >
                Account
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
              >
                Statement
              </th>
              <th
                v-for="col in visibleIngestedColumns"
                :key="col.name"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800"
                @click="handleSort(`ingested_content.${col.name}`)"
              >
                {{ col.name }} {{ sortIcon(`ingested_content.${col.name}`) }}
              </th>
            </tr>
          </thead>
          <tbody
            class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700"
          >
            <tr v-if="transactionsStore.isLoading">
              <td
                :colspan="3 + visibleIngestedColumns.length"
                class="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400"
              >
                Loading transactions...
              </td>
            </tr>
            <tr v-else-if="transactionsStore.transactions.length === 0">
              <td
                :colspan="3 + visibleIngestedColumns.length"
                class="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400"
              >
                No transactions found.
              </td>
            </tr>
            <tr
              v-for="transaction in transactionsStore.transactions"
              :key="transaction.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <td
                class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
              >
                {{ formatDateTime(transaction.inserted_at) }}
              </td>
              <td
                class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white"
              >
                {{ transaction.account.name }}
              </td>
              <td
                class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
              >
                {{ transaction.statement_file.original_filename }}
              </td>
              <td
                v-for="col in visibleIngestedColumns"
                :key="col.name"
                class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white"
              >
                {{
                  formatValue(
                    transaction.ingested_content[col.name],
                    getColumnType(col.name),
                  )
                }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div
        class="bg-white dark:bg-gray-800 px-4 py-3 border-t border-gray-200 dark:border-gray-700 sm:px-6"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-700 dark:text-gray-300">
              Showing
              <select
                v-model="transactionsStore.pageSize"
                @change="
                  transactionsStore.setPageSize(transactionsStore.pageSize)
                "
                class="mx-1 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700"
              >
                <option :value="25">25</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
              </select>
              per page
            </span>
            <span class="text-sm text-gray-700 dark:text-gray-300">
              Page {{ transactionsStore.currentPage }} of
              {{ transactionsStore.totalPages }} (Total:
              {{ transactionsStore.totalCount.toLocaleString() }})
            </span>
          </div>
          <div class="flex gap-2">
            <button
              @click="
                transactionsStore.setPage(transactionsStore.currentPage - 1)
              "
              :disabled="transactionsStore.currentPage === 1"
              class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Previous
            </button>
            <button
              @click="
                transactionsStore.setPage(transactionsStore.currentPage + 1)
              "
              :disabled="
                transactionsStore.currentPage >= transactionsStore.totalPages
              "
              class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Column Chooser Modal -->
    <div
      v-if="showColumnChooser"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showColumnChooser = false"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
        @click.stop
      >
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Column Settings
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Showing {{ transactionsStore.visibleColumns.size }} of
          {{ transactionsStore.allColumns.length }} columns
        </p>
        <div class="space-y-2">
          <div
            v-for="col in transactionsStore.allColumns"
            :key="col.name"
            class="flex items-center gap-2"
          >
            <input
              type="checkbox"
              :id="`col-${col.name}`"
              :checked="transactionsStore.visibleColumns.has(col.name)"
              @change="transactionsStore.toggleColumn(col.name)"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label
              :for="`col-${col.name}`"
              class="text-sm text-gray-700 dark:text-gray-300 cursor-pointer"
            >
              {{ col.name }}
              <span class="text-xs text-gray-500">({{ col.type }})</span>
            </label>
          </div>
        </div>
        <div class="mt-6 flex justify-end gap-2">
          <button
            @click="transactionsStore.setDefaultVisibleColumns()"
            class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            Show All
          </button>
          <button
            @click="showColumnChooser = false"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Done
          </button>
        </div>
      </div>
    </div>

    <!-- Filter Dialog -->
    <div
      v-if="showFilterDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showFilterDialog = false"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-md w-full mx-4"
        @click.stop
      >
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Add Filter
        </h3>
        <div class="space-y-4">
          <div>
            <label
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Field
            </label>
            <select
              v-model="currentFilter!.field"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
            >
              <option value="">Select field...</option>
              <option
                v-for="col in transactionsStore.ingestedColumns"
                :key="col.name"
                :value="col.name"
              >
                {{ col.name }} ({{ col.type }})
              </option>
            </select>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Operator
            </label>
            <select
              v-model="currentFilter!.operator"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
            >
              <option v-for="op in operators" :key="op.value" :value="op.value">
                {{ op.label }}
              </option>
            </select>
          </div>
          <div
            v-if="
              currentFilter!.operator !== 'empty' &&
              currentFilter!.operator !== 'not_empty'
            "
          >
            <label
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Value
            </label>
            <input
              v-model="currentFilter!.value"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
              placeholder="Enter value..."
            />
          </div>
        </div>
        <div class="mt-6 flex justify-end gap-2">
          <button
            @click="showFilterDialog = false"
            class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            Cancel
          </button>
          <button
            @click="applyFilter"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Apply
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteConfirm"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showDeleteConfirm = false"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-md w-full mx-4"
        @click.stop
      >
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Remove All Transactions
        </h3>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          {{
            transactionsStore.selectedAccountId
              ? `Are you sure you want to delete all transactions for the selected account? This action cannot be undone.`
              : `Are you sure you want to delete ALL transactions? This action cannot be undone.`
          }}
        </p>
        <div class="flex justify-end gap-3">
          <button
            @click="showDeleteConfirm = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600"
          >
            Cancel
          </button>
          <button
            @click="handleDeleteAll"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
