import { describe, it, expect, beforeEach, vi } from "vitest";
import { mount } from "@vue/test-utils";
import AccountForm from "../AccountForm.vue";
import { useAccountMeta } from "../../../composables/useAccountMeta";
import type { Account } from "../../../types/accounts";

// Mock the composable
vi.mock("../../../composables/useAccountMeta", () => ({
  useAccountMeta: vi.fn(),
}));

const mockMeta = {
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
    { value: "EUR", name: "Euro", digits: 2 },
  ],
};

describe("AccountForm", () => {
  beforeEach(() => {
    vi.mocked(useAccountMeta).mockReturnValue({
      fetchMeta: vi.fn().mockResolvedValue(mockMeta),
      clearCache: vi.fn(),
      isLoading: { value: false },
      error: { value: null },
      cached: () => null,
    });
  });

  it("renders form fields", async () => {
    const wrapper = mount(AccountForm);

    await wrapper.vm.$nextTick();

    expect(wrapper.find('input[id="name"]').exists()).toBe(true);
    expect(wrapper.find('input[id="institution"]').exists()).toBe(true);
    expect(wrapper.find('select[id="currency"]').exists()).toBe(true);
    expect(wrapper.find('select[id="accountType"]').exists()).toBe(true);
    expect(wrapper.find('select[id="economicArea"]').exists()).toBe(true);
  });

  it("pre-fills form when account prop is provided", async () => {
    const account: Account = {
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
    };

    const wrapper = mount(AccountForm, {
      props: {
        account,
      },
    });

    await wrapper.vm.$nextTick();
    await new Promise((resolve) => setTimeout(resolve, 100));

    const nameInput = wrapper.find('input[id="name"]')
      .element as HTMLInputElement;
    expect(nameInput.value).toBe("Test Account");
  });

  it("validates required fields", async () => {
    const wrapper = mount(AccountForm);

    await wrapper.vm.$nextTick();

    const form = wrapper.find("form");
    await form.trigger("submit");

    // Should show validation errors
    expect(wrapper.text()).toContain("Account name is required");
  });

  it("emits submit event with form data", async () => {
    const wrapper = mount(AccountForm);

    await wrapper.vm.$nextTick();
    await new Promise((resolve) => setTimeout(resolve, 300)); // Wait for meta to load

    // Fill in form using component instance
    const vm = wrapper.vm as any;
    vm.name = "New Account";
    vm.institution = "New Bank";
    vm.currency = "USD";
    vm.accountType = "checking";

    await wrapper.vm.$nextTick();

    const form = wrapper.find("form");
    await form.trigger("submit");

    await wrapper.vm.$nextTick();
    await new Promise((resolve) => setTimeout(resolve, 50));

    expect(wrapper.emitted("submit")).toBeTruthy();
    const submitData = wrapper.emitted("submit")?.[0]?.[0];
    expect(submitData).toMatchObject({
      name: "New Account",
      institution: "New Bank",
      currency: "USD",
      account_type: "checking",
    });
  });

  it("emits cancel event when cancel button is clicked", async () => {
    const wrapper = mount(AccountForm);

    await wrapper.vm.$nextTick();

    const cancelButton = wrapper
      .findAll("button")
      .find((btn) => btn.text().includes("Cancel"));
    await cancelButton?.trigger("click");

    expect(wrapper.emitted("cancel")).toBeTruthy();
  });

  it("shows error message when error prop is provided", () => {
    const wrapper = mount(AccountForm, {
      props: {
        error: "Failed to save account",
      },
    });

    expect(wrapper.text()).toContain("Failed to save account");
  });

  it("disables submit button when loading", () => {
    const wrapper = mount(AccountForm, {
      props: {
        isLoading: true,
      },
    });

    const submitButton = wrapper
      .findAll("button")
      .find((btn) => btn.text().includes("Saving"));
    expect(submitButton?.attributes("disabled")).toBeDefined();
  });

  it("shows correct button text for create mode", () => {
    const wrapper = mount(AccountForm);

    expect(wrapper.text()).toContain("Create Account");
  });

  it("shows correct button text for edit mode", () => {
    const account: Account = {
      id: 1,
      name: "Test",
      institution: "Bank",
      currency: "USD",
      account_type: "checking",
      economic_area: null,
      datelock_from: null,
      datelock_to: null,
      created_at: "2025-01-01T00:00:00Z",
      updated_at: null,
    };

    const wrapper = mount(AccountForm, {
      props: {
        account,
      },
    });

    expect(wrapper.text()).toContain("Save Changes");
  });
});
