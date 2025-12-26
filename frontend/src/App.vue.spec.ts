import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import { createRouter, createMemoryHistory } from "vue-router";
import App from "./App.vue";

describe("App", () => {
  it("renders router-view and app container", async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: "/",
          component: { template: "<div>Test Route</div>" },
        },
      ],
    });

    const wrapper = mount(App, {
      global: {
        plugins: [router],
      },
    });

    // Wait for router to be ready
    await router.isReady();

    // Verify the app container exists
    expect(wrapper.find("#app").exists()).toBe(true);

    // Verify router is working by checking route content is rendered
    // After router navigation, the route component should be rendered
    expect(wrapper.html()).toContain("Test Route");
  });
});
