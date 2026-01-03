<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { healthService } from "../services";
import { accountsService } from "../services/accounts";
import { statementsService } from "../services/statements";
import { transactionsService } from "../services/transactions";
import type { HealthInfo } from "../services/health";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

const healthStatus = ref<HealthInfo | null>(null);
const accountsCount = ref<number>(0);
const statementsCount = ref<number>(0);
const transactionsCount = ref<number>(0);
const recentActivity = ref<{ message: string; date: string } | null>(null);
const isLoading = ref(false);

let healthCheckInterval: number | null = null;

const checkHealth = async () => {
  try {
    healthStatus.value = await healthService.getHealth();
  } catch (err) {
    console.error("Health check failed:", err);
    healthStatus.value = null;
  }
};

const formatUptime = (seconds: number): string => {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  if (days > 0) {
    return `${days}d ${hours}h ${minutes}m`;
  } else if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else {
    return `${minutes}m`;
  }
};

const loadData = async () => {
  isLoading.value = true;
  try {
    // Load health status
    await checkHealth();

    // Load accounts count
    // Get full count by fetching all (or we could add a count endpoint)
    const allAccounts = await accountsService.listAccounts(0, 1000);
    accountsCount.value = allAccounts.length;

    // Load statements count
    const statements = await statementsService.listStatements(
      undefined,
      0,
      1000,
    );
    statementsCount.value = statements.length;

    // Get most recent statement for activity
    if (statements.length > 0) {
      const sorted = statements.sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      );
      const latest = sorted[0];
      if (latest) {
        recentActivity.value = {
          message: latest.original_filename,
          date: new Date(latest.created_at).toLocaleDateString(),
        };
      }
    }

    // Load transactions count
    try {
      const txResponse = await transactionsService.listTransactions({
        page: 1,
        page_size: 1,
      });
      transactionsCount.value = txResponse.meta.total || 0;
    } catch (err) {
      console.error("Failed to load transactions count:", err);
    }
  } catch (err) {
    console.error("Failed to load data:", err);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  loadData();
  // Check health every 20 seconds
  healthCheckInterval = window.setInterval(checkHealth, 20000);
});

onUnmounted(() => {
  if (healthCheckInterval) {
    clearInterval(healthCheckInterval);
  }
});
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex flex-col gap-2">
      <h1 class="text-balance text-xl font-semibold text-foreground">
        Welcome to Moneta
      </h1>
      <p class="text-pretty text-sm text-muted-foreground">
        Personal finance management application
      </p>
    </div>

    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <!-- API Status Card -->
      <Card>
        <CardHeader>
          <CardTitle>API Status</CardTitle>
          <CardDescription>System health information</CardDescription>
        </CardHeader>
        <CardContent class="flex flex-col gap-4">
          <template v-if="isLoading">
            <Skeleton class="h-6 w-24" />
            <div class="flex flex-col gap-3">
              <div class="flex justify-between">
                <Skeleton class="h-4 w-16" />
                <Skeleton class="h-4 w-20" />
              </div>
              <div class="flex justify-between">
                <Skeleton class="h-4 w-16" />
                <Skeleton class="h-4 w-20" />
              </div>
              <div class="flex justify-between">
                <Skeleton class="h-4 w-16" />
                <Skeleton class="h-4 w-20" />
              </div>
              <div class="flex justify-between">
                <Skeleton class="h-4 w-20" />
                <Skeleton class="h-4 w-32" />
              </div>
            </div>
          </template>
          <template v-else>
            <div class="flex items-center gap-2">
              <Badge
                variant="outline"
                :class="
                  healthStatus?.ok
                    ? 'bg-green-500/10 text-green-600 dark:text-green-400'
                    : 'bg-red-500/10 text-red-600 dark:text-red-400'
                "
              >
                <span
                  class="mr-1 h-2 w-2 rounded-full"
                  :class="
                    healthStatus?.ok
                      ? 'bg-green-600 dark:bg-green-400'
                      : 'bg-red-600 dark:bg-red-400'
                  "
                />
                {{ healthStatus?.ok ? "Healthy" : "Unhealthy" }}
              </Badge>
            </div>
            <div class="flex flex-col gap-1 text-sm">
              <div class="flex justify-between">
                <span class="text-muted-foreground">Version:</span>
                <span class="font-medium">{{
                  healthStatus?.version || "N/A"
                }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">Python:</span>
                <span class="font-medium">{{
                  healthStatus?.pythonVersion || "N/A"
                }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">Uptime:</span>
                <span class="font-medium">
                  {{
                    healthStatus?.uptimeSeconds
                      ? formatUptime(healthStatus.uptimeSeconds)
                      : "N/A"
                  }}
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">Timestamp:</span>
                <span class="font-medium">
                  {{
                    healthStatus?.timestamp
                      ? new Date(healthStatus.timestamp).toLocaleString(
                          undefined,
                          {
                            dateStyle: "short",
                            timeStyle: "medium",
                          },
                        )
                      : "N/A"
                  }}
                </span>
              </div>
            </div>
          </template>
        </CardContent>
      </Card>

      <!-- Quick Stats Card -->
      <Card>
        <CardHeader>
          <CardTitle>Quick Stats</CardTitle>
          <CardDescription>Your financial overview</CardDescription>
        </CardHeader>
        <CardContent class="flex flex-col gap-4">
          <template v-if="isLoading">
            <div class="flex flex-col gap-3">
              <div class="flex justify-between">
                <Skeleton class="h-4 w-24" />
                <Skeleton class="h-4 w-12" />
              </div>
              <div class="flex justify-between">
                <Skeleton class="h-4 w-20" />
                <Skeleton class="h-4 w-12" />
              </div>
              <div class="flex justify-between">
                <Skeleton class="h-4 w-24" />
                <Skeleton class="h-4 w-16" />
              </div>
            </div>
          </template>
          <template v-else>
            <div class="flex flex-col gap-1 text-sm">
              <div class="flex justify-between">
                <span class="text-muted-foreground">Total Accounts:</span>
                <span class="font-medium">{{ accountsCount }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">Statements:</span>
                <span class="font-medium">{{ statementsCount }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">Transactions:</span>
                <span class="font-medium">{{
                  transactionsCount.toLocaleString()
                }}</span>
              </div>
            </div>
          </template>
        </CardContent>
      </Card>

      <!-- Recent Activity Card -->
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest updates</CardDescription>
        </CardHeader>
        <CardContent>
          <template v-if="isLoading">
            <div class="flex flex-col gap-2">
              <Skeleton class="h-4 w-32" />
              <Skeleton class="h-4 w-48" />
            </div>
          </template>
          <template v-else>
            <div class="flex flex-col gap-2 text-sm">
              <div v-if="recentActivity" class="flex flex-col gap-1">
                <span class="font-medium">Statement Uploaded</span>
                <span class="text-muted-foreground">
                  {{ recentActivity.message }} - {{ recentActivity.date }}
                </span>
              </div>
              <div v-else class="text-muted-foreground">No recent activity</div>
            </div>
          </template>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
