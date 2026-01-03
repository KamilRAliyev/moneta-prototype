<script setup lang="ts">
import { cn } from "@/utils/cn";
</script>

<template>
  <div :class="cn('text-sm text-muted-foreground', $attrs.class)">
    <slot />
  </div>
</template>
