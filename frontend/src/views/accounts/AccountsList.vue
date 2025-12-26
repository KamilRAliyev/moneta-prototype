<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { accountsService } from "../../services/accounts";
import AccountTable from "../../components/accounts/AccountTable.vue";
import type { Account } from "../../types/accounts";

const router = useRouter();

const accounts = ref<Account[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);
const deleteConfirmId = ref<number | null>(null);

const loadAccounts = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    accounts.value = await accountsService.listAccounts();
  } catch (err) {
    error.value =
      err instanceof Error ? err.message : "Failed to load accounts";
    console.error("Failed to load accounts:", err);
  } finally {
    isLoading.value = false;
  }
};

const handleView = (account: Account) => {
  router.push(`/accounts/${account.id}`);
};

const handleEdit = (account: Account) => {
  router.push(`/accounts/${account.id}`);
};

const handleDelete = (account: Account) => {
  deleteConfirmId.value = account.id;
};

const confirmDelete = async () => {
  if (!deleteConfirmId.value) return;

  try {
    await accountsService.deleteAccount(deleteConfirmId.value);
    deleteConfirmId.value = null;
    await loadAccounts(); // Reload list
  } catch (err) {
    error.value =
      err instanceof Error ? err.message : "Failed to delete account";
    console.error("Failed to delete account:", err);
  }
};

const cancelDelete = () => {
  deleteConfirmId.value = null;
};

onMounted(() => {
  loadAccounts();
});
</script>

<template>
  <div class="space-y-6 w-full">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Accounts</h1>
      <router-link
        to="/accounts/new"
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
      >
        Create Account
      </router-link>
    </div>

    <!-- Error Message -->
    <div
      v-if="error"
      class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md"
    >
      <p class="text-sm text-red-800 dark:text-red-200">
        {{ error }}
      </p>
    </div>

    <!-- Accounts Table -->
    <AccountTable
      :accounts="accounts"
      :is-loading="isLoading"
      @view="handleView"
      @edit="handleEdit"
      @delete="handleDelete"
    />

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
          Delete Account
        </h3>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          Are you sure you want to delete this account? This action cannot be
          undone.
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
