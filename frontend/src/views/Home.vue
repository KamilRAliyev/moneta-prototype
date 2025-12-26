<script setup lang="ts">
import { ref, onMounted } from "vue";
import HelloWorld from "../components/HelloWorld.vue";
import { healthService } from "../services";
import type { HealthInfo } from "../services/health";

const healthStatus = ref<HealthInfo | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);

const checkHealth = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    healthStatus.value = await healthService.getHealth();
  } catch (err) {
    error.value = "Failed to connect to API";
    console.error("Health check error:", err);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  checkHealth();
});
</script>

<template>
  <div class="space-y-8">
    <!-- Welcome Section -->
    <div class="text-center">
      <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-4">
        Welcome to Moneta
      </h1>
      <p class="text-lg text-gray-600 dark:text-gray-400">
        Personal finance management application
      </p>
    </div>

    <!-- API Health Check -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
        API Status
      </h2>
      <div class="space-y-4">
        <button
          @click="checkHealth"
          :disabled="isLoading"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ isLoading ? "Checking..." : "Check Health" }}
        </button>

        <div v-if="error" class="text-red-600 dark:text-red-400">
          {{ error }}
        </div>

        <div v-if="healthStatus" class="space-y-2">
          <div class="flex items-center space-x-2">
            <span
              class="w-3 h-3 rounded-full"
              :class="healthStatus.ok ? 'bg-green-500' : 'bg-red-500'"
            ></span>
            <span class="text-gray-700 dark:text-gray-300">
              Status: {{ healthStatus.ok ? "Healthy" : "Unhealthy" }}
            </span>
          </div>
          <div
            v-if="healthStatus.version"
            class="text-sm text-gray-600 dark:text-gray-400"
          >
            Version: {{ healthStatus.version }}
          </div>
          <div
            v-if="healthStatus.timestamp"
            class="text-sm text-gray-600 dark:text-gray-400"
          >
            Timestamp: {{ healthStatus.timestamp }}
          </div>
        </div>
      </div>
    </div>

    <!-- Example Component -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <HelloWorld msg="Vite + Vue" />
    </div>
  </div>
</template>
