<script setup lang="ts">
import { cn } from "@/utils/cn";
</script>

<template>
  <div
    :class="
      cn('text-2xl font-semibold leading-none tracking-tight', $attrs.class)
    "
  >
    <slot />
  </div>
</template>
