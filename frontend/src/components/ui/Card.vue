<script setup lang="ts">
import { cn } from "@/utils/cn";

interface Props {
  class?: string;
}

defineProps<Props>();
</script>

<template>
  <div
    :class="
      cn(
        'rounded-lg border bg-card text-card-foreground shadow-sm',
        $attrs.class,
      )
    "
  >
    <slot />
  </div>
</template>
