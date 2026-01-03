<script setup lang="ts">
import { computed } from "vue";
import { useRoute, RouterLink } from "vue-router";
import { useLocalStorage } from "@vueuse/core";
import {
  Home,
  Wallet,
  FileText,
  Receipt,
  ChevronLeft,
  ChevronRight,
} from "lucide-vue-next";
import { cn } from "@/utils/cn";

const route = useRoute();
const isCollapsed = useLocalStorage("sidebar-collapsed", false);

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};

const navItems = [
  { path: "/", label: "Home", icon: Home },
  { path: "/accounts", label: "Accounts", icon: Wallet },
  { path: "/statements", label: "Statements", icon: FileText },
  { path: "/transactions", label: "Transactions", icon: Receipt },
];

const isActive = (path: string) => {
  if (path === "/") {
    return route.path === "/";
  }
  return route.path.startsWith(path);
};
</script>

<template>
  <aside
    :class="
      cn(
        'fixed left-0 top-0 z-40 h-screen border-r bg-sidebar transition-all duration-300',
        isCollapsed ? 'w-16' : 'w-64',
      )
    "
  >
    <div class="flex h-full flex-col">
      <!-- Logo/Brand -->
      <div
        :class="
          cn(
            'flex h-16 items-center border-b border-sidebar-border px-4',
            isCollapsed && 'justify-center',
          )
        "
      >
        <RouterLink
          to="/"
          :class="
            cn(
              'flex items-center gap-2 font-bold text-sidebar-foreground transition-colors hover:text-sidebar-primary',
              isCollapsed && 'justify-center',
            )
          "
        >
          <Wallet class="h-6 w-6" />
          <span v-if="!isCollapsed" class="text-lg">Moneta</span>
        </RouterLink>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 space-y-1 p-4">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          :class="
            cn(
              'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
              isCollapsed ? 'justify-center' : '',
              isActive(item.path)
                ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
            )
          "
        >
          <component :is="item.icon" class="h-5 w-5 shrink-0" />
          <span v-if="!isCollapsed" class="truncate">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <!-- Collapse Toggle (at bottom) -->
      <div class="border-t border-sidebar-border p-4">
        <button
          @click="toggleCollapse"
          class="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-sidebar-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
          :class="isCollapsed ? 'justify-center' : ''"
        >
          <ChevronLeft v-if="!isCollapsed" class="h-5 w-5" />
          <ChevronRight v-else class="h-5 w-5" />
          <span v-if="!isCollapsed">Collapse</span>
        </button>
      </div>
    </div>
  </aside>
</template>
