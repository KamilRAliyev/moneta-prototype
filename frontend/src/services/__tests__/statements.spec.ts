import { describe, it, expect, beforeEach, vi } from "vitest";
import { statementsService } from "../statements";
import { apiClient } from "../api";
import type {
  StatementFile,
  StatementFileSummary,
  DateFormatInferenceResponse,
  SupportedDateFormatsResponse,
} from "../../types/statements";

// Mock the API client
vi.mock("../api", () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockedApiClient = vi.mocked(apiClient);

describe("Statements Service", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("uploadStatement", () => {
    it("calls API with file and account ID", async () => {
      const file = new File(["Date,Amount\n2024-01-01,100"], "test.csv", {
        type: "text/csv",
      });
      const mockStatement: StatementFile = {
        id: "550e8400-e29b-41d4-a716-446655440000",
        account_id: 1,
        account_name: "Test Account",
        original_filename: "test.csv",
        stored_filename: "550e8400-e29b-41d4-a716-446655440000.csv",
        stored_path:
          "/data/statements/550e8400-e29b-41d4-a716-446655440000.csv",
        format: "csv",
        size_bytes: 1024,
        content_hash: "abc123",
        row_count: 1,
        columns: ["Date", "Amount"],
        date_from: "2024-01-01",
        date_to: "2024-01-01",
        status: "uploaded",
        is_ingested: false,
        ingested_at: null,
        file_exists: true,
        created_at: "2025-12-26T10:00:00Z",
        updated_at: null,
      };

      mockedApiClient.post.mockResolvedValue({
        data: mockStatement,
        status: 201,
        statusText: "Created",
        headers: {},
        config: {} as any,
      });

      const result = await statementsService.uploadStatement(file, 1);

      expect(mockedApiClient.post).toHaveBeenCalledWith(
        "/statements?account_id=1",
        expect.any(FormData),
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        },
      );
      expect(result).toEqual(mockStatement);
    });
  });

  describe("listStatements", () => {
    it("calls API with default pagination", async () => {
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

      mockedApiClient.get.mockResolvedValue({
        data: mockStatements,
        status: 200,
        statusText: "OK",
        headers: {},
        config: {} as any,
      });

      const result = await statementsService.listStatements();

      expect(mockedApiClient.get).toHaveBeenCalledWith("/statements", {
        params: { skip: 0, limit: 100 },
      });
      expect(result).toEqual(mockStatements);
    });

    it("calls API with account filter and pagination", async () => {
      mockedApiClient.get.mockResolvedValue({
        data: [],
        status: 200,
        statusText: "OK",
        headers: {},
        config: {} as any,
      });

      await statementsService.listStatements(1, 10, 20);

      expect(mockedApiClient.get).toHaveBeenCalledWith("/statements", {
        params: { account_id: 1, skip: 10, limit: 20 },
      });
    });
  });

  describe("getStatement", () => {
    it("calls API with statement ID", async () => {
      const mockStatement: StatementFile = {
        id: "550e8400-e29b-41d4-a716-446655440000",
        account_id: 1,
        account_name: "Test Account",
        original_filename: "test.csv",
        stored_filename: "550e8400-e29b-41d4-a716-446655440000.csv",
        stored_path:
          "/data/statements/550e8400-e29b-41d4-a716-446655440000.csv",
        format: "csv",
        size_bytes: 1024,
        content_hash: "abc123",
        row_count: 100,
        columns: ["Date", "Amount"],
        date_from: "2024-01-01",
        date_to: "2024-01-31",
        status: "uploaded",
        is_ingested: false,
        ingested_at: null,
        file_exists: true,
        created_at: "2025-12-26T10:00:00Z",
        updated_at: null,
      };

      mockedApiClient.get.mockResolvedValue({
        data: mockStatement,
        status: 200,
        statusText: "OK",
        headers: {},
        config: {} as any,
      });

      const result = await statementsService.getStatement(
        "550e8400-e29b-41d4-a716-446655440000",
      );

      expect(mockedApiClient.get).toHaveBeenCalledWith(
        "/statements/550e8400-e29b-41d4-a716-446655440000",
      );
      expect(result).toEqual(mockStatement);
    });
  });

  describe("deleteStatement", () => {
    it("calls API with statement ID", async () => {
      mockedApiClient.delete.mockResolvedValue({
        data: undefined,
        status: 204,
        statusText: "No Content",
        headers: {},
        config: {} as any,
      });

      await statementsService.deleteStatement(
        "550e8400-e29b-41d4-a716-446655440000",
      );

      expect(mockedApiClient.delete).toHaveBeenCalledWith(
        "/statements/550e8400-e29b-41d4-a716-446655440000",
      );
    });
  });

  describe("inferDateFormat", () => {
    it("calls API with file", async () => {
      const file = new File(["Date\n2024-01-01"], "test.csv", {
        type: "text/csv",
      });
      const mockResponse: DateFormatInferenceResponse = {
        date_column_detected: true,
        date_column_name: "Date",
        date_column_index: 0,
        inferred_format: {
          strptime_format: "%Y-%m-%d",
          human_readable: "YYYY-MM-DD",
          confidence: 0.95,
          matches: 1,
          total_tested: 1,
        },
        date_range: {
          earliest: "2024-01-01",
          latest: "2024-01-01",
        },
        total_rows_analyzed: 1,
        parsing_errors: 0,
        sample_dates: ["2024-01-01"],
      };

      mockedApiClient.post.mockResolvedValue({
        data: mockResponse,
        status: 200,
        statusText: "OK",
        headers: {},
        config: {} as any,
      });

      const result = await statementsService.inferDateFormat(file);

      expect(mockedApiClient.post).toHaveBeenCalledWith(
        "/meta/statements/infer-date-format",
        expect.any(FormData),
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        },
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe("getSupportedDateFormats", () => {
    it("calls API and returns supported formats", async () => {
      const mockResponse: SupportedDateFormatsResponse = {
        supported_formats: [
          {
            format: "YYYY-MM-DD",
            pattern: "%Y-%m-%d",
            description: "ISO 8601 format",
            example: "2024-01-15",
          },
        ],
      };

      mockedApiClient.get.mockResolvedValue({
        data: mockResponse,
        status: 200,
        statusText: "OK",
        headers: {},
        config: {} as any,
      });

      const result = await statementsService.getSupportedDateFormats();

      expect(mockedApiClient.get).toHaveBeenCalledWith(
        "/meta/statements/date-formats",
      );
      expect(result).toEqual(mockResponse);
    });
  });
});
