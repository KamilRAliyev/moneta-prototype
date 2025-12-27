<script setup lang="ts">
import { computed } from "vue";
import type { StatementFileSummary } from "../../types/statements";

interface Props {
  statements: StatementFileSummary[];
  isLoading?: boolean;
}

interface Emits {
  (e: "delete", statement: StatementFileSummary): void;
  (e: "ingest", statementId: string): void;
  (e: "ingest-all"): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

const formatDate = (dateString: string | null): string => {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

const formatDateRange = (
  dateFrom: string | null,
  dateTo: string | null,
): string => {
  if (!dateFrom && !dateTo) return "-";
  if (dateFrom && dateTo) {
    return `${formatDate(dateFrom)} - ${formatDate(dateTo)}`;
  }
  return dateFrom
    ? `From ${formatDate(dateFrom)}`
    : `Until ${formatDate(dateTo)}`;
};

const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString();
};

const nonIngestedStatements = computed(() => {
  return props.statements.filter((s) => !s.is_ingested);
});

const formatIngestionStatus = (statement: StatementFileSummary): string => {
  if (!statement.is_ingested) {
    return "Not ingested";
  }
  const ingested = statement.ingested_rows_count ?? 0;
  const total = statement.row_count;
  const errors = statement.ingestion_errors_count ?? 0;

  if (errors > 0) {
    return `Ingested (${ingested}/${total}) – ${errors} errors`;
  }
  if (ingested === 0) {
    return `Ingested (0/${total}) – blocked by date lock`;
  }
  if (ingested < total) {
    return `Partial (${ingested}/${total})`;
  }
  return `Ingested (${ingested}/${total})`;
};
</script>

<template>
  <div class="space-y-4">
    <!-- Ingest All Button -->
    <div v-if="nonIngestedStatements.length > 0" class="flex justify-end">
      <button
        @click="emit('ingest-all')"
        :disabled="isLoading"
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        Ingest All ({{ nonIngestedStatements.length }})
      </button>
    </div>

    <div class="overflow-x-auto -mx-4 sm:mx-0">
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
              Uploaded At
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
            >
              Filename
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
            >
              Account
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
            >
              Size
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
            >
              Rows
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
            >
              Date Range
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
            >
              Status
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
            >
              Ingested
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
            >
              File
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
              colspan="10"
              class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400"
            >
              Loading statements...
            </td>
          </tr>
          <tr v-else-if="props.statements.length === 0" class="text-center">
            <td
              colspan="10"
              class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400"
            >
              No statements found. Upload your first statement to get started.
            </td>
          </tr>
          <tr
            v-for="statement in props.statements"
            :key="statement.id"
            class="hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors"
          >
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
            >
              {{ formatDateTime(statement.created_at) }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white"
            >
              {{ statement.original_filename }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
            >
              {{ statement.account_name || `Account #${statement.account_id}` }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
            >
              {{ formatFileSize(statement.size_bytes) }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
            >
              {{ statement.row_count.toLocaleString() }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
            >
              {{ formatDateRange(statement.date_from, statement.date_to) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span
                class="px-2 py-1 text-xs font-medium rounded-full"
                :class="
                  statement.status === 'uploaded'
                    ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                "
              >
                {{ statement.status }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span
                v-if="statement.is_ingested"
                class="px-2 py-1 text-xs font-medium rounded-full"
                :class="
                  (statement.ingestion_errors_count ?? 0) > 0
                    ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300'
                    : statement.ingested_rows_count === statement.row_count
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                      : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                "
                :title="formatIngestionStatus(statement)"
              >
                {{ formatIngestionStatus(statement) }}
              </span>
              <span
                v-else
                class="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300"
              >
                ⏳ Not ingested
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span
                v-if="statement.file_exists"
                class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300"
                title="File exists on disk"
              >
                ✓ Exists
              </span>
              <span
                v-else
                class="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300"
                title="File missing from disk"
              >
                ✗ Missing
              </span>
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2"
            >
              <button
                v-if="!statement.is_ingested"
                @click="emit('ingest', statement.id)"
                :disabled="isLoading"
                class="px-3 py-1 bg-blue-600 text-white text-xs rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                Ingest
              </button>
              <button
                @click="emit('delete', statement)"
                class="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300 transition-colors"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
