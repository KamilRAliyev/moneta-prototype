<script setup lang="ts">
import { computed } from "vue";

interface Props {
  modelValue: string | null;
  error?: string;
}

interface Emits {
  (e: "update:modelValue", value: string | null): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const dateValue = computed({
  get: () => props.modelValue || "",
  set: (value: string) => {
    emit("update:modelValue", value || null);
  },
});

const clearLock = () => {
  emit("update:modelValue", null);
};

const hasLock = computed(() => !!props.modelValue);
</script>

<template>
  <div class="space-y-2">
    <label
      for="datelock_from"
      class="block text-sm font-medium text-gray-700 dark:text-gray-300"
    >
      Date Lock
    </label>

    <div class="flex gap-2">
      <input
        id="datelock_from"
        v-model="dateValue"
        type="date"
        class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
        :class="{
          'border-red-500': props.error,
        }"
      />
      <button
        v-if="hasLock"
        type="button"
        @click="clearLock"
        class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
      >
        Clear
      </button>
    </div>

    <p v-if="props.error" class="text-sm text-red-600 dark:text-red-400">
      {{ props.error }}
    </p>

    <p class="text-xs text-gray-500 dark:text-gray-400">
      <strong>Date Lock:</strong> Transactions before this date will not be
      ingested or reprocessed for this account. Leave empty to allow full
      historical ingestion.
    </p>
  </div>
</template>
