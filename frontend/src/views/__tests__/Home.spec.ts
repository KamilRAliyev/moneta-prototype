import { describe, it, expect, beforeEach, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { createRouter, createMemoryHistory } from "vue-router";
import Home from "../Home.vue";
import { healthService } from "../../services";
import { accountsService } from "../../services/accounts";
import { statementsService } from "../../services/statements";
import { transactionsService } from "../../services/transactions";
import type { HealthInfo } from "../../services/health";

// Mock all services
vi.mock("../../services", () => ({
  healthService: {
    getHealth: vi.fn(),
  },
}));

vi.mock("../../services/accounts", () => ({
  accountsService: {
    listAccounts: vi.fn(),
  },
}));

vi.mock("../../services/statements", () => ({
  statementsService: {
    listStatements: vi.fn(),
  },
}));

vi.mock("../../services/transactions", () => ({
  transactionsService: {
    listTransactions: vi.fn(),
  },
}));

const mockedHealthService = vi.mocked(healthService);
const mockedAccountsService = vi.mocked(accountsService);
const mockedStatementsService = vi.mocked(statementsService);
const mockedTransactionsService = vi.mocked(transactionsService);

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
    // Setup default mocks
    mockedHealthService.getHealth.mockResolvedValue({
      ok: true,
      version: "0.1.0",
      timestamp: "2025-01-01T00:00:00Z",
    } as HealthInfo);
    mockedAccountsService.listAccounts.mockResolvedValue([]);
    mockedStatementsService.listStatements.mockResolvedValue([]);
    mockedTransactionsService.listTransactions.mockResolvedValue({
      data: [],
      meta: { total: 0, page: 1, page_size: 1, total_pages: 0 },
    });
  });

  it("renders welcome message", async () => {
    const router = createTestRouter();
    const wrapper = mount(Home, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 100));

    expect(wrapper.text()).toContain("Welcome to Moneta");
    expect(wrapper.text()).toContain("Personal finance management application");
  });

  it("renders API status card", async () => {
    const router = createTestRouter();
    const wrapper = mount(Home, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 100));

    expect(wrapper.text()).toContain("API Status");
    expect(wrapper.text()).toContain("System health information");
  });

  it("calls all services on mount", async () => {
    const router = createTestRouter();
    mount(Home, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 200)); // Wait for onMounted

    expect(mockedHealthService.getHealth).toHaveBeenCalled();
    expect(mockedAccountsService.listAccounts).toHaveBeenCalled();
    expect(mockedStatementsService.listStatements).toHaveBeenCalled();
    expect(mockedTransactionsService.listTransactions).toHaveBeenCalled();
  });

  it("displays health status when available", async () => {
    const mockHealthInfo: HealthInfo = {
      ok: true,
      version: "0.1.0",
      timestamp: "2025-01-01T00:00:00Z",
      pythonVersion: "3.13.0",
      uptimeSeconds: 86400,
    };

    mockedHealthService.getHealth.mockResolvedValue(mockHealthInfo);

    const router = createTestRouter();
    const wrapper = mount(Home, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 200)); // Wait for API call

    expect(wrapper.text()).toContain("Healthy");
    expect(wrapper.text()).toContain("0.1.0");
  });

  it("shows skeleton loaders while loading", async () => {
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

    // Should show skeleton loaders
    const skeletons = wrapper.findAll('[class*="animate-pulse"]');
    expect(skeletons.length).toBeGreaterThan(0);

    // Resolve the promise
    resolveHealth!({ ok: true });

    await new Promise((resolve) => setTimeout(resolve, 200));
  });

  it("renders Quick Stats card", async () => {
    mockedAccountsService.listAccounts.mockResolvedValue([
      {
        id: 1,
        name: "Test",
        institution: "Bank",
        currency: "USD",
        account_type: "checking",
        economic_area: "us",
        datelock_from: null,
        datelock_to: null,
        created_at: "2025-01-01",
        updated_at: null,
      },
    ]);
    mockedStatementsService.listStatements.mockResolvedValue([
      {
        id: "1",
        account_id: 1,
        account_name: "Test",
        original_filename: "test.csv",
        size_bytes: 1000,
        row_count: 10,
        date_from: null,
        date_to: null,
        status: "uploaded",
        is_ingested: false,
        ingested_at: null,
        file_exists: true,
        created_at: "2025-01-01",
      },
    ]);
    mockedTransactionsService.listTransactions.mockResolvedValue({
      data: [],
      meta: { total: 100, page: 1, page_size: 1, total_pages: 1 },
    });

    const router = createTestRouter();
    const wrapper = mount(Home, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 200));

    expect(wrapper.text()).toContain("Quick Stats");
    expect(wrapper.text()).toContain("Total Accounts");
  });

  it("renders Recent Activity card", async () => {
    const mockStatement = {
      id: "1",
      account_id: 1,
      account_name: "Test",
      original_filename: "test.csv",
      size_bytes: 1000,
      row_count: 10,
      date_from: null,
      date_to: null,
      status: "uploaded",
      is_ingested: false,
      ingested_at: null,
      file_exists: true,
      created_at: "2025-01-01T00:00:00Z",
    };

    mockedStatementsService.listStatements.mockResolvedValue([mockStatement]);

    const router = createTestRouter();
    const wrapper = mount(Home, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 200));

    expect(wrapper.text()).toContain("Recent Activity");
  });
});
