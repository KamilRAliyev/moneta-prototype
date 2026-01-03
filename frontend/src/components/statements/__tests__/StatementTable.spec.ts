import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import StatementTable from "../StatementTable.vue";
import type { StatementFileSummary } from "../../../types/statements";

const mockStatements: StatementFileSummary[] = [
  {
    id: "550e8400-e29b-41d4-a716-446655440000",
    account_id: 1,
    account_name: "Test Account",
    original_filename: "statement_2024_01.csv",
    size_bytes: 10240,
    row_count: 150,
    date_from: "2024-01-01",
    date_to: "2024-01-31",
    status: "uploaded",
    is_ingested: false,
    ingested_at: null,
    file_exists: true,
    created_at: "2025-12-26T10:00:00Z",
  },
  {
    id: "660e8400-e29b-41d4-a716-446655440001",
    account_id: 2,
    account_name: "Another Account",
    original_filename: "statement_2024_02.csv",
    size_bytes: 20480,
    row_count: 300,
    date_from: "2024-02-01",
    date_to: "2024-02-29",
    status: "uploaded",
    is_ingested: true,
    ingested_at: "2025-12-27T10:00:00Z",
    file_exists: false,
    created_at: "2025-12-27T10:00:00Z",
  },
];

describe("StatementTable", () => {
  it("renders table with statements", () => {
    const wrapper = mount(StatementTable, {
      props: {
        statements: mockStatements,
      },
    });

    expect(wrapper.find("table").exists()).toBe(true);
    expect(wrapper.text()).toContain("statement_2024_01.csv");
    expect(wrapper.text()).toContain("statement_2024_02.csv");
  });

  it("displays all statement fields", () => {
    const wrapper = mount(StatementTable, {
      props: {
        statements: [mockStatements[0]],
      },
    });

    expect(wrapper.text()).toContain("statement_2024_01.csv");
    expect(wrapper.text()).toContain("Test Account");
    expect(wrapper.text()).toContain("10.00 KB");
    expect(wrapper.text()).toContain("150");
  });

  it("formats file size correctly", () => {
    const wrapper = mount(StatementTable, {
      props: {
        statements: [
          {
            ...mockStatements[0],
            size_bytes: 1024, // 1 KB
          },
        ],
      },
    });

    expect(wrapper.text()).toContain("1.00 KB");
  });

  it("formats date range correctly", () => {
    const wrapper = mount(StatementTable, {
      props: {
        statements: [mockStatements[0]],
      },
    });

    // Date range should be formatted
    expect(wrapper.text()).toMatch(/\d+\/\d+\/\d+.*\d+\/\d+\/\d+/);
  });

  it("shows loading state with skeleton loaders", () => {
    const wrapper = mount(StatementTable, {
      props: {
        statements: [],
        isLoading: true,
      },
    });

    // Should show skeleton loaders instead of "Loading statements..." text
    const skeletons = wrapper.findAll('[class*="animate-pulse"]');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("shows empty state", () => {
    const wrapper = mount(StatementTable, {
      props: {
        statements: [],
        isLoading: false,
      },
    });

    expect(wrapper.text()).toContain("No statements found");
  });

  it("displays ingested status correctly", () => {
    const wrapper = mount(StatementTable, {
      props: {
        statements: mockStatements,
      },
    });

    expect(wrapper.text()).toContain("Not ingested");
    expect(wrapper.text()).toContain("Ingested");
  });

  it("displays file existence status correctly", () => {
    const wrapper = mount(StatementTable, {
      props: {
        statements: mockStatements,
      },
    });

    expect(wrapper.text()).toContain("Exists");
    expect(wrapper.text()).toContain("Missing");
  });

  it("emits delete event when delete button is clicked", async () => {
    const wrapper = mount(StatementTable, {
      props: {
        statements: [mockStatements[0]],
      },
    });

    const deleteButton = wrapper
      .findAll("button")
      .find((btn) => btn.text().includes("Delete"));
    await deleteButton?.trigger("click");

    expect(wrapper.emitted("delete")).toBeTruthy();
    expect(wrapper.emitted("delete")?.[0]).toEqual([mockStatements[0]]);
  });

  it("formats row count with locale string", () => {
    const wrapper = mount(StatementTable, {
      props: {
        statements: [
          {
            ...mockStatements[0],
            row_count: 1125,
          },
        ],
      },
    });

    expect(wrapper.text()).toContain("1,125");
  });
});
