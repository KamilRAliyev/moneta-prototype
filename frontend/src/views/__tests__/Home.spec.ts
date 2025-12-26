import { describe, it, expect, beforeEach, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { createRouter, createMemoryHistory } from "vue-router";
import Home from "../Home.vue";
import { healthService } from "../../services";
import type { HealthInfo } from "../../services/health";

// Mock the health service
vi.mock("../../services", () => ({
  healthService: {
    getHealth: vi.fn(),
  },
}));

const mockedHealthService = vi.mocked(healthService);

describe("Home", () => {
  const createTestRouter = () => {
    return createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: "/",
          component: Home,
        },
      ],
    });
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders welcome message", async () => {
    mockedHealthService.getHealth.mockResolvedValue({
      ok: true,
    } as HealthInfo);

    const router = createTestRouter();
    const wrapper = mount(Home, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();

    expect(wrapper.text()).toContain("Welcome to Moneta");
    expect(wrapper.text()).toContain("Personal finance management application");
  });

  it("renders API status section", async () => {
    mockedHealthService.getHealth.mockResolvedValue({
      ok: true,
    } as HealthInfo);

    const router = createTestRouter();
    const wrapper = mount(Home, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();

    expect(wrapper.text()).toContain("API Status");
    expect(wrapper.find("button").exists()).toBe(true);
    expect(wrapper.find("button").text()).toContain("Check Health");
  });

  it("calls health service on mount", async () => {
    mockedHealthService.getHealth.mockResolvedValue({
      ok: true,
    } as HealthInfo);

    const router = createTestRouter();
    mount(Home, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 100)); // Wait for onMounted

    expect(mockedHealthService.getHealth).toHaveBeenCalledTimes(1);
  });

  it("displays health status when available", async () => {
    const mockHealthInfo: HealthInfo = {
      ok: true,
      version: "0.1.0",
      timestamp: "2025-01-01T00:00:00Z",
    };

    mockedHealthService.getHealth.mockResolvedValue(mockHealthInfo);

    const router = createTestRouter();
    const wrapper = mount(Home, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 100)); // Wait for API call

    expect(wrapper.text()).toContain("Healthy");
    expect(wrapper.text()).toContain("0.1.0");
  });

  it("displays error message when health check fails", async () => {
    mockedHealthService.getHealth.mockRejectedValue(new Error("Network error"));

    const router = createTestRouter();
    const wrapper = mount(Home, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 100)); // Wait for API call

    expect(wrapper.text()).toContain("Failed to connect to API");
  });

  it("shows loading state when checking health", async () => {
    // Create a promise that we can control
    let resolveHealth: (value: HealthInfo) => void;
    const healthPromise = new Promise<HealthInfo>((resolve) => {
      resolveHealth = resolve;
    });

    mockedHealthService.getHealth.mockReturnValue(healthPromise);

    const router = createTestRouter();
    const wrapper = mount(Home, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();

    // Click the button to trigger health check
    const button = wrapper.find("button");
    await button.trigger("click");

    // Button should show loading state
    expect(button.text()).toContain("Checking...");
    expect(button.attributes("disabled")).toBeDefined();

    // Resolve the promise
    resolveHealth!({ ok: true });

    await new Promise((resolve) => setTimeout(resolve, 100));

    // Button should be enabled again
    expect(button.text()).toContain("Check Health");
  });

  it("renders HelloWorld component", async () => {
    mockedHealthService.getHealth.mockResolvedValue({
      ok: true,
    } as HealthInfo);

    const router = createTestRouter();
    const wrapper = mount(Home, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();

    // HelloWorld should be rendered
    expect(wrapper.html()).toContain("Vite + Vue");
  });
});
