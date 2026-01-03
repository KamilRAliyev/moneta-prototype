<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { X } from "lucide-vue-next";
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
        <h1 class="text-3xl font-bold text-foreground">Transactions</h1>
        <p class="mt-2 text-sm text-muted-foreground">
          View and manage ingested transaction data
        </p>
      </div>
      <div class="flex gap-2">
        <Button @click="showColumnChooser = true" variant="secondary">
          Column Settings
        </Button>
        <Button @click="showDeleteConfirm = true" variant="destructive">
          Remove All Transactions
        </Button>
      </div>
    </div>

    <!-- Error Message -->
    <div
      v-if="transactionsStore.error"
      class="p-4 bg-destructive/10 border border-destructive/20 rounded-md"
    >
      <p class="text-sm text-destructive">
        {{ transactionsStore.error }}
      </p>
    </div>

    <!-- Filters -->
    <div class="bg-card shadow rounded-lg p-4">
      <div class="flex flex-wrap gap-4 items-center">
        <div>
          <label class="block text-sm font-medium text-foreground mb-1">
            Account
          </label>
          <select
            v-model="transactionsStore.selectedAccountId"
            @change="
              transactionsStore.setAccount(transactionsStore.selectedAccountId)
            "
            class="px-3 py-2 border border-input rounded-md bg-background text-foreground"
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
          <label class="block text-sm font-medium text-foreground mb-1">
            Filters
          </label>
          <div class="flex gap-2 items-center flex-wrap">
            <span
              v-for="(filter, index) in activeFilters"
              :key="index"
              class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded text-sm flex items-center gap-1"
            >
              {{ filter }}
              <Button
                @click="removeFilter(index)"
                variant="ghost"
                size="icon"
                class="h-4 w-4 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
              >
                <X class="h-3 w-3" />
              </Button>
            </span>
            <Button @click="handleAddFilter" variant="outline" size="sm">
              + Add Filter
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Transactions Table -->
    <div class="bg-card shadow rounded-lg overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-border">
          <thead class="bg-muted/50">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted"
                @click="handleSort('inserted_at')"
              >
                Inserted At {{ sortIcon("inserted_at") }}
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider"
              >
                Account
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider"
              >
                Statement
              </th>
              <th
                v-for="col in visibleIngestedColumns"
                :key="col.name"
                class="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted"
                @click="handleSort(`ingested_content.${col.name}`)"
              >
                {{ col.name }} {{ sortIcon(`ingested_content.${col.name}`) }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-card divide-y divide-border">
            <template v-if="transactionsStore.isLoading">
              <tr
                v-for="i in 5"
                :key="`skeleton-${i}`"
                class="hover:bg-muted/50"
              >
                <td class="px-6 py-4">
                  <Skeleton class="h-4 w-32" />
                </td>
                <td class="px-6 py-4">
                  <Skeleton class="h-4 w-24" />
                </td>
                <td class="px-6 py-4">
                  <Skeleton class="h-4 w-40" />
                </td>
                <td
                  v-for="col in visibleIngestedColumns"
                  :key="col.name"
                  class="px-6 py-4"
                >
                  <Skeleton class="h-4 w-20" />
                </td>
              </tr>
            </template>
            <template v-else-if="transactionsStore.transactions.length === 0">
              <tr>
                <td
                  :colspan="3 + visibleIngestedColumns.length"
                  class="px-6 py-4 text-center text-sm text-muted-foreground"
                >
                  No transactions found.
                </td>
              </tr>
            </template>
            <template v-else>
              <tr
                v-for="transaction in transactionsStore.transactions"
                :key="transaction.id"
                class="hover:bg-muted/50"
              >
                <td
                  class="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground"
                >
                  {{ formatDateTime(transaction.inserted_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-foreground">
                  {{ transaction.account.name }}
                </td>
                <td
                  class="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground"
                >
                  {{ transaction.statement_file.original_filename }}
                </td>
                <td
                  v-for="col in visibleIngestedColumns"
                  :key="col.name"
                  class="px-6 py-4 whitespace-nowrap text-sm text-foreground"
                >
                  {{
                    formatValue(
                      transaction.ingested_content[col.name],
                      getColumnType(col.name),
                    )
                  }}
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="bg-card px-4 py-3 border-t border-border sm:px-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <span class="text-sm text-foreground">
              Showing
              <select
                v-model="transactionsStore.pageSize"
                @change="
                  transactionsStore.setPageSize(transactionsStore.pageSize)
                "
                class="mx-1 px-2 py-1 border border-input rounded bg-background text-foreground"
              >
                <option :value="25">25</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
              </select>
              per page
            </span>
            <span class="text-sm text-foreground">
              Page {{ transactionsStore.currentPage }} of
              {{ transactionsStore.totalPages }} (Total:
              {{ transactionsStore.totalCount.toLocaleString() }})
            </span>
          </div>
          <div class="flex gap-2">
            <Button
              @click="
                transactionsStore.setPage(transactionsStore.currentPage - 1)
              "
              :disabled="transactionsStore.currentPage === 1"
              variant="outline"
              size="sm"
            >
              Previous
            </Button>
            <Button
              @click="
                transactionsStore.setPage(transactionsStore.currentPage + 1)
              "
              :disabled="
                transactionsStore.currentPage >= transactionsStore.totalPages
              "
              variant="outline"
              size="sm"
            >
              Next
            </Button>
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
        class="bg-card rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
        @click.stop
      >
        <h3 class="text-lg font-semibold text-foreground mb-4">
          Column Settings
        </h3>
        <p class="text-sm text-muted-foreground mb-4">
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
              class="w-4 h-4 text-primary border-input rounded focus:ring-ring"
            />
            <label
              :for="`col-${col.name}`"
              class="text-sm text-foreground cursor-pointer"
            >
              {{ col.name }}
              <span class="text-xs text-muted-foreground"
                >({{ col.type }})</span
              >
            </label>
          </div>
        </div>
        <div class="mt-6 flex justify-end gap-2">
          <Button
            @click="transactionsStore.setDefaultVisibleColumns()"
            variant="outline"
            size="sm"
          >
            Show All
          </Button>
          <Button @click="showColumnChooser = false" size="sm"> Done </Button>
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
        class="bg-card rounded-lg shadow-xl p-6 max-w-md w-full mx-4"
        @click.stop
      >
        <h3 class="text-lg font-semibold text-foreground mb-4">Add Filter</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-foreground mb-1">
              Field
            </label>
            <select
              v-model="currentFilter!.field"
              class="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
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
            <label class="block text-sm font-medium text-foreground mb-1">
              Operator
            </label>
            <select
              v-model="currentFilter!.operator"
              class="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
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
            <label class="block text-sm font-medium text-foreground mb-1">
              Value
            </label>
            <input
              v-model="currentFilter!.value"
              type="text"
              class="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
              placeholder="Enter value..."
            />
          </div>
        </div>
        <div class="mt-6 flex justify-end gap-2">
          <Button @click="showFilterDialog = false" variant="outline" size="sm">
            Cancel
          </Button>
          <Button @click="applyFilter" size="sm"> Apply </Button>
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
        class="bg-card rounded-lg shadow-xl p-6 max-w-md w-full mx-4"
        @click.stop
      >
        <h3 class="text-lg font-semibold text-foreground mb-4">
          Remove All Transactions
        </h3>
        <p class="text-muted-foreground mb-6">
          {{
            transactionsStore.selectedAccountId
              ? `Are you sure you want to delete all transactions for the selected account? This action cannot be undone.`
              : `Are you sure you want to delete ALL transactions? This action cannot be undone.`
          }}
        </p>
        <div class="flex justify-end gap-3">
          <Button
            @click="showDeleteConfirm = false"
            variant="outline"
            size="sm"
          >
            Cancel
          </Button>
          <Button @click="handleDeleteAll" variant="destructive" size="sm">
            Delete
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
