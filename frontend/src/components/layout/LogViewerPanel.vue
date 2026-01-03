<template>
  <!-- Backdrop -->
  <Transition
    enter-active-class="transition-opacity duration-300"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-300"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="isOpen"
      @click="$emit('close')"
      :class="[
        'fixed inset-0 z-50 bg-black/50 transition-opacity',
        isOpen ? 'opacity-100' : 'pointer-events-none opacity-0',
      ]"
    />
  </Transition>

  <!-- Panel -->
  <Transition
    enter-active-class="transition-transform duration-300 ease-in-out"
    enter-from-class="translate-x-full"
    enter-to-class="translate-x-0"
    leave-active-class="transition-transform duration-300 ease-in-out"
    leave-from-class="translate-x-0"
    leave-to-class="translate-x-full"
  >
    <div
      v-if="isOpen"
      :class="[
        'bg-background fixed right-0 top-0 z-50 h-full w-full border-l shadow-lg sm:w-[480px]',
        isOpen ? 'translate-x-0' : 'translate-x-full',
      ]"
    >
      <div class="flex h-full flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between border-b p-4">
          <div class="flex flex-col gap-1">
            <h2 class="text-lg font-semibold text-foreground">System Logs</h2>
            <p class="text-sm text-muted-foreground">
              Real-time application logs
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            @click="$emit('close')"
            class="h-8 w-8"
          >
            <X class="h-4 w-4" />
            <span class="sr-only">Close</span>
          </Button>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-2 border-b p-4">
          <Button
            variant="outline"
            size="sm"
            @click="handleRefresh"
            class="gap-2 bg-transparent"
          >
            <RefreshCw class="h-3.5 w-3.5" />
            Force Refresh
          </Button>
          <Button
            variant="outline"
            size="sm"
            @click="handleClear"
            class="gap-2 bg-transparent"
          >
            <Trash2 class="h-3.5 w-3.5" />
            Clear
          </Button>
        </div>

        <!-- Logs -->
        <ScrollArea class="flex-1 p-4">
          <div class="flex flex-col gap-2">
            <template v-if="logs.length === 0">
              <div class="flex h-[400px] items-center justify-center">
                <p class="text-sm text-muted-foreground">No logs available</p>
              </div>
            </template>
            <template v-else>
              <div
                v-for="(log, index) in logs"
                :key="index"
                class="rounded-lg border bg-card p-3 text-sm text-foreground"
              >
                <div class="mb-1 flex items-center gap-2">
                  <span
                    :class="[
                      'inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium',
                      getLogBadgeClass(log.level),
                    ]"
                  >
                    {{ log.level.toUpperCase() }}
                  </span>
                  <span class="text-xs text-muted-foreground">{{
                    log.timestamp
                  }}</span>
                </div>
                <p class="text-foreground">{{ log.message }}</p>
              </div>
            </template>
          </div>
        </ScrollArea>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { X, RefreshCw, Trash2 } from "lucide-vue-next";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";

defineProps<{
  isOpen: boolean;
}>();

defineEmits<{
  close: [];
}>();

const sampleLogs = [
  {
    timestamp: "2025-12-27 09:39:59",
    level: "info",
    message: "API health check passed",
  },
  {
    timestamp: "2025-12-27 09:35:12",
    level: "success",
    message: "Statement uploaded successfully",
  },
  {
    timestamp: "2025-12-27 09:34:45",
    level: "info",
    message: "Processing CSV file: Chase6490_Activity.csv",
  },
  {
    timestamp: "2025-12-27 09:30:22",
    level: "info",
    message: "User authenticated",
  },
  {
    timestamp: "2025-12-27 09:25:11",
    level: "warning",
    message: "Slow query detected: transactions table",
  },
  {
    timestamp: "2025-12-27 09:20:05",
    level: "info",
    message: "Database connection established",
  },
];

const logs = ref(sampleLogs);

const getLogBadgeClass = (level: string) => {
  const classes = {
    error: "bg-red-500/10 text-red-600 dark:text-red-400",
    warning: "bg-yellow-500/10 text-yellow-600 dark:text-yellow-400",
    success: "bg-green-500/10 text-green-600 dark:text-green-400",
    info: "bg-blue-500/10 text-blue-600 dark:text-blue-400",
  };
  return (
    classes[level.toLowerCase() as keyof typeof classes] ||
    "bg-muted text-muted-foreground"
  );
};

const handleClear = () => {
  logs.value = [];
};

const handleRefresh = () => {
  logs.value = sampleLogs;
};
</script>
