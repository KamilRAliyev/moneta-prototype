import { apiClient } from "./api";
import type {
  Account,
  AccountCreateRequest,
  AccountUpdateRequest,
  MetaOptionsResponse,
} from "../types/accounts";

/**
 * Accounts service
 */
export const accountsService = {
  /**
   * List all accounts with pagination
   */
  async listAccounts(skip = 0, limit = 100): Promise<Account[]> {
    const response = await apiClient.get<Account[]>("/accounts", {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Get account by ID
   */
  async getAccount(id: number): Promise<Account> {
    const response = await apiClient.get<Account>(`/accounts/${id}`);
    return response.data;
  },

  /**
   * Create a new account
   */
  async createAccount(payload: AccountCreateRequest): Promise<Account> {
    const response = await apiClient.post<Account>("/accounts", payload);
    return response.data;
  },

  /**
   * Update an existing account
   */
  async updateAccount(
    id: number,
    payload: AccountUpdateRequest,
  ): Promise<Account> {
    const response = await apiClient.put<Account>(`/accounts/${id}`, payload);
    return response.data;
  },

  /**
   * Delete an account
   */
  async deleteAccount(id: number): Promise<void> {
    await apiClient.delete(`/accounts/${id}`);
  },

  /**
   * Get meta options (account types, economic areas, currencies)
   */
  async getAccountMetaOptions(): Promise<MetaOptionsResponse> {
    const response = await apiClient.get<MetaOptionsResponse>(
      "/meta/accounts/options",
    );
    return response.data;
  },
};
