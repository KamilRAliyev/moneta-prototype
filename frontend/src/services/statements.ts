import { apiClient } from "./api";
import type {
  StatementFile,
  StatementFileSummary,
  DateFormatInferenceResponse,
  SupportedDateFormatsResponse,
} from "../types/statements";

/**
 * Statements service
 */
export const statementsService = {
  /**
   * Upload a CSV statement file for an account
   */
  async uploadStatement(file: File, accountId: number): Promise<StatementFile> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiClient.post<StatementFile>(
      `/statements?account_id=${accountId}`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );
    return response.data;
  },

  /**
   * List statement files with optional filtering and pagination
   */
  async listStatements(
    accountId?: number,
    skip = 0,
    limit = 100,
  ): Promise<StatementFileSummary[]> {
    const params: Record<string, string | number> = { skip, limit };
    if (accountId !== undefined) {
      params.account_id = accountId;
    }

    const response = await apiClient.get<StatementFileSummary[]>(
      "/statements",
      { params },
    );
    return response.data;
  },

  /**
   * Get statement file by ID
   */
  async getStatement(id: string): Promise<StatementFile> {
    const response = await apiClient.get<StatementFile>(`/statements/${id}`);
    return response.data;
  },

  /**
   * Delete a statement file
   */
  async deleteStatement(id: string): Promise<void> {
    await apiClient.delete(`/statements/${id}`);
  },

  /**
   * Infer date format from a CSV file
   */
  async inferDateFormat(file: File): Promise<DateFormatInferenceResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiClient.post<DateFormatInferenceResponse>(
      "/meta/statements/infer-date-format",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );
    return response.data;
  },

  /**
   * Get list of supported date formats
   */
  async getSupportedDateFormats(): Promise<SupportedDateFormatsResponse> {
    const response = await apiClient.get<SupportedDateFormatsResponse>(
      "/meta/statements/date-formats",
    );
    return response.data;
  },
};
