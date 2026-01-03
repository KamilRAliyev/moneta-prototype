<script setup lang="ts">
import { computed } from "vue";
import {
  X,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  Info,
} from "lucide-vue-next";
import type { Toast } from "@/stores/toast";
import { cn } from "@/utils/cn";
import BaseButton from "./BaseButton.vue";

interface Props {
  toast: Toast;
  onDismiss: (id: string) => void;
}

const props = defineProps<Props>();

const iconMap = {
  success: CheckCircle2,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
};

const variantClasses = {
  success:
    "border-green-500/50 bg-green-500/10 text-green-700 dark:text-green-400",
  error: "border-destructive/50 bg-destructive/10 text-destructive",
  warning:
    "border-yellow-500/50 bg-yellow-500/10 text-yellow-700 dark:text-yellow-400",
  info: "border-blue-500/50 bg-blue-500/10 text-blue-700 dark:text-blue-400",
};

const Icon = computed(() => iconMap[props.toast.type]);
</script>

<template>
  <div
    :class="
      cn(
        'group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-4 pr-8 shadow-lg transition-all',
        variantClasses[toast.type],
      )
    "
  >
    <div class="flex items-start gap-3 flex-1">
      <component :is="Icon" class="h-5 w-5 shrink-0 mt-0.5" />
      <div class="flex-1">
        <p class="text-sm font-semibold">{{ toast.title }}</p>
        <p v-if="toast.description" class="text-sm opacity-90 mt-1">
          {{ toast.description }}
        </p>
      </div>
    </div>

    <BaseButton
      variant="ghost"
      size="icon"
      class="absolute right-2 top-2 h-6 w-6 opacity-0 transition-opacity group-hover:opacity-100"
      @click="onDismiss(toast.id)"
    >
      <X class="h-4 w-4" />
    </BaseButton>
  </div>
</template>
