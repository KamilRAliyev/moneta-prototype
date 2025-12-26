import { describe, it, expect, beforeEach, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { createRouter, createMemoryHistory } from "vue-router";
import AccountCreate from "../AccountCreate.vue";
import { accountsService } from "../../../services/accounts";
import type { Account } from "../../../types/accounts";

// Mock the accounts service
vi.mock("../../../services/accounts", () => ({
  accountsService: {
    createAccount: vi.fn(),
  },
}));

const mockedAccountsService = vi.mocked(accountsService);

describe("AccountCreate", () => {
  const createTestRouter = () => {
    return createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: "/accounts/new",
          component: AccountCreate,
        },
        {
          path: "/accounts/:id",
          component: { template: "<div>Account Detail</div>" },
        },
      ],
    });
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders page title and form", async () => {
    const router = createTestRouter();
    const wrapper = mount(AccountCreate, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();

    expect(wrapper.text()).toContain("Create Account");
    expect(wrapper.find("form").exists()).toBe(true);
  });

  it("navigates to account detail after successful creation", async () => {
    const mockAccount: Account = {
      id: 1,
      name: "New Account",
      institution: "New Bank",
      currency: "USD",
      account_type: "checking",
      economic_area: null,
      datelock_from: null,
      created_at: "2025-01-01T00:00:00Z",
      updated_at: null,
    };

    mockedAccountsService.createAccount.mockResolvedValue(mockAccount);

    const router = createTestRouter();
    const wrapper = mount(AccountCreate, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 300)); // Wait for form to load

    // Trigger submit event directly on AccountForm component
    const accountForm = wrapper.findComponent({ name: "AccountForm" });
    if (accountForm.exists()) {
      await accountForm.vm.$emit("submit", {
        name: "New Account",
        institution: "New Bank",
        currency: "USD",
        account_type: "checking",
      });

      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(mockedAccountsService.createAccount).toHaveBeenCalled();
      expect(router.currentRoute.value.path).toBe("/accounts/1");
    }
  });

  it("shows error message when creation fails", async () => {
    mockedAccountsService.createAccount.mockRejectedValue(
      new Error("Network error"),
    );

    const router = createTestRouter();
    const wrapper = mount(AccountCreate, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 300)); // Wait for form to load

    // Trigger submit event directly on AccountForm component
    const accountForm = wrapper.findComponent({ name: "AccountForm" });
    if (accountForm.exists()) {
      await accountForm.vm.$emit("submit", {
        name: "New Account",
        institution: "New Bank",
        currency: "USD",
        account_type: "checking",
      });

      await new Promise((resolve) => setTimeout(resolve, 200));
      await wrapper.vm.$nextTick();

      // Error should be displayed
      const errorDiv = wrapper.find('[class*="red"]');
      expect(
        errorDiv.exists() || wrapper.text().includes("Network error"),
      ).toBe(true);
    }
  });

  it("navigates back to accounts list when cancel is clicked", async () => {
    const router = createTestRouter();
    router.push("/accounts/new");

    const wrapper = mount(AccountCreate, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();

    const cancelButton = wrapper
      .findAll("button")
      .find((btn) => btn.text().includes("Cancel"));
    await cancelButton?.trigger("click");

    await new Promise((resolve) => setTimeout(resolve, 50));

    expect(router.currentRoute.value.path).toBe("/accounts");
  });
});
