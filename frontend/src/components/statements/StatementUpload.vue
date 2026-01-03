<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Button } from "@/components/ui/button";
import { X } from "lucide-vue-next";
import { accountsService } from "../../services/accounts";
import type { Account } from "../../types/accounts";

interface Props {
  isLoading?: boolean;
  error?: string | null;
}

interface Emits {
  (e: "upload", file: File, accountId: number): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// State
const selectedAccountId = ref<number | null>(null);
const selectedFile = ref<File | null>(null);
const isDragging = ref(false);
const accounts = ref<Account[]>([]);
const isLoadingAccounts = ref(false);
const errors = ref<Record<string, string>>({});

// Load accounts for dropdown
onMounted(async () => {
  isLoadingAccounts.value = true;
  try {
    accounts.value = await accountsService.listAccounts();
  } catch (err) {
    console.error("Failed to load accounts:", err);
  } finally {
    isLoadingAccounts.value = false;
  }
});

// Drag and drop handlers
const handleDragEnter = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = true;
};

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = false;
};

const handleDragOver = (e: DragEvent) => {
  e.preventDefault();
};

const handleDrop = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = false;

  const files = e.dataTransfer?.files;
  if (files && files.length > 0) {
    handleFileSelect(files[0]);
  }
};

const handleFileInput = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    handleFileSelect(target.files[0]);
  }
};

const handleFileSelect = (file: File) => {
  // Validate file type
  if (!file.name.toLowerCase().endsWith(".csv")) {
    errors.value.file = "Only CSV files are allowed";
    selectedFile.value = null;
    return;
  }

  // Validate file size (50MB limit)
  const maxSize = 50 * 1024 * 1024; // 50MB
  if (file.size > maxSize) {
    errors.value.file = "File size must be less than 50MB";
    selectedFile.value = null;
    return;
  }

  errors.value.file = "";
  selectedFile.value = file;
};

const handleUpload = () => {
  errors.value = {};

  // Validate account selection
  if (!selectedAccountId.value) {
    errors.value.account = "Please select an account";
    return;
  }

  // Validate file selection
  if (!selectedFile.value) {
    errors.value.file = "Please select a CSV file";
    return;
  }

  emit("upload", selectedFile.value, selectedAccountId.value);
};

const clearFile = () => {
  selectedFile.value = null;
  errors.value.file = "";
};
</script>

<template>
  <div class="space-y-6">
    <!-- Account Selection -->
    <div>
      <label
        for="account"
        class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
      >
        Account <span class="text-red-500">*</span>
      </label>
      <select
        id="account"
        v-model="selectedAccountId"
        :disabled="isLoadingAccounts || props.isLoading"
        class="block w-full px-3 py-2 border border-input rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-ring focus:border-ring bg-background text-foreground"
        :class="{ 'border-red-500': errors.account }"
      >
        <option :value="null">Select an account...</option>
        <option
          v-for="account in accounts"
          :key="account.id"
          :value="account.id"
        >
          {{ account.name }} ({{ account.institution }})
        </option>
      </select>
      <p v-if="errors.account" class="mt-1 text-sm text-destructive">
        {{ errors.account }}
      </p>
    </div>

    <!-- File Upload Area -->
    <div>
      <label
        class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
      >
        CSV File <span class="text-red-500">*</span>
      </label>
      <div
        @dragenter="handleDragEnter"
        @dragleave="handleDragLeave"
        @dragover="handleDragOver"
        @drop="handleDrop"
        class="border-2 border-dashed rounded-lg p-8 text-center transition-colors"
        :class="
          isDragging
            ? 'border-primary bg-primary/10'
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
        "
      >
        <input
          type="file"
          accept=".csv"
          @change="handleFileInput"
          class="hidden"
          id="file-input"
          :disabled="props.isLoading"
        />
        <label
          for="file-input"
          class="cursor-pointer"
          :class="{ 'pointer-events-none opacity-50': props.isLoading }"
        >
          <svg
            class="mx-auto h-12 w-12 text-muted-foreground"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
          <p class="mt-2 text-sm text-muted-foreground">
            <span class="font-medium text-primary">Click to upload</span>
            or drag and drop
          </p>
          <p class="mt-1 text-xs text-muted-foreground">
            CSV files only (max 50MB)
          </p>
        </label>
      </div>

      <!-- Selected File Display -->
      <div
        v-if="selectedFile"
        class="mt-4 p-4 bg-muted rounded-md flex items-center justify-between"
      >
        <div class="flex items-center gap-3">
          <svg
            class="h-5 w-5 text-green-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div>
            <p class="text-sm font-medium text-foreground">
              {{ selectedFile.name }}
            </p>
            <p class="text-xs text-muted-foreground">
              {{ (selectedFile.size / 1024).toFixed(2) }} KB
            </p>
          </div>
        </div>
        <Button
          @click="clearFile"
          type="button"
          variant="ghost"
          size="icon"
          :disabled="props.isLoading"
          class="text-destructive hover:text-destructive"
        >
          <X class="h-4 w-4" />
        </Button>
      </div>

      <p v-if="errors.file" class="mt-1 text-sm text-red-600 dark:text-red-400">
        {{ errors.file }}
      </p>
    </div>

    <!-- Error Message -->
    <div
      v-if="props.error"
      class="p-4 bg-destructive/10 border border-destructive/20 rounded-md"
    >
      <p class="text-sm text-destructive">
        {{ props.error }}
      </p>
    </div>

    <!-- Upload Button -->
    <div class="flex justify-end">
      <Button
        @click="handleUpload"
        :disabled="props.isLoading || !selectedFile || !selectedAccountId"
      >
        {{ props.isLoading ? "Uploading..." : "Upload Statement" }}
      </Button>
    </div>
  </div>
</template>
