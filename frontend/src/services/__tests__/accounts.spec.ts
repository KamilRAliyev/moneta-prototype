import { describe, it, expect, beforeEach, vi } from "vitest";
import { accountsService } from "../accounts";
import { apiClient } from "../api";
import type {
  Account,
  AccountCreateRequest,
  AccountUpdateRequest,
  MetaOptionsResponse,
} from "../../types/accounts";

// Mock the API client
vi.mock("../api", () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockedApiClient = vi.mocked(apiClient);

describe("Accounts Service", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("listAccounts", () => {
    it("calls API with default pagination", async () => {
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

      mockedApiClient.get.mockResolvedValue({
        data: mockAccounts,
        status: 200,
        statusText: "OK",
        headers: {},
        config: {} as any,
      });

      const result = await accountsService.listAccounts();

      expect(mockedApiClient.get).toHaveBeenCalledWith("/accounts", {
        params: { skip: 0, limit: 100 },
      });
      expect(result).toEqual(mockAccounts);
    });

    it("calls API with custom pagination", async () => {
      mockedApiClient.get.mockResolvedValue({
        data: [],
        status: 200,
        statusText: "OK",
        headers: {},
        config: {} as any,
      });

      await accountsService.listAccounts(10, 20);

      expect(mockedApiClient.get).toHaveBeenCalledWith("/accounts", {
        params: { skip: 10, limit: 20 },
      });
    });
  });

  describe("getAccount", () => {
    it("calls API with account ID", async () => {
      const mockAccount: Account = {
        id: 1,
        name: "Test Account",
        institution: "Test Bank",
        currency: "USD",
        account_type: "checking",
        economic_area: "us",
        datelock_from: null,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: null,
      };

      mockedApiClient.get.mockResolvedValue({
        data: mockAccount,
        status: 200,
        statusText: "OK",
        headers: {},
        config: {} as any,
      });

      const result = await accountsService.getAccount(1);

      expect(mockedApiClient.get).toHaveBeenCalledWith("/accounts/1");
      expect(result).toEqual(mockAccount);
    });
  });

  describe("createAccount", () => {
    it("calls API with account data", async () => {
      const createRequest: AccountCreateRequest = {
        name: "New Account",
        institution: "New Bank",
        currency: "USD",
        account_type: "checking",
      };

      const mockAccount: Account = {
        id: 1,
        ...createRequest,
        economic_area: null,
        datelock_from: null,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: null,
      };

      mockedApiClient.post.mockResolvedValue({
        data: mockAccount,
        status: 201,
        statusText: "Created",
        headers: {},
        config: {} as any,
      });

      const result = await accountsService.createAccount(createRequest);

      expect(mockedApiClient.post).toHaveBeenCalledWith(
        "/accounts",
        createRequest,
      );
      expect(result).toEqual(mockAccount);
    });
  });

  describe("updateAccount", () => {
    it("calls API with account ID and update data", async () => {
      const updateRequest: AccountUpdateRequest = {
        name: "Updated Account",
      };

      const mockAccount: Account = {
        id: 1,
        name: "Updated Account",
        institution: "Test Bank",
        currency: "USD",
        account_type: "checking",
        economic_area: "us",
        datelock_from: null,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-02T00:00:00Z",
      };

      mockedApiClient.put.mockResolvedValue({
        data: mockAccount,
        status: 200,
        statusText: "OK",
        headers: {},
        config: {} as any,
      });

      const result = await accountsService.updateAccount(1, updateRequest);

      expect(mockedApiClient.put).toHaveBeenCalledWith(
        "/accounts/1",
        updateRequest,
      );
      expect(result).toEqual(mockAccount);
    });
  });

  describe("deleteAccount", () => {
    it("calls API with account ID", async () => {
      mockedApiClient.delete.mockResolvedValue({
        data: undefined,
        status: 204,
        statusText: "No Content",
        headers: {},
        config: {} as any,
      });

      await accountsService.deleteAccount(1);

      expect(mockedApiClient.delete).toHaveBeenCalledWith("/accounts/1");
    });
  });

  describe("getAccountMetaOptions", () => {
    it("calls API and returns meta options", async () => {
      const mockMeta: MetaOptionsResponse = {
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
          { code: "EUR", name: "Euro", digits: 2 },
        ],
      };

      mockedApiClient.get.mockResolvedValue({
        data: mockMeta,
        status: 200,
        statusText: "OK",
        headers: {},
        config: {} as any,
      });

      const result = await accountsService.getAccountMetaOptions();

      expect(mockedApiClient.get).toHaveBeenCalledWith(
        "/meta/accounts/options",
      );
      expect(result).toEqual(mockMeta);
    });
  });
});
