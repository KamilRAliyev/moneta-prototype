<script setup lang="ts">
import { computed } from "vue";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
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
      <Button @click="emit('ingest-all')" :disabled="isLoading">
        Ingest All ({{ nonIngestedStatements.length }})
      </Button>
    </div>

    <div class="-mx-4 sm:mx-0">
      <div class="overflow-x-auto">
        <table class="w-full divide-y divide-border bg-card shadow rounded-lg">
          <thead class="bg-card border-b border-border">
            <tr>
              <th
                scope="col"
                class="px-3 py-2 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap"
              >
                Uploaded At
              </th>
              <th
                scope="col"
                class="px-3 py-2 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider"
              >
                Filename
              </th>
              <th
                scope="col"
                class="px-3 py-2 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider"
              >
                Account
              </th>
              <th
                scope="col"
                class="px-3 py-2 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap"
              >
                Size
              </th>
              <th
                scope="col"
                class="px-3 py-2 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap"
              >
                Rows
              </th>
              <th
                scope="col"
                class="px-3 py-2 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider"
              >
                Date Range
              </th>
              <th
                scope="col"
                class="px-3 py-2 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap"
              >
                Status
              </th>
              <th
                scope="col"
                class="px-3 py-2 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap"
              >
                Ingested
              </th>
              <th
                scope="col"
                class="px-3 py-2 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap"
              >
                File
              </th>
              <th
                scope="col"
                class="px-3 py-2 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap"
              >
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-card divide-y divide-border">
            <template v-if="props.isLoading">
              <tr
                v-for="i in 5"
                :key="`skeleton-${i}`"
                class="hover:bg-muted/50"
              >
                <td class="px-3 py-2">
                  <Skeleton class="h-4 w-32" />
                </td>
                <td class="px-3 py-2">
                  <Skeleton class="h-4 w-40" />
                </td>
                <td class="px-3 py-2">
                  <Skeleton class="h-4 w-24" />
                </td>
                <td class="px-3 py-2">
                  <Skeleton class="h-4 w-16" />
                </td>
                <td class="px-3 py-2">
                  <Skeleton class="h-4 w-12" />
                </td>
                <td class="px-3 py-2">
                  <Skeleton class="h-4 w-28" />
                </td>
                <td class="px-3 py-2">
                  <Skeleton class="h-4 w-20" />
                </td>
                <td class="px-3 py-2">
                  <Skeleton class="h-4 w-24" />
                </td>
                <td class="px-3 py-2">
                  <Skeleton class="h-4 w-16" />
                </td>
                <td class="px-3 py-2 text-right">
                  <div class="flex justify-end gap-2">
                    <Skeleton class="h-8 w-16" />
                    <Skeleton class="h-8 w-16" />
                  </div>
                </td>
              </tr>
            </template>
            <template v-else-if="props.statements.length === 0">
              <tr class="text-center">
                <td
                  colspan="10"
                  class="px-6 py-4 text-sm text-muted-foreground"
                >
                  No statements found. Upload your first statement to get
                  started.
                </td>
              </tr>
            </template>
            <template v-else>
              <tr
                v-for="statement in props.statements"
                :key="statement.id"
                class="hover:bg-muted/50 transition-colors"
              >
                <td
                  class="px-3 py-2 whitespace-nowrap text-sm text-muted-foreground"
                >
                  {{ formatDateTime(statement.created_at) }}
                </td>
                <td
                  class="px-3 py-2 text-sm font-medium text-foreground max-w-xs truncate"
                >
                  {{ statement.original_filename }}
                </td>
                <td
                  class="px-3 py-2 text-sm text-muted-foreground max-w-[120px] truncate"
                >
                  {{
                    statement.account_name || `Account #${statement.account_id}`
                  }}
                </td>
                <td
                  class="px-3 py-2 whitespace-nowrap text-sm text-muted-foreground"
                >
                  {{ formatFileSize(statement.size_bytes) }}
                </td>
                <td
                  class="px-3 py-2 whitespace-nowrap text-sm text-muted-foreground"
                >
                  {{ statement.row_count.toLocaleString() }}
                </td>
                <td
                  class="px-3 py-2 text-sm text-muted-foreground max-w-[140px] truncate"
                >
                  {{ formatDateRange(statement.date_from, statement.date_to) }}
                </td>
                <td class="px-3 py-2 whitespace-nowrap text-sm">
                  <span
                    class="px-2 py-1 text-xs font-medium rounded-full"
                    :class="
                      statement.status === 'uploaded'
                        ? 'bg-primary/10 text-primary'
                        : 'bg-muted text-muted-foreground'
                    "
                  >
                    {{ statement.status }}
                  </span>
                </td>
                <td class="px-3 py-2 whitespace-nowrap text-sm">
                  <span
                    v-if="statement.is_ingested"
                    class="px-2 py-1 text-xs font-medium rounded-full"
                    :class="
                      (statement.ingestion_errors_count ?? 0) > 0
                        ? 'bg-destructive/10 text-destructive'
                        : statement.ingested_rows_count === statement.row_count
                          ? 'bg-green-500/10 text-green-600 dark:text-green-400'
                          : 'bg-yellow-500/10 text-yellow-600 dark:text-yellow-400'
                    "
                    :title="formatIngestionStatus(statement)"
                  >
                    {{ formatIngestionStatus(statement) }}
                  </span>
                  <span
                    v-else
                    class="px-2 py-1 text-xs font-medium rounded-full bg-yellow-500/10 text-yellow-600 dark:text-yellow-400"
                  >
                    ⏳ Not ingested
                  </span>
                </td>
                <td class="px-3 py-2 whitespace-nowrap text-sm">
                  <span
                    v-if="statement.file_exists"
                    class="px-2 py-1 text-xs font-medium rounded-full bg-green-500/10 text-green-600 dark:text-green-400"
                    title="File exists on disk"
                  >
                    ✓ Exists
                  </span>
                  <span
                    v-else
                    class="px-2 py-1 text-xs font-medium rounded-full bg-destructive/10 text-destructive"
                    title="File missing from disk"
                  >
                    ✗ Missing
                  </span>
                </td>
                <td
                  class="px-3 py-2 whitespace-nowrap text-right text-sm font-medium space-x-2"
                >
                  <div class="flex justify-end gap-2">
                    <Button
                      v-if="!statement.is_ingested"
                      @click="emit('ingest', statement.id)"
                      :disabled="isLoading"
                      size="sm"
                    >
                      Ingest
                    </Button>
                    <Button
                      @click="emit('delete', statement)"
                      variant="ghost"
                      size="sm"
                      class="text-destructive hover:text-destructive"
                    >
                      Delete
                    </Button>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
