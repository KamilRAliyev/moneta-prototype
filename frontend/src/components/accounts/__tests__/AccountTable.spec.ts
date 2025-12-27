import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import AccountTable from "../AccountTable.vue";
import type { Account } from "../../../types/accounts";

const mockAccounts: Account[] = [
  {
    id: 1,
    name: "Test Account",
    institution: "Test Bank",
    currency: "USD",
    account_type: "checking",
    economic_area: "us",
    datelock_from: "2023-01-01",
    datelock_to: "2023-12-31",
    created_at: "2025-01-01T00:00:00Z",
    updated_at: null,
  },
  {
    id: 2,
    name: "Savings Account",
    institution: "Another Bank",
    currency: "EUR",
    account_type: "savings",
    economic_area: null,
    datelock_from: null,
    datelock_to: null,
    created_at: "2025-01-01T00:00:00Z",
    updated_at: null,
  },
];

describe("AccountTable", () => {
  it("renders table with accounts", () => {
    const wrapper = mount(AccountTable, {
      props: {
        accounts: mockAccounts,
      },
    });

    expect(wrapper.find("table").exists()).toBe(true);
    expect(wrapper.text()).toContain("Test Account");
    expect(wrapper.text()).toContain("Savings Account");
  });

  it("displays all account fields", () => {
    const wrapper = mount(AccountTable, {
      props: {
        accounts: [mockAccounts[0]],
      },
    });

    expect(wrapper.text()).toContain("Test Account");
    expect(wrapper.text()).toContain("Test Bank");
    expect(wrapper.text()).toContain("USD");
    expect(wrapper.text()).toContain("Checking");
    expect(wrapper.text()).toContain("us");
  });

  it("formats date lock correctly", () => {
    const wrapper = mount(AccountTable, {
      props: {
        accounts: mockAccounts,
      },
    });

    expect(wrapper.text()).toContain("2023-01-01 to 2023-12-31");
    expect(wrapper.text()).toContain("No date lock");
  });

  it("formats account type correctly", () => {
    const wrapper = mount(AccountTable, {
      props: {
        accounts: [
          {
            ...mockAccounts[0],
            account_type: "credit_card",
          },
        ],
      },
    });

    expect(wrapper.text()).toContain("Credit Card");
  });

  it("shows loading state", () => {
    const wrapper = mount(AccountTable, {
      props: {
        accounts: [],
        isLoading: true,
      },
    });

    expect(wrapper.text()).toContain("Loading accounts...");
  });

  it("shows empty state", () => {
    const wrapper = mount(AccountTable, {
      props: {
        accounts: [],
        isLoading: false,
      },
    });

    expect(wrapper.text()).toContain("No accounts found");
  });

  it("emits view event when row is clicked", async () => {
    const wrapper = mount(AccountTable, {
      props: {
        accounts: [mockAccounts[0]],
      },
    });

    const row = wrapper.find("tbody tr");
    await row.trigger("click");

    expect(wrapper.emitted("view")).toBeTruthy();
    expect(wrapper.emitted("view")?.[0]).toEqual([mockAccounts[0]]);
  });

  it("emits edit event when edit button is clicked", async () => {
    const wrapper = mount(AccountTable, {
      props: {
        accounts: [mockAccounts[0]],
      },
    });

    const editButton = wrapper
      .findAll("button")
      .find((btn) => btn.text().includes("Edit"));
    await editButton?.trigger("click");

    expect(wrapper.emitted("edit")).toBeTruthy();
    expect(wrapper.emitted("edit")?.[0]).toEqual([mockAccounts[0]]);
  });

  it("emits delete event when delete button is clicked", async () => {
    const wrapper = mount(AccountTable, {
      props: {
        accounts: [mockAccounts[0]],
      },
    });

    const deleteButton = wrapper
      .findAll("button")
      .find((btn) => btn.text().includes("Delete"));
    await deleteButton?.trigger("click");

    expect(wrapper.emitted("delete")).toBeTruthy();
    expect(wrapper.emitted("delete")?.[0]).toEqual([mockAccounts[0]]);
  });

  it("does not emit view when action buttons are clicked", async () => {
    const wrapper = mount(AccountTable, {
      props: {
        accounts: [mockAccounts[0]],
      },
    });

    const editButton = wrapper
      .findAll("button")
      .find((btn) => btn.text().includes("Edit"));
    await editButton?.trigger("click");

    // Should not emit view, only edit
    expect(wrapper.emitted("view")).toBeFalsy();
    expect(wrapper.emitted("edit")).toBeTruthy();
  });
});
