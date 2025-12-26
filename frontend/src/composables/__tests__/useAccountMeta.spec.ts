import { describe, it, expect, beforeEach, vi } from "vitest";
import { accountsService } from "../../services/accounts";
import type { MetaOptionsResponse } from "../../types/accounts";

// Mock the accounts service
vi.mock("../../services/accounts", () => ({
  accountsService: {
    getAccountMetaOptions: vi.fn(),
  },
}));

const mockedAccountsService = vi.mocked(accountsService);

describe("useAccountMeta", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("fetches meta options on first call", async () => {
    // Import dynamically to get fresh instance
    const { useAccountMeta } = await import("../useAccountMeta");

    const mockMeta: MetaOptionsResponse = {
      account_types: [{ value: "checking", label: "Checking" }],
      economic_areas: [{ value: "us", label: "United States" }],
      currencies: [{ code: "USD", name: "US Dollar", digits: 2 }],
    };

    mockedAccountsService.getAccountMetaOptions.mockResolvedValue(mockMeta);

    const { fetchMeta } = useAccountMeta();
    const result = await fetchMeta();

    expect(mockedAccountsService.getAccountMetaOptions).toHaveBeenCalledTimes(
      1,
    );
    expect(result).toEqual(mockMeta);
  });

  it("caches meta options after first fetch", async () => {
    // Reset modules to clear cache
    vi.resetModules();
    const { useAccountMeta } = await import("../useAccountMeta");

    const mockMeta: MetaOptionsResponse = {
      account_types: [{ value: "checking", label: "Checking" }],
      economic_areas: [{ value: "us", label: "United States" }],
      currencies: [{ code: "USD", name: "US Dollar", digits: 2 }],
    };

    mockedAccountsService.getAccountMetaOptions.mockResolvedValue(mockMeta);

    const { fetchMeta } = useAccountMeta();

    // First call
    const result1 = await fetchMeta();
    // Second call should use cache
    const result2 = await fetchMeta();

    // Should only call API once
    expect(mockedAccountsService.getAccountMetaOptions).toHaveBeenCalledTimes(
      1,
    );
    expect(result1).toEqual(mockMeta);
    expect(result2).toEqual(mockMeta);
  });

  it("handles errors during fetch", async () => {
    // Import dynamically to get fresh instance
    vi.resetModules();
    const { useAccountMeta } = await import("../useAccountMeta");

    const error = new Error("Network error");
    mockedAccountsService.getAccountMetaOptions.mockRejectedValue(error);

    const { fetchMeta, error: errorRef } = useAccountMeta();

    try {
      await fetchMeta();
      expect.fail("Should have thrown an error");
    } catch (err) {
      expect(err).toBe(error);
      expect(errorRef.value).toBe("Network error");
    }
  });

  it("clears cache when clearCache is called", async () => {
    // Import dynamically to get fresh instance
    vi.resetModules();
    const { useAccountMeta } = await import("../useAccountMeta");

    const mockMeta: MetaOptionsResponse = {
      account_types: [{ value: "checking", label: "Checking" }],
      economic_areas: [{ value: "us", label: "United States" }],
      currencies: [{ code: "USD", name: "US Dollar", digits: 2 }],
    };

    mockedAccountsService.getAccountMetaOptions.mockResolvedValue(mockMeta);

    const { fetchMeta, clearCache } = useAccountMeta();

    // First call
    await fetchMeta();
    // Clear cache
    clearCache();
    // Second call should fetch again
    await fetchMeta();

    // Should call API twice after cache clear
    expect(mockedAccountsService.getAccountMetaOptions).toHaveBeenCalledTimes(
      2,
    );
  });
});
