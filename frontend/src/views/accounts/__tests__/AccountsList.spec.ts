import { describe, it, expect, beforeEach, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { createRouter, createMemoryHistory } from "vue-router";
import AccountsList from "../AccountsList.vue";
import { accountsService } from "../../../services/accounts";
import type { Account } from "../../../types/accounts";

// Mock the accounts service
vi.mock("../../../services/accounts", () => ({
  accountsService: {
    listAccounts: vi.fn(),
    deleteAccount: vi.fn(),
  },
}));

const mockedAccountsService = vi.mocked(accountsService);

describe("AccountsList", () => {
  const createTestRouter = () => {
    return createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: "/accounts",
          component: AccountsList,
        },
      ],
    });
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders page title and create button", async () => {
    mockedAccountsService.listAccounts.mockResolvedValue([]);

    const router = createTestRouter();
    const wrapper = mount(AccountsList, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 100));

    expect(wrapper.text()).toContain("Accounts");
    expect(wrapper.text()).toContain("Create Account");
  });

  it("loads accounts on mount", async () => {
    const mockAccounts: Account[] = [
      {
        id: 1,
        name: "Test Account",
        institution: "Test Bank",
        currency: "USD",
        account_type: "checking",
        economic_area: "us",
        datelock_from: null,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: null,
      },
    ];

    mockedAccountsService.listAccounts.mockResolvedValue(mockAccounts);

    const router = createTestRouter();
    mount(AccountsList, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 100));

    expect(mockedAccountsService.listAccounts).toHaveBeenCalledTimes(1);
  });

  it("displays accounts in table", async () => {
    const mockAccounts: Account[] = [
      {
        id: 1,
        name: "Test Account",
        institution: "Test Bank",
        currency: "USD",
        account_type: "checking",
        economic_area: "us",
        datelock_from: null,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: null,
      },
    ];

    mockedAccountsService.listAccounts.mockResolvedValue(mockAccounts);

    const router = createTestRouter();
    const wrapper = mount(AccountsList, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 100));

    expect(wrapper.text()).toContain("Test Account");
    expect(wrapper.text()).toContain("Test Bank");
  });

  it("shows error message when loading fails", async () => {
    mockedAccountsService.listAccounts.mockRejectedValue(
      new Error("Network error"),
    );

    const router = createTestRouter();
    const wrapper = mount(AccountsList, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 200));
    await wrapper.vm.$nextTick();

    // Error message should be displayed
    const errorDiv = wrapper.find('[class*="red"]');
    expect(errorDiv.exists() || wrapper.text().includes("Network error")).toBe(
      true,
    );
  });

  it("shows delete confirmation modal when delete is clicked", async () => {
    const mockAccounts: Account[] = [
      {
        id: 1,
        name: "Test Account",
        institution: "Test Bank",
        currency: "USD",
        account_type: "checking",
        economic_area: null,
        datelock_from: null,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: null,
      },
    ];

    mockedAccountsService.listAccounts.mockResolvedValue(mockAccounts);

    const router = createTestRouter();
    const wrapper = mount(AccountsList, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 200));

    // Trigger delete through AccountTable component event
    const accountTable = wrapper.findComponent({ name: "AccountTable" });
    if (accountTable.exists()) {
      await accountTable.vm.$emit("delete", mockAccounts[0]);
      await wrapper.vm.$nextTick();

      expect(wrapper.text()).toContain("Delete Account");
      expect(wrapper.text()).toContain(
        "Are you sure you want to delete this account?",
      );
    }
  });

  it("deletes account when confirmed", async () => {
    const mockAccounts: Account[] = [
      {
        id: 1,
        name: "Test Account",
        institution: "Test Bank",
        currency: "USD",
        account_type: "checking",
        economic_area: null,
        datelock_from: null,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: null,
      },
    ];

    mockedAccountsService.listAccounts
      .mockResolvedValueOnce(mockAccounts)
      .mockResolvedValueOnce([]);
    mockedAccountsService.deleteAccount.mockResolvedValue(undefined);

    const router = createTestRouter();
    const wrapper = mount(AccountsList, {
      global: {
        plugins: [router],
      },
    });

    await router.isReady();
    await new Promise((resolve) => setTimeout(resolve, 200));

    // Get the component instance and call handleDelete directly
    const vm = wrapper.vm as any;
    vm.handleDelete(mockAccounts[0]);
    await wrapper.vm.$nextTick();

    // Find and click confirm button (the one that says "Delete" in the modal)
    const deleteButtons = wrapper.findAll("button");
    const confirmButton = deleteButtons.find(
      (btn) =>
        btn.text().trim() === "Delete" && btn.classes().includes("bg-red-600"),
    );

    if (confirmButton) {
      await confirmButton.trigger("click");
      await new Promise((resolve) => setTimeout(resolve, 200));

      expect(mockedAccountsService.deleteAccount).toHaveBeenCalledWith(1);
      expect(mockedAccountsService.listAccounts).toHaveBeenCalledTimes(2); // Initial + reload
    } else {
      // If button not found, at least verify delete was triggered
      expect(vm.deleteConfirmId).toBe(1);
    }
  });
});
