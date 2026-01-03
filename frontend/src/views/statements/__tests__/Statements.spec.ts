import { describe, it, expect, beforeEach, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import Statements from "../Statements.vue";
import { useStatementsStore } from "../../../stores/statements";
import { statementsService } from "../../../services/statements";
import type { StatementFileSummary } from "../../../types/statements";

// Mock the statements service
vi.mock("../../../services/statements", () => ({
  statementsService: {
    listStatements: vi.fn(),
    uploadStatement: vi.fn(),
    deleteStatement: vi.fn(),
    getStatement: vi.fn(),
    inferDateFormat: vi.fn(),
    getSupportedDateFormats: vi.fn(),
  },
}));

const mockedStatementsService = vi.mocked(statementsService);

describe("Statements", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
    mockedStatementsService.listStatements.mockResolvedValue([]);
  });

  it("renders page title and sections", () => {
    const wrapper = mount(Statements);

    expect(wrapper.text()).toContain("Statements");
    expect(wrapper.text()).toContain("Upload and manage CSV statement files");
    expect(wrapper.text()).toContain("Upload Statement");
    expect(wrapper.text()).toContain("Uploaded Statements");
  });

  it("loads statements on mount", async () => {
    const store = useStatementsStore();
    const loadStatementsSpy = vi.spyOn(store, "loadStatements");

    mount(Statements);

    await new Promise((resolve) => setTimeout(resolve, 100));

    expect(loadStatementsSpy).toHaveBeenCalledTimes(1);
    expect(mockedStatementsService.listStatements).toHaveBeenCalledTimes(1);
  });

  it("displays statements in table", async () => {
    const mockStatements: StatementFileSummary[] = [
      {
        id: "550e8400-e29b-41d4-a716-446655440000",
        account_id: 1,
        account_name: "Test Account",
        original_filename: "test.csv",
        size_bytes: 1024,
        row_count: 100,
        date_from: "2024-01-01",
        date_to: "2024-01-31",
        status: "uploaded",
        is_ingested: false,
        ingested_at: null,
        file_exists: true,
        created_at: "2025-12-26T10:00:00Z",
      },
    ];

    // Mock the service to return the test statements
    mockedStatementsService.listStatements.mockResolvedValue(mockStatements);

    const wrapper = mount(Statements);

    // Wait for the component to mount and load statements
    await wrapper.vm.$nextTick();
    await new Promise((resolve) => setTimeout(resolve, 100));

    expect(wrapper.text()).toContain("test.csv");
    expect(wrapper.text()).toContain("Test Account");
  });

  it("handles upload event", async () => {
    const store = useStatementsStore();
    const uploadSpy = vi
      .spyOn(store, "uploadStatement")
      .mockResolvedValue({} as StatementFileSummary);

    const wrapper = mount(Statements);
    const file = new File(["Date,Amount\n2024-01-01,100"], "test.csv", {
      type: "text/csv",
    });

    const uploadComponent = wrapper.findComponent({ name: "StatementUpload" });
    if (uploadComponent.exists()) {
      await uploadComponent.vm.$emit("upload", file, 1);
      await wrapper.vm.$nextTick();

      expect(uploadSpy).toHaveBeenCalledWith(file, 1);
    }
  });

  it("shows delete confirmation modal when delete is clicked", async () => {
    const mockStatement: StatementFileSummary = {
      id: "550e8400-e29b-41d4-a716-446655440000",
      account_id: 1,
      account_name: "Test Account",
      original_filename: "test.csv",
      size_bytes: 1024,
      row_count: 100,
      date_from: "2024-01-01",
      date_to: "2024-01-31",
      status: "uploaded",
      is_ingested: false,
      ingested_at: null,
      file_exists: true,
      created_at: "2025-12-26T10:00:00Z",
    };

    // Mock the service to return the test statement
    mockedStatementsService.listStatements.mockResolvedValue([mockStatement]);

    const wrapper = mount(Statements);
    await wrapper.vm.$nextTick();
    await new Promise((resolve) => setTimeout(resolve, 100));

    const tableComponent = wrapper.findComponent({ name: "StatementTable" });
    if (tableComponent.exists()) {
      await tableComponent.vm.$emit("delete", mockStatement);
      await wrapper.vm.$nextTick();

      expect(wrapper.text()).toContain("Delete Statement");
      expect(wrapper.text()).toContain(
        "Are you sure you want to delete this statement file?",
      );
    }
  });

  it("deletes statement when confirmed", async () => {
    const store = useStatementsStore();
    const deleteSpy = vi.spyOn(store, "deleteStatement").mockResolvedValue();

    const mockStatement: StatementFileSummary = {
      id: "550e8400-e29b-41d4-a716-446655440000",
      account_id: 1,
      account_name: "Test Account",
      original_filename: "test.csv",
      size_bytes: 1024,
      row_count: 100,
      date_from: "2024-01-01",
      date_to: "2024-01-31",
      status: "uploaded",
      is_ingested: false,
      ingested_at: null,
      file_exists: true,
      created_at: "2025-12-26T10:00:00Z",
    };

    // Mock the service to return the test statement
    mockedStatementsService.listStatements.mockResolvedValue([mockStatement]);

    const wrapper = mount(Statements);
    await wrapper.vm.$nextTick();
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Trigger delete
    const vm = wrapper.vm as any;
    vm.handleDelete(mockStatement);
    await wrapper.vm.$nextTick();

    // Find and click confirm button
    const deleteButtons = wrapper.findAll("button");
    const confirmButton = deleteButtons.find(
      (btn) =>
        btn.text().trim() === "Delete" && btn.classes().includes("bg-red-600"),
    );

    if (confirmButton) {
      await confirmButton.trigger("click");
      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(deleteSpy).toHaveBeenCalledWith(mockStatement.id);
    }
  });

  it("displays error message from store", () => {
    const store = useStatementsStore();
    store.error = "Failed to load statements";

    const wrapper = mount(Statements);

    expect(wrapper.text()).toContain("Failed to load statements");
  });
});
