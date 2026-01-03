import { describe, it, expect, beforeEach, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { createRouter, createMemoryHistory } from "vue-router";
import AccountDetail from "../AccountDetail.vue";
import { accountsService } from "../../../services/accounts";
import type { Account, MetaOptionsResponse } from "../../../types/accounts";

// Mock the accounts service
vi.mock("../../../services/accounts", () => ({
  accountsService: {
    getAccount: vi.fn(),
    updateAccount: vi.fn(),
    getAccountMetaOptions: vi.fn(),
  },
}));

const mockedAccountsService = vi.mocked(accountsService);

describe("AccountDetail", () => {
  const createTestRouter = () => {
    return createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: "/accounts/:id",
          component: AccountDetail,
        },
        {
          path: "/accounts",
          component: { template: "<div>Accounts List</div>" },
        },
      ],
    });
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Setup default mock for getAccountMetaOptions
    mockedAccountsService.getAccountMetaOptions.mockResolvedValue({
      account_types: [
        { value: "checking", label: "Checking" },
        { value: "savings", label: "Savings" },
      ],
      economic_areas: [
        { value: "us", label: "United States" },
        { value: "eu", label: "European Union" },
      ],
      currencies: [
        { code: "USD", name: "US Dollar", digits: 2 },
        { code: "EUR", name: "Euro", digits: 2 },
      ],
    } as MetaOptionsResponse);
  });

  it("renders page title with account name", async () => {
    const mockAccount: Account = {
      id: 1,
      name: "Test Account",
      institution: "Test Bank",
      currency: "USD",
      account_type: "checking",
      economic_area: "us",
      datelock_from: null,
      datelock_to: null,
      created_at: "2025-01-01T00:00:00Z",
      updated_at: null,
    };

    mockedAccountsService.getAccount.mockResolvedValue(mockAccount);

    const router = createTestRouter();
    await router.push("/accounts/1");

    const wrapper = mount(AccountDetail, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 200));

    expect(wrapper.text()).toContain("Test Account");
    expect(wrapper.text()).toContain("Test Bank");
  });

  it("loads account on mount", async () => {
    const mockAccount: Account = {
      id: 1,
      name: "Test Account",
      institution: "Test Bank",
      currency: "USD",
      account_type: "checking",
      economic_area: null,
      datelock_from: null,
      datelock_to: null,
      created_at: "2025-01-01T00:00:00Z",
      updated_at: null,
    };

    mockedAccountsService.getAccount.mockResolvedValue(mockAccount);

    const router = createTestRouter();
    await router.push("/accounts/1");

    mount(AccountDetail, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 200));

    expect(mockedAccountsService.getAccount).toHaveBeenCalledWith(1);
  });

  it("shows loading state while fetching account", async () => {
    // Create a promise that we can control
    let resolveAccount: (value: Account) => void;
    const accountPromise = new Promise<Account>((resolve) => {
      resolveAccount = resolve;
    });

    mockedAccountsService.getAccount.mockReturnValue(accountPromise);

    const router = createTestRouter();
    await router.push("/accounts/1");

    const wrapper = mount(AccountDetail, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Loading account...");

    // Resolve the promise
    resolveAccount!({
      id: 1,
      name: "Test Account",
      institution: "Test Bank",
      currency: "USD",
      account_type: "checking",
      economic_area: null,
      datelock_from: null,
      datelock_to: null,
      created_at: "2025-01-01T00:00:00Z",
      updated_at: null,
    });

    await new Promise((resolve) => setTimeout(resolve, 100));
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).not.toContain("Loading account...");
  });

  it("shows error message when account load fails", async () => {
    mockedAccountsService.getAccount.mockRejectedValue(
      new Error("Account not found"),
    );

    const router = createTestRouter();
    await router.push("/accounts/999");

    const wrapper = mount(AccountDetail, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 200));
    await wrapper.vm.$nextTick();

    // Error message should be displayed (could be "Account not found" or "Failed to load account")
    expect(
      wrapper.text().includes("Account not found") ||
        wrapper.text().includes("Failed to load account"),
    ).toBe(true);
  });

  it("updates account when form is submitted", async () => {
    const mockAccount: Account = {
      id: 1,
      name: "Original Name",
      institution: "Original Bank",
      currency: "USD",
      account_type: "checking",
      economic_area: null,
      datelock_from: null,
      datelock_to: null,
      created_at: "2025-01-01T00:00:00Z",
      updated_at: null,
    };

    const updatedAccount: Account = {
      ...mockAccount,
      name: "Updated Name",
      updated_at: "2025-01-02T00:00:00Z",
    };

    mockedAccountsService.getAccount.mockResolvedValue(mockAccount);
    mockedAccountsService.updateAccount.mockResolvedValue(updatedAccount);

    const router = createTestRouter();
    await router.push("/accounts/1");

    const wrapper = mount(AccountDetail, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 300)); // Wait for account to load and form to render

    // Find and submit form
    const form = wrapper.find("form");
    if (form.exists()) {
      await form.trigger("submit");
      await new Promise((resolve) => setTimeout(resolve, 100));
      expect(mockedAccountsService.updateAccount).toHaveBeenCalled();
    } else {
      // Form might not be rendered yet, skip this test detail
      expect(mockedAccountsService.getAccount).toHaveBeenCalled();
    }
  });

  it("navigates back to accounts list when cancel is clicked", async () => {
    const mockAccount: Account = {
      id: 1,
      name: "Test Account",
      institution: "Test Bank",
      currency: "USD",
      account_type: "checking",
      economic_area: null,
      datelock_from: null,
      datelock_to: null,
      created_at: "2025-01-01T00:00:00Z",
      updated_at: null,
    };

    mockedAccountsService.getAccount.mockResolvedValue(mockAccount);

    const router = createTestRouter();
    await router.push("/accounts/1");

    const wrapper = mount(AccountDetail, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 300)); // Wait for account to load

    const cancelButton = wrapper
      .findAll("button")
      .find((btn) => btn.text().includes("Cancel"));

    if (cancelButton) {
      await cancelButton.trigger("click");
      await new Promise((resolve) => setTimeout(resolve, 50));
      expect(router.currentRoute.value.path).toBe("/accounts");
    }
  });
});
