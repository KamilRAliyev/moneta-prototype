<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useTheme } from "@/composables/useTheme";
import { useLocalStorage } from "@vueuse/core";
import { Sun, Moon, FileText, Menu } from "lucide-vue-next";
import { healthService } from "@/services/health";
import { Button } from "@/components/ui/button";
import { cn } from "@/utils/cn";

interface Props {
  onToggleSidebar?: () => void;
  onToggleLogs?: () => void;
}

const props = defineProps<Props>();

const { isDark, toggleTheme } = useTheme();
const isCollapsed = useLocalStorage("sidebar-collapsed", false);

const healthStatus = ref<"healthy" | "degraded" | "down">("healthy");
const lastHealthCheck = ref<Date | null>(null);

let healthCheckInterval: number | null = null;

const checkApiHealth = async () => {
  try {
    const response = await healthService.getHealth();
    healthStatus.value = response.ok ? "healthy" : "degraded";
    lastHealthCheck.value = new Date();
  } catch (error) {
    healthStatus.value = "down";
    lastHealthCheck.value = new Date();
  }
};

onMounted(() => {
  checkApiHealth();
  // Check health every 30 seconds
  healthCheckInterval = window.setInterval(checkApiHealth, 30000);
});

onUnmounted(() => {
  if (healthCheckInterval) {
    clearInterval(healthCheckInterval);
  }
});

const healthColor = {
  healthy: "bg-green-500",
  degraded: "bg-yellow-500",
  down: "bg-red-500",
};

const healthTooltip = computed(() => {
  const statusText = {
    healthy: "API is healthy",
    degraded: "API is degraded",
    down: "API is down",
  };
  const timeText = lastHealthCheck.value
    ? `Last check: ${lastHealthCheck.value.toLocaleTimeString()}`
    : "Checking...";
  return `${statusText[healthStatus.value]}\n${timeText}`;
});
</script>

<template>
  <header
    class="sticky top-0 z-30 flex h-16 items-center border-b bg-background px-4 shadow-sm"
  >
    <!-- Left: Sidebar Toggle (only show when sidebar is collapsed on mobile) -->
    <div class="flex items-center gap-4">
      <Button
        v-if="isCollapsed"
        variant="ghost"
        size="icon"
        @click="props.onToggleSidebar?.()"
        class="lg:hidden"
      >
        <Menu class="h-5 w-5" />
      </Button>
    </div>

    <!-- Right: Actions -->
    <div class="ml-auto flex items-center gap-2">
      <!-- Theme Toggle -->
      <Button
        variant="ghost"
        size="icon"
        @click="toggleTheme()"
        :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
      >
        <Sun v-if="isDark" class="h-5 w-5 transition-all" />
        <Moon v-else class="h-5 w-5 transition-all" />
      </Button>

      <!-- API Health Indicator -->
      <div class="relative flex items-center" :title="healthTooltip">
        <div :class="cn('h-2 w-2 rounded-full', healthColor[healthStatus])" />
      </div>

      <!-- Logs Toggle -->
      <Button
        variant="ghost"
        size="icon"
        @click="props.onToggleLogs?.()"
        title="View logs"
      >
        <FileText class="h-5 w-5" />
      </Button>
    </div>
  </header>
</template>
