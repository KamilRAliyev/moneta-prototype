<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useStatementsStore } from "../../stores/statements";
import StatementUpload from "../../components/statements/StatementUpload.vue";
import StatementTable from "../../components/statements/StatementTable.vue";
import type { StatementFileSummary } from "../../types/statements";

const store = useStatementsStore();

const deleteConfirmId = ref<string | null>(null);

const handleUpload = async (file: File, accountId: number) => {
  try {
    await store.uploadStatement(file, accountId);
    // Success - statements are automatically reloaded in the store
  } catch (err) {
    // Error is handled in the store
    console.error("Upload failed:", err);
  }
};

const handleDelete = (statement: StatementFileSummary) => {
  deleteConfirmId.value = statement.id;
};

const confirmDelete = async () => {
  if (!deleteConfirmId.value) return;

  try {
    await store.deleteStatement(deleteConfirmId.value);
    deleteConfirmId.value = null;
  } catch (err) {
    // Error is handled in the store
    console.error("Delete failed:", err);
  }
};

const cancelDelete = () => {
  deleteConfirmId.value = null;
};

onMounted(() => {
  store.loadStatements();
});
</script>

<template>
  <div class="space-y-6 w-full">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        Statements
      </h1>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        Upload and manage CSV statement files for your accounts
      </p>
    </div>

    <!-- Error Message -->
    <div
      v-if="store.error"
      class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md"
    >
      <p class="text-sm text-red-800 dark:text-red-200">
        {{ store.error }}
      </p>
    </div>

    <!-- Upload Section -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
        Upload Statement
      </h2>
      <StatementUpload
        :is-loading="store.isLoading"
        :error="store.error"
        @upload="handleUpload"
      />
    </div>

    <!-- Statements Table -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
        Uploaded Statements
      </h2>
      <StatementTable
        :statements="store.statements"
        :is-loading="store.isLoading"
        @delete="handleDelete"
      />
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="deleteConfirmId"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="cancelDelete"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-md w-full mx-4"
        @click.stop
      >
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Delete Statement
        </h3>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          Are you sure you want to delete this statement file? This action
          cannot be undone and will also delete the file from the server.
        </p>
        <div class="flex justify-end gap-3">
          <button
            @click="cancelDelete"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="confirmDelete"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
