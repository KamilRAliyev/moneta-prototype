<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-50 flex flex-col gap-2">
      <TransitionGroup
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 translate-x-full"
        enter-to-class="opacity-100 translate-x-0"
        leave-active-class="transition-all duration-300 ease-in"
        leave-from-class="opacity-100 translate-x-0"
        leave-to-class="opacity-0 translate-x-full"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'px-4 py-3 rounded-lg shadow-lg border max-w-sm',
            getToastClasses(toast.type),
          ]"
        >
          <div class="flex items-start gap-3">
            <component
              :is="getToastIcon(toast.type)"
              class="w-5 h-5 flex-shrink-0 mt-0.5"
            />
            <div class="flex-1">
              <p class="font-medium text-sm">{{ toast.title }}</p>
              <p v-if="toast.message" class="text-sm mt-1 opacity-90">
                {{ toast.message }}
              </p>
            </div>
            <button @click="removeToast(toast.id)" class="flex-shrink-0">
              <X class="w-4 h-4" />
            </button>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { X, CheckCircle2, AlertCircle, Info } from "lucide-vue-next";
import type { Component } from "vue";

const toasts = ref([]);

const getToastClasses = (type) => {
  const classes = {
    success:
      "bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800 text-green-900 dark:text-green-100",
    error:
      "bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800 text-red-900 dark:text-red-100",
    warning:
      "bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800 text-yellow-900 dark:text-yellow-100",
    info: "bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800 text-blue-900 dark:text-blue-100",
  };
  return classes[type] || classes.info;
};

const getToastIcon = (type): Component => {
  const icons = {
    success: CheckCircle2,
    error: AlertCircle,
    warning: AlertCircle,
    info: Info,
  };
  return icons[type] || Info;
};

const removeToast = (id) => {
  const index = toasts.value.findIndex((t) => t.id === id);
  if (index > -1) {
    toasts.value.splice(index, 1);
  }
};

const addToast = (toast) => {
  const id = Date.now();
  toasts.value.push({ ...toast, id });
  setTimeout(() => removeToast(id), 5000);
};

onMounted(() => {
  window.showToast = addToast;
});
</script>
