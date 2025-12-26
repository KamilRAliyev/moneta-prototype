<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { accountsService } from "../../services/accounts";
import AccountForm from "../../components/accounts/AccountForm.vue";
import type { AccountCreateRequest } from "../../types/accounts";

const router = useRouter();

const isLoading = ref(false);
const error = ref<string | null>(null);

const handleSubmit = async (payload: AccountCreateRequest) => {
  isLoading.value = true;
  error.value = null;

  try {
    const account = await accountsService.createAccount(payload);
    // Navigate to the new account's detail page
    router.push(`/accounts/${account.id}`);
  } catch (err) {
    error.value =
      err instanceof Error ? err.message : "Failed to create account";
    console.error("Failed to create account:", err);
  } finally {
    isLoading.value = false;
  }
};

const handleCancel = () => {
  router.push("/accounts");
};
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        Create Account
      </h1>
      <router-link
        to="/accounts"
        class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
      >
        ← Back to Accounts
      </router-link>
    </div>

    <!-- Form -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <AccountForm
        :is-loading="isLoading"
        :error="error"
        @submit="handleSubmit"
        @cancel="handleCancel"
      />
    </div>
  </div>
</template>
