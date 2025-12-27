import { apiClient } from "./api";
import type {
  TransactionListResponse,
  TransactionMetaResponse,
  DeleteTransactionsResponse,
} from "../types/transactions";

/**
 * Transactions service
 */
export const transactionsService = {
  /**
   * List transactions with pagination, sorting, and filtering
   */
  async listTransactions(params: {
    account_id?: number;
    statement_file_id?: string;
    page?: number;
    page_size?: number;
    sort_by?: string;
    sort_dir?: "asc" | "desc";
    filters?: string;
  }): Promise<TransactionListResponse> {
    const queryParams: Record<string, string | number> = {};
    if (params.account_id !== undefined) {
      queryParams.account_id = params.account_id;
    }
    if (params.statement_file_id !== undefined) {
      queryParams.statement_file_id = params.statement_file_id;
    }
    if (params.page !== undefined) {
      queryParams.page = params.page;
    }
    if (params.page_size !== undefined) {
      queryParams.page_size = params.page_size;
    }
    if (params.sort_by !== undefined) {
      queryParams.sort_by = params.sort_by;
    }
    if (params.sort_dir !== undefined) {
      queryParams.sort_dir = params.sort_dir;
    }
    if (params.filters !== undefined) {
      queryParams.filters = params.filters;
    }

    const response = await apiClient.get<TransactionListResponse>(
      "/transactions",
      { params: queryParams },
    );
    return response.data;
  },

  /**
   * Get transaction column metadata
   */
  async getTransactionMeta(
    accountId?: number,
  ): Promise<TransactionMetaResponse> {
    const params: Record<string, number> = {};
    if (accountId !== undefined) {
      params.account_id = accountId;
    }

    const response = await apiClient.get<TransactionMetaResponse>(
      "/transactions/meta",
      { params },
    );
    return response.data;
  },

  /**
   * Delete transactions with optional account filter
   */
  async deleteTransactions(
    accountId?: number,
  ): Promise<DeleteTransactionsResponse> {
    const params: Record<string, number> = {};
    if (accountId !== undefined) {
      params.account_id = accountId;
    }

    const response = await apiClient.delete<DeleteTransactionsResponse>(
      "/transactions",
      { params },
    );
    return response.data;
  },
};
