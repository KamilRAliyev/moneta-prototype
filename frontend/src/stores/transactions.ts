import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { transactionsService } from "../services/transactions";
import type {
  Transaction,
  TransactionMetaResponse,
} from "../types/transactions";

export const useTransactionsStore = defineStore("transactions", () => {
  // State
  const transactions = ref<Transaction[]>([]);
  const meta = ref<TransactionMetaResponse | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Pagination state
  const currentPage = ref(1);
  const pageSize = ref(50);
  const totalCount = ref(0);
  const totalPages = ref(0);

  // Filtering state
  const selectedAccountId = ref<number | undefined>(undefined);
  const selectedStatementFileId = ref<string | undefined>(undefined);
  const filters = ref<string>("");

  // Sorting state
  const sortBy = ref<string>("inserted_at");
  const sortDir = ref<"asc" | "desc">("desc");

  // Column visibility state (from localStorage)
  const visibleColumns = ref<Set<string>>(new Set());

  // Getters
  const hasTransactions = computed(() => transactions.value.length > 0);

  const ingestedColumns = computed(() => {
    return meta.value?.ingested_columns ?? [];
  });

  const computedColumns = computed(() => {
    return meta.value?.computed_columns ?? [];
  });

  const allColumns = computed(() => {
    return [...ingestedColumns.value, ...computedColumns.value];
  });

  // Actions
  async function loadTransactions() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await transactionsService.listTransactions({
        account_id: selectedAccountId.value,
        statement_file_id: selectedStatementFileId.value,
        page: currentPage.value,
        page_size: pageSize.value,
        sort_by: sortBy.value,
        sort_dir: sortDir.value,
        filters: filters.value || undefined,
      });
      transactions.value = response.items;
      totalCount.value = response.meta.total;
      totalPages.value = response.meta.total_pages;
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Failed to load transactions";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function loadMeta() {
    try {
      meta.value = await transactionsService.getTransactionMeta(
        selectedAccountId.value,
      );
      // Initialize visible columns from localStorage or default to all
      initializeVisibleColumns();
    } catch (err) {
      error.value =
        err instanceof Error
          ? err.message
          : "Failed to load transaction metadata";
      throw err;
    }
  }

  function initializeVisibleColumns() {
    const stored = localStorage.getItem(
      `transactions_visible_columns_${selectedAccountId.value ?? "all"}`,
    );
    if (stored) {
      try {
        visibleColumns.value = new Set(JSON.parse(stored));
      } catch {
        // Invalid stored data, use default
        setDefaultVisibleColumns();
      }
    } else {
      setDefaultVisibleColumns();
    }
  }

  function setDefaultVisibleColumns() {
    // Show all ingested columns by default
    visibleColumns.value = new Set(
      ingestedColumns.value.map((col) => col.name),
    );
    saveVisibleColumns();
  }

  function saveVisibleColumns() {
    localStorage.setItem(
      `transactions_visible_columns_${selectedAccountId.value ?? "all"}`,
      JSON.stringify(Array.from(visibleColumns.value)),
    );
  }

  function toggleColumn(columnName: string) {
    if (visibleColumns.value.has(columnName)) {
      visibleColumns.value.delete(columnName);
    } else {
      visibleColumns.value.add(columnName);
    }
    saveVisibleColumns();
  }

  function setPage(page: number) {
    currentPage.value = page;
    loadTransactions();
  }

  function setPageSize(size: number) {
    pageSize.value = size;
    currentPage.value = 1; // Reset to first page
    loadTransactions();
  }

  function setSort(field: string, direction: "asc" | "desc" = "desc") {
    sortBy.value = field;
    sortDir.value = direction;
    currentPage.value = 1; // Reset to first page
    loadTransactions();
  }

  function setAccount(accountId: number | undefined) {
    selectedAccountId.value = accountId;
    currentPage.value = 1;
    initializeVisibleColumns();
    loadMeta();
    loadTransactions();
  }

  function setStatementFile(statementFileId: string | undefined) {
    selectedStatementFileId.value = statementFileId;
    currentPage.value = 1;
    loadTransactions();
  }

  function setFilters(filterString: string) {
    filters.value = filterString;
    currentPage.value = 1;
    loadTransactions();
  }

  async function deleteTransactions(accountId?: number): Promise<number> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await transactionsService.deleteTransactions(accountId);
      // Reload transactions
      await loadTransactions();
      return response.deleted_count;
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Failed to delete transactions";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function clearError() {
    error.value = null;
  }

  function reset() {
    transactions.value = [];
    meta.value = null;
    isLoading.value = false;
    error.value = null;
    currentPage.value = 1;
    pageSize.value = 50;
    totalCount.value = 0;
    totalPages.value = 0;
    selectedAccountId.value = undefined;
    selectedStatementFileId.value = undefined;
    filters.value = "";
    sortBy.value = "inserted_at";
    sortDir.value = "desc";
    visibleColumns.value = new Set();
  }

  return {
    // State
    transactions,
    meta,
    isLoading,
    error,
    currentPage,
    pageSize,
    totalCount,
    totalPages,
    selectedAccountId,
    selectedStatementFileId,
    filters,
    sortBy,
    sortDir,
    visibleColumns,
    // Getters
    hasTransactions,
    ingestedColumns,
    computedColumns,
    allColumns,
    // Actions
    loadTransactions,
    loadMeta,
    toggleColumn,
    setPage,
    setPageSize,
    setSort,
    setAccount,
    setStatementFile,
    setFilters,
    deleteTransactions,
    setDefaultVisibleColumns,
    clearError,
    reset,
  };
});
