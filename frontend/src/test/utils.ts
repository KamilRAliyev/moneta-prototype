import { createPinia, setActivePinia } from "pinia";
import { createRouter, createWebHistory } from "vue-router";
import { config } from "@vue/test-utils";

// Create a test router instance
export function createTestRouter() {
  return createRouter({
    history: createWebHistory(),
    routes: [
      {
        path: "/",
        name: "home",
        component: { template: "<div>Home</div>" },
      },
    ],
  });
}

// Setup Pinia for tests
export function setupPinia() {
  const pinia = createPinia();
  setActivePinia(pinia);
  return pinia;
}

// Global test configuration
config.global.stubs = {
  RouterLink: true,
  RouterView: true,
};
