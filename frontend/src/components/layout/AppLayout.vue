<template>
  <div class="flex h-screen overflow-hidden">
    <!-- Sidebar -->
    <aside
      :class="[
        'h-screen sticky top-0 border-r bg-card transition-all duration-300 ease-in-out flex flex-col',
        isCollapsed ? 'w-16' : 'w-64',
      ]"
    >
      <!-- Logo -->
      <div class="h-16 border-b flex items-center px-4">
        <div class="flex items-center gap-2">
          <div
            class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold"
          >
            M
          </div>
          <span v-if="!isCollapsed" class="font-semibold text-lg">Moneta</span>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-3 space-y-1">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground"
          :class="{
            'bg-accent text-accent-foreground': route.path === item.path,
          }"
        >
          <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
          <span v-if="!isCollapsed">{{ item.label }}</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Header -->
      <header
        class="bg-background sticky top-0 z-10 flex h-14 shrink-0 items-center gap-2 border-b px-4"
      >
        <div class="flex flex-1 items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            @click="toggleSidebar"
            class="h-9 w-9"
          >
            <Menu class="h-4 w-4" />
            <span class="sr-only">Toggle Sidebar</span>
          </Button>
        </div>
        <div class="flex items-center gap-2">
          <!-- Health Status with Tooltip -->
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger as-child>
                <div class="flex items-center">
                  <div
                    class="flex items-center gap-2 rounded-md border px-3 py-1.5 text-sm"
                  >
                    <div
                      :class="[
                        'size-2 rounded-full',
                        healthStatus === 'healthy'
                          ? 'bg-green-500 animate-pulse'
                          : healthStatus === 'degraded'
                            ? 'bg-yellow-500'
                            : 'bg-red-500',
                      ]"
                    />
                    <span class="hidden font-medium sm:inline capitalize">{{
                      healthStatus === "healthy"
                        ? "Healthy"
                        : healthStatus === "degraded"
                          ? "Degraded"
                          : "Down"
                    }}</span>
                  </div>
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <div class="flex flex-col gap-1">
                  <div class="font-semibold">API Status</div>
                  <div class="flex justify-between gap-4 text-xs">
                    <span class="text-muted-foreground">Version:</span>
                    <span>{{ apiVersion }}</span>
                  </div>
                  <div class="flex justify-between gap-4 text-xs">
                    <span class="text-muted-foreground">Status:</span>
                    <span
                      :class="[
                        healthStatus === 'healthy'
                          ? 'text-green-600 dark:text-green-400'
                          : healthStatus === 'degraded'
                            ? 'text-yellow-600 dark:text-yellow-400'
                            : 'text-red-600 dark:text-red-400',
                      ]"
                    >
                      {{
                        healthStatus === "healthy"
                          ? "Healthy"
                          : healthStatus === "degraded"
                            ? "Degraded"
                            : "Down"
                      }}
                    </span>
                  </div>
                  <div class="flex justify-between gap-4 text-xs">
                    <span class="text-muted-foreground">Timestamp:</span>
                    <span>{{ apiTimestamp }}</span>
                  </div>
                </div>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <!-- Logs Button -->
          <Button
            variant="ghost"
            size="icon"
            @click="toggleLogs"
            class="h-9 w-9"
          >
            <Terminal class="h-4 w-4" />
            <span class="sr-only">View Logs</span>
          </Button>

          <!-- Theme Toggle -->
          <Button
            variant="ghost"
            size="icon"
            @click="toggleTheme"
            class="h-9 w-9"
          >
            <Sun
              v-if="isDark"
              class="h-4 w-4 rotate-0 scale-100 transition-all"
            />
            <Moon v-else class="h-4 w-4 rotate-0 scale-100 transition-all" />
            <span class="sr-only">Toggle theme</span>
          </Button>
        </div>
      </header>

      <!-- Content Area -->
      <main class="flex-1 overflow-y-auto p-6">
        <slot />
      </main>
    </div>

    <!-- Log Viewer Panel -->
    <LogViewerPanel :is-open="isLogsOpen" @close="toggleLogs" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { useLocalStorage } from "@vueuse/core";
import {
  Home,
  Wallet,
  FileText,
  ArrowLeftRight,
  Menu,
  Sun,
  Moon,
  Terminal,
} from "lucide-vue-next";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useTheme } from "@/composables/useTheme";
import { healthService } from "@/services/health";
import LogViewerPanel from "./LogViewerPanel.vue";

const route = useRoute();
const { isDark, toggleTheme } = useTheme();
const isCollapsed = useLocalStorage("sidebar-collapsed", false);
const isLogsOpen = ref(false);

// API health data
const healthStatus = ref<"healthy" | "degraded" | "down">("healthy");
const apiVersion = ref<string>("");
const apiTimestamp = ref<string>("");

let healthCheckInterval: number | null = null;

const checkApiHealth = async () => {
  try {
    const response = await healthService.getHealth();
    healthStatus.value = response.ok ? "healthy" : "degraded";
    apiVersion.value = response.version || "0.1.0";
    apiTimestamp.value = response.timestamp
      ? new Date(response.timestamp).toLocaleString()
      : new Date().toLocaleString();
  } catch (error) {
    healthStatus.value = "down";
    apiTimestamp.value = new Date().toLocaleString();
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

const navItems = [
  { path: "/", label: "Home", icon: Home },
  { path: "/accounts", label: "Accounts", icon: Wallet },
  { path: "/statements", label: "Statements", icon: FileText },
  { path: "/transactions", label: "Transactions", icon: ArrowLeftRight },
];

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

const toggleLogs = () => {
  isLogsOpen.value = !isLogsOpen.value;
};
</script>
