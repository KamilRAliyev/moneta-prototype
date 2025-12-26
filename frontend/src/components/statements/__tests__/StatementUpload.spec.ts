import { describe, it, expect, beforeEach, vi } from "vitest";
import { mount } from "@vue/test-utils";
import StatementUpload from "../StatementUpload.vue";
import { accountsService } from "../../../services/accounts";
import type { Account } from "../../../types/accounts";

// Mock the accounts service
vi.mock("../../../services/accounts", () => ({
  accountsService: {
    listAccounts: vi.fn(),
  },
}));

const mockedAccountsService = vi.mocked(accountsService);

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
  {
    id: 2,
    name: "Another Account",
    institution: "Another Bank",
    currency: "EUR",
    account_type: "savings",
    economic_area: null,
    datelock_from: null,
    created_at: "2025-01-01T00:00:00Z",
    updated_at: null,
  },
];

describe("StatementUpload", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedAccountsService.listAccounts.mockResolvedValue(mockAccounts);
  });

  it("renders upload form", async () => {
    const wrapper = mount(StatementUpload);

    await new Promise((resolve) => setTimeout(resolve, 100));

    expect(wrapper.text()).toContain("Account");
    expect(wrapper.text()).toContain("CSV File");
    expect(wrapper.text()).toContain("Upload Statement");
  });

  it("loads accounts on mount", async () => {
    mount(StatementUpload);

    await new Promise((resolve) => setTimeout(resolve, 100));

    expect(mockedAccountsService.listAccounts).toHaveBeenCalledTimes(1);
  });

  it("displays accounts in dropdown", async () => {
    const wrapper = mount(StatementUpload);

    await new Promise((resolve) => setTimeout(resolve, 100));
    await wrapper.vm.$nextTick();

    const select = wrapper.find("select");
    expect(select.exists()).toBe(true);
    expect(select.text()).toContain("Test Account");
    expect(select.text()).toContain("Another Account");
  });

  it("validates account selection", async () => {
    const wrapper = mount(StatementUpload);

    await new Promise((resolve) => setTimeout(resolve, 100));
    await wrapper.vm.$nextTick();

    // Directly call handleUpload to trigger validation
    const vm = wrapper.vm as any;
    vm.handleUpload();
    await wrapper.vm.$nextTick();

    // Should show error for missing account
    expect(wrapper.text()).toContain("Please select an account");
  });

  it("validates file selection", async () => {
    const wrapper = mount(StatementUpload);

    await new Promise((resolve) => setTimeout(resolve, 100));
    await wrapper.vm.$nextTick();

    // Set account but no file
    const select = wrapper.find("select");
    await select.setValue(1);
    await wrapper.vm.$nextTick();

    // Directly call handleUpload to trigger validation
    const vm = wrapper.vm as any;
    vm.handleUpload();
    await wrapper.vm.$nextTick();

    // Should show error for missing file
    expect(wrapper.text()).toContain("Please select a CSV file");
  });

  it("validates CSV file type", async () => {
    const wrapper = mount(StatementUpload);

    await new Promise((resolve) => setTimeout(resolve, 100));

    const file = new File(["content"], "test.txt", { type: "text/plain" });
    const input = wrapper.find('input[type="file"]');
    const inputElement = input.element as HTMLInputElement;

    // Create a FileList mock
    const fileList = {
      0: file,
      length: 1,
      item: (index: number) => (index === 0 ? file : null),
      [Symbol.iterator]: function* () {
        yield file;
      },
    } as FileList;

    Object.defineProperty(inputElement, "files", {
      value: fileList,
      writable: false,
    });

    await input.trigger("change");
    await wrapper.vm.$nextTick();

    // Should show error for non-CSV file
    expect(wrapper.text()).toContain("Only CSV files are allowed");
  });

  it("validates file size", async () => {
    const wrapper = mount(StatementUpload);

    await new Promise((resolve) => setTimeout(resolve, 100));

    // Create a file larger than 50MB
    const largeFile = new File(["x".repeat(51 * 1024 * 1024)], "large.csv", {
      type: "text/csv",
    });
    const input = wrapper.find('input[type="file"]');
    const inputElement = input.element as HTMLInputElement;

    // Create a FileList mock
    const fileList = {
      0: largeFile,
      length: 1,
      item: (index: number) => (index === 0 ? largeFile : null),
      [Symbol.iterator]: function* () {
        yield largeFile;
      },
    } as FileList;

    Object.defineProperty(inputElement, "files", {
      value: fileList,
      writable: false,
    });

    await input.trigger("change");
    await wrapper.vm.$nextTick();

    // Should show error for file too large
    expect(wrapper.text()).toContain("File size must be less than 50MB");
  });

  it("accepts valid CSV file", async () => {
    const wrapper = mount(StatementUpload);

    await new Promise((resolve) => setTimeout(resolve, 100));

    const file = new File(["Date,Amount\n2024-01-01,100"], "test.csv", {
      type: "text/csv",
    });
    const input = wrapper.find('input[type="file"]');
    const inputElement = input.element as HTMLInputElement;

    // Create a FileList mock
    const fileList = {
      0: file,
      length: 1,
      item: (index: number) => (index === 0 ? file : null),
      [Symbol.iterator]: function* () {
        yield file;
      },
    } as FileList;

    Object.defineProperty(inputElement, "files", {
      value: fileList,
      writable: false,
    });

    await input.trigger("change");
    await wrapper.vm.$nextTick();

    // Should display selected file
    expect(wrapper.text()).toContain("test.csv");
  });

  it("emits upload event with file and account ID", async () => {
    const wrapper = mount(StatementUpload);

    await new Promise((resolve) => setTimeout(resolve, 100));

    // Set account
    const select = wrapper.find("select");
    await select.setValue(1);
    await wrapper.vm.$nextTick();

    // Set file
    const file = new File(["Date,Amount\n2024-01-01,100"], "test.csv", {
      type: "text/csv",
    });
    const input = wrapper.find('input[type="file"]');
    const inputElement = input.element as HTMLInputElement;

    // Create a FileList mock
    const fileList = {
      0: file,
      length: 1,
      item: (index: number) => (index === 0 ? file : null),
      [Symbol.iterator]: function* () {
        yield file;
      },
    } as FileList;

    Object.defineProperty(inputElement, "files", {
      value: fileList,
      writable: false,
    });

    await input.trigger("change");
    await wrapper.vm.$nextTick();

    // Click upload
    const uploadButton = wrapper
      .findAll("button")
      .find((btn) => btn.text().includes("Upload Statement"));
    await uploadButton?.trigger("click");
    await wrapper.vm.$nextTick();

    expect(wrapper.emitted("upload")).toBeTruthy();
    const uploadEvent = wrapper.emitted("upload")?.[0];
    expect(uploadEvent?.[0]).toBeInstanceOf(File);
    expect(uploadEvent?.[1]).toBe(1);
  });

  it("shows loading state", () => {
    const wrapper = mount(StatementUpload, {
      props: {
        isLoading: true,
      },
    });

    expect(wrapper.text()).toContain("Uploading...");
    const uploadButton = wrapper
      .findAll("button")
      .find((btn) => btn.text().includes("Uploading..."));
    expect(uploadButton?.exists()).toBe(true);
  });

  it("displays error message", () => {
    const wrapper = mount(StatementUpload, {
      props: {
        error: "Upload failed",
      },
    });

    expect(wrapper.text()).toContain("Upload failed");
  });
});
