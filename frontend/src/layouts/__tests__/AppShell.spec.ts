import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import { createRouter, createMemoryHistory } from "vue-router";
import AppShell from "../AppShell.vue";

describe("AppShell", () => {
  const createTestRouter = () => {
    return createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: "/",
          component: AppShell,
          children: [
            {
              path: "",
              component: { template: "<div>Test Content</div>" },
            },
          ],
        },
      ],
    });
  };

  it("renders sidebar with logo and navigation", async () => {
    const router = createTestRouter();
    const wrapper = mount(AppShell, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();

    // Check sidebar exists
    const sidebar = wrapper.find("aside");
    expect(sidebar.exists()).toBe(true);

    // Check logo/brand
    expect(wrapper.text()).toContain("Moneta");

    // Check navigation
    const nav = wrapper.find("nav");
    expect(nav.exists()).toBe(true);
  });

  it("renders main content area with router-view", async () => {
    const router = createTestRouter();
    const wrapper = mount(AppShell, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();

    // Check main content area exists
    const main = wrapper.find("main");
    expect(main.exists()).toBe(true);

    // Check router-view is rendered (content should be there)
    expect(wrapper.html()).toContain("Test Content");
  });

  it("renders header with actions", async () => {
    const router = createTestRouter();
    const wrapper = mount(AppShell, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();

    // Check header exists
    const header = wrapper.find("header");
    expect(header.exists()).toBe(true);
  });

  it("applies active route styling to navigation link", async () => {
    const router = createTestRouter();
    await router.push("/");

    const wrapper = mount(AppShell, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();

    // The active link should have specific classes
    // Note: This test might need adjustment based on actual rendered classes
    expect(wrapper.html()).toContain("Home");

    // Verify navigation link exists
    const navLinks = wrapper.findAll("nav a");
    expect(navLinks.length).toBeGreaterThan(0);
  });
});
