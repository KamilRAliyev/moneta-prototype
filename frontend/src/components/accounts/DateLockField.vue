<script setup lang="ts">
import { computed } from "vue";

interface Props {
  datelockFrom: string | null;
  datelockTo: string | null;
  error?: string;
}

interface Emits {
  (e: "update:datelockFrom", value: string | null): void;
  (e: "update:datelockTo", value: string | null): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const dateFromValue = computed({
  get: () => props.datelockFrom || "",
  set: (value: string) => {
    emit("update:datelockFrom", value || null);
  },
});

const dateToValue = computed({
  get: () => props.datelockTo || "",
  set: (value: string) => {
    emit("update:datelockTo", value || null);
  },
});

const clearFrom = () => {
  emit("update:datelockFrom", null);
};

const clearTo = () => {
  emit("update:datelockTo", null);
};

const hasFrom = computed(() => !!props.datelockFrom);
const hasTo = computed(() => !!props.datelockTo);

// Compute min date for "to" field (must be >= from)
const minDateTo = computed(() => props.datelockFrom || undefined);
// Compute max date for "from" field (must be <= to)
const maxDateFrom = computed(() => props.datelockTo || undefined);
</script>

<template>
  <div class="space-y-2">
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      Date Lock Range
    </label>

    <div class="space-y-3">
      <!-- Date Lock From -->
      <div>
        <label
          for="datelock_from"
          class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1"
        >
          From Date (transactions on or after this date are already ingested and
          will be skipped)
        </label>
        <div class="flex gap-2">
          <input
            id="datelock_from"
            v-model="dateFromValue"
            type="date"
            :max="maxDateFrom"
            class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            :class="{
              'border-red-500': props.error,
            }"
          />
          <button
            v-if="hasFrom"
            type="button"
            @click="clearFrom"
            class="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      <!-- Date Lock To -->
      <div>
        <label
          for="datelock_to"
          class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1"
        >
          To Date (transactions on or before this date are already ingested and
          will be skipped)
        </label>
        <div class="flex gap-2">
          <input
            id="datelock_to"
            v-model="dateToValue"
            type="date"
            :min="minDateTo"
            class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            :class="{
              'border-red-500': props.error,
            }"
          />
          <button
            v-if="hasTo"
            type="button"
            @click="clearTo"
            class="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          >
            Clear
          </button>
        </div>
      </div>
    </div>

    <p v-if="props.error" class="text-sm text-red-600 dark:text-red-400">
      {{ props.error }}
    </p>

    <p class="text-xs text-gray-500 dark:text-gray-400">
      <strong>Date Lock Range:</strong> This range marks dates that have already
      been ingested. Transactions within this range (inclusive) will be skipped.
      Transactions outside this range will be ingested. Leave both empty if no
      dates have been ingested yet. If only one is set, it acts as a one-sided
      lock.
    </p>
  </div>
</template>
