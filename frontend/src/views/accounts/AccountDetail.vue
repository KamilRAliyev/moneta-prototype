<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { accountsService } from "../../services/accounts";
import AccountForm from "../../components/accounts/AccountForm.vue";
import type { Account, AccountUpdateRequest } from "../../types/accounts";

const router = useRouter();
const route = useRoute();

const account = ref<Account | null>(null);
const isLoading = ref(false);
const isSaving = ref(false);
const error = ref<string | null>(null);

const loadAccount = async () => {
  const id = Number(route.params.id);
  if (isNaN(id)) {
    error.value = "Invalid account ID";
    return;
  }

  isLoading.value = true;
  error.value = null;

  try {
    account.value = await accountsService.getAccount(id);
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Failed to load account";
    console.error("Failed to load account:", err);
  } finally {
    isLoading.value = false;
  }
};

const handleSubmit = async (payload: AccountUpdateRequest) => {
  if (!account.value) return;

  isSaving.value = true;
  error.value = null;

  try {
    account.value = await accountsService.updateAccount(
      account.value.id,
      payload,
    );
    // Optionally show success message or navigate
  } catch (err) {
    error.value =
      err instanceof Error ? err.message : "Failed to update account";
    console.error("Failed to update account:", err);
  } finally {
    isSaving.value = false;
  }
};

const handleCancel = () => {
  router.push("/accounts");
};

onMounted(() => {
  loadAccount();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          {{ account ? account.name : "Account Details" }}
        </h1>
        <p v-if="account" class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          {{ account.institution }} • {{ account.currency }}
        </p>
      </div>
      <router-link
        to="/accounts"
        class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
      >
        ← Back to Accounts
      </router-link>
    </div>

    <!-- Loading State -->
    <div
      v-if="isLoading"
      class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 text-center"
    >
      <p class="text-gray-600 dark:text-gray-400">Loading account...</p>
    </div>

    <!-- Error State -->
    <div
      v-else-if="error && !account"
      class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6"
    >
      <p class="text-sm text-red-800 dark:text-red-200">
        {{ error }}
      </p>
    </div>

    <!-- Form -->
    <div
      v-else-if="account"
      class="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
    >
      <AccountForm
        :account="account"
        :is-loading="isSaving"
        :error="error"
        @submit="handleSubmit"
        @cancel="handleCancel"
      />
    </div>
  </div>
</template>
