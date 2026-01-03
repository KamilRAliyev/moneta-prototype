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

const handleIngest = async (statementId: string) => {
  try {
    const result = await store.ingestStatement(statementId);
    // Show success message or handle errors
    if (result.summary.errors > 0) {
      console.warn(
        `Ingestion completed with ${result.summary.errors} errors`,
        result.errors,
      );
      // TODO: Show error modal or toast notification
    } else {
      // TODO: Show success message
      console.log("Ingestion completed successfully", result);
    }
  } catch (err: any) {
    // Error is handled in the store, but show user-friendly message
    const errorMessage =
      err?.response?.data?.detail ||
      err?.message ||
      "Failed to ingest statement. Please check the console for details.";
    console.error("Ingestion failed:", err);
    alert(`Ingestion failed: ${errorMessage}`);
  }
};

const handleIngestAll = async () => {
  const nonIngested = store.statements.filter((s) => !s.is_ingested);
  if (nonIngested.length === 0) return;

  try {
    const statementIds = nonIngested.map((s) => s.id);
    const results = await store.ingestAllStatements(statementIds);
    // Show summary or handle errors
    const totalErrors = results.reduce((sum, r) => sum + r.summary.errors, 0);
    if (totalErrors > 0) {
      console.warn(`Bulk ingestion completed with ${totalErrors} total errors`);
    }
  } catch (err) {
    // Error is handled in the store
    console.error("Bulk ingestion failed:", err);
  }
};

onMounted(() => {
  store.loadStatements();
});
</script>

<template>
  <div class="space-y-6 w-full">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold text-foreground">Statements</h1>
      <p class="mt-2 text-sm text-muted-foreground">
        Upload and manage CSV statement files for your accounts
      </p>
    </div>

    <!-- Error Message -->
    <div
      v-if="store.error"
      class="p-4 bg-destructive/10 border border-destructive/20 rounded-md"
    >
      <p class="text-sm text-destructive">
        {{ store.error }}
      </p>
    </div>

    <!-- Upload Section -->
    <div class="bg-card shadow rounded-lg p-6">
      <h2 class="text-xl font-semibold text-foreground mb-4">
        Upload Statement
      </h2>
      <StatementUpload
        :is-loading="store.isLoading"
        :error="store.error"
        @upload="handleUpload"
      />
    </div>

    <!-- Statements Table -->
    <div class="bg-card shadow rounded-lg p-6">
      <h2 class="text-xl font-semibold text-foreground mb-4">
        Uploaded Statements
      </h2>
      <StatementTable
        :statements="store.statements"
        :is-loading="store.isLoading"
        @delete="handleDelete"
        @ingest="handleIngest"
        @ingest-all="handleIngestAll"
      />
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="deleteConfirmId"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="cancelDelete"
    >
      <div
        class="bg-card rounded-lg shadow-xl p-6 max-w-md w-full mx-4"
        @click.stop
      >
        <h3 class="text-lg font-semibold text-foreground mb-4">
          Delete Statement
        </h3>
        <p class="text-muted-foreground mb-6">
          Are you sure you want to delete this statement file? This action
          cannot be undone and will also delete the file from the server.
        </p>
        <div class="flex justify-end gap-3">
          <Button @click="cancelDelete" variant="outline" size="sm">
            Cancel
          </Button>
          <Button @click="confirmDelete" variant="destructive" size="sm">
            Delete
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
