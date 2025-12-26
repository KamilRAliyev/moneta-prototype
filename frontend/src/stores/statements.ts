import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { statementsService } from "../services/statements";
import type { StatementFileSummary } from "../types/statements";

export const useStatementsStore = defineStore("statements", () => {
  // State
  const statements = ref<StatementFileSummary[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const selectedAccountId = ref<number | undefined>(undefined);

  // Getters
  const statementsByAccount = computed(() => {
    if (!selectedAccountId.value) {
      return statements.value;
    }
    return statements.value.filter(
      (s) => s.account_id === selectedAccountId.value,
    );
  });

  const hasStatements = computed(() => statements.value.length > 0);

  // Actions
  async function loadStatements(accountId?: number, skip = 0, limit = 100) {
    isLoading.value = true;
    error.value = null;
    try {
      statements.value = await statementsService.listStatements(
        accountId,
        skip,
        limit,
      );
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Failed to load statements";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function uploadStatement(file: File, accountId: number) {
    isLoading.value = true;
    error.value = null;
    try {
      const newStatement = await statementsService.uploadStatement(
        file,
        accountId,
      );
      // Reload statements to include the new one
      await loadStatements(selectedAccountId.value);
      return newStatement;
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Failed to upload statement";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteStatement(id: string) {
    isLoading.value = true;
    error.value = null;
    try {
      await statementsService.deleteStatement(id);
      // Remove from local state
      statements.value = statements.value.filter((s) => s.id !== id);
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Failed to delete statement";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function setSelectedAccount(accountId: number | undefined) {
    selectedAccountId.value = accountId;
  }

  function clearError() {
    error.value = null;
  }

  function reset() {
    statements.value = [];
    isLoading.value = false;
    error.value = null;
    selectedAccountId.value = undefined;
  }

  return {
    // State
    statements,
    isLoading,
    error,
    selectedAccountId,
    // Getters
    statementsByAccount,
    hasStatements,
    // Actions
    loadStatements,
    uploadStatement,
    deleteStatement,
    setSelectedAccount,
    clearError,
    reset,
  };
});
