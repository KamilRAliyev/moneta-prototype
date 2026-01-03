<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import type { Account } from "../../types/accounts";

interface Props {
  accounts: Account[];
  isLoading?: boolean;
}

interface Emits {
  (e: "view", account: Account): void;
  (e: "edit", account: Account): void;
  (e: "delete", account: Account): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const formatDateLock = (from: string | null, to: string | null): string => {
  if (!from && !to) return "No date lock";
  if (from && to) return `${from} to ${to}`;
  if (from) return `From: ${from}`;
  if (to) return `To: ${to}`;
  return "No date lock";
};

const formatAccountType = (type: string): string => {
  return type
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};
</script>

<template>
  <div class="overflow-x-auto -mx-4 sm:mx-0">
    <!-- Desktop Table View -->
    <table class="min-w-full divide-y divide-border bg-card shadow rounded-lg">
      <thead class="bg-card border-b border-border">
        <tr>
          <th
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider"
          >
            Name
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider"
          >
            Institution
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider"
          >
            Currency
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider"
          >
            Type
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider"
          >
            Economic Area
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider"
          >
            Date Lock
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
          >
            Actions
          </th>
        </tr>
      </thead>
      <tbody class="bg-card divide-y divide-border">
        <template v-if="props.isLoading">
          <tr v-for="i in 5" :key="`skeleton-${i}`" class="hover:bg-muted/50">
            <td class="px-6 py-4">
              <Skeleton class="h-4 w-32" />
            </td>
            <td class="px-6 py-4">
              <Skeleton class="h-4 w-24" />
            </td>
            <td class="px-6 py-4">
              <Skeleton class="h-4 w-12" />
            </td>
            <td class="px-6 py-4">
              <Skeleton class="h-4 w-20" />
            </td>
            <td class="px-6 py-4">
              <Skeleton class="h-4 w-16" />
            </td>
            <td class="px-6 py-4">
              <Skeleton class="h-4 w-28" />
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <Skeleton class="h-8 w-16" />
                <Skeleton class="h-8 w-16" />
              </div>
            </td>
          </tr>
        </template>
        <template v-else-if="props.accounts.length === 0">
          <tr class="text-center">
            <td colspan="8" class="px-6 py-4 text-sm text-muted-foreground">
              No accounts found. Create your first account to get started.
            </td>
          </tr>
        </template>
        <template v-else>
          <tr
            v-for="account in props.accounts"
            :key="account.id"
            class="hover:bg-muted/50 cursor-pointer transition-colors"
            @click="emit('view', account)"
          >
            <td
              class="px-6 py-4 whitespace-nowrap text-sm font-medium text-foreground"
            >
              {{ account.name }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
            >
              {{ account.institution }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
            >
              {{ account.currency }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
            >
              {{ formatAccountType(account.account_type) }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
            >
              {{ account.economic_area || "-" }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400"
            >
              {{ formatDateLock(account.datelock_from, account.datelock_to) }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
              @click.stop
            >
              <div class="flex justify-end gap-2">
                <Button
                  @click="emit('edit', account)"
                  variant="ghost"
                  size="sm"
                >
                  Edit
                </Button>
                <Button
                  @click="emit('delete', account)"
                  variant="ghost"
                  size="sm"
                  class="text-destructive hover:text-destructive"
                >
                  Delete
                </Button>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>
