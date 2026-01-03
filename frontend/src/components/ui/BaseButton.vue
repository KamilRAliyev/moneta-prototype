<script setup lang="ts">
import { computed } from "vue";
import { cn } from "@/utils/cn";

interface Props {
  variant?:
    | "default"
    | "destructive"
    | "outline"
    | "secondary"
    | "ghost"
    | "link";
  size?: "default" | "sm" | "lg" | "icon";
  as?: string;
  disabled?: boolean;
  type?: "button" | "submit" | "reset";
  class?: string;
}

const props = withDefaults(defineProps<Props>(), {
  variant: "default",
  size: "default",
  as: "button",
  disabled: false,
  type: "button",
});

const buttonClasses = computed(() => {
  const baseClasses =
    "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0";

  const variantClasses = {
    default: "bg-primary text-primary-foreground hover:bg-primary/90",
    destructive:
      "bg-destructive text-destructive-foreground hover:bg-destructive/90",
    outline:
      "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
    secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
    ghost: "hover:bg-accent hover:text-accent-foreground",
    link: "text-primary underline-offset-4 hover:underline",
  };

  const sizeClasses = {
    default: "h-10 px-4 py-2",
    sm: "h-9 rounded-md px-3",
    lg: "h-11 rounded-md px-8",
    icon: "h-10 w-10",
  };

  return cn(
    baseClasses,
    variantClasses[props.variant],
    sizeClasses[props.size],
    props.class,
  );
});
</script>

<template>
  <component
    :is="as"
    :class="buttonClasses"
    :disabled="disabled"
    :type="as === 'button' ? type : undefined"
  >
    <slot />
  </component>
</template>
