import { describe, it, expect, beforeEach, vi } from "vitest";
import { healthService } from "../health";
import { apiClient } from "../api";
import type { HealthInfo } from "../health";

// Mock the API client
vi.mock("../api", () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

const mockedApiClient = vi.mocked(apiClient);

describe("Health Service", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calls getHealth and returns health info", async () => {
    const mockHealthInfo: HealthInfo = {
      ok: true,
      timestamp: "2025-01-01T00:00:00Z",
      version: "0.1.0",
    };

    mockedApiClient.get.mockResolvedValue({
      data: mockHealthInfo,
      status: 200,
      statusText: "OK",
      headers: {},
      config: {} as any,
    });

    const result = await healthService.getHealth();

    expect(mockedApiClient.get).toHaveBeenCalledWith("/health");
    expect(result).toEqual(mockHealthInfo);
    expect(result.ok).toBe(true);
  });

  it("handles API errors", async () => {
    const mockError = new Error("Network error");
    mockedApiClient.get.mockRejectedValue(mockError);

    await expect(healthService.getHealth()).rejects.toThrow("Network error");
    expect(mockedApiClient.get).toHaveBeenCalledWith("/health");
  });

  it("handles unhealthy status", async () => {
    const mockHealthInfo: HealthInfo = {
      ok: false,
    };

    mockedApiClient.get.mockResolvedValue({
      data: mockHealthInfo,
      status: 200,
      statusText: "OK",
      headers: {},
      config: {} as any,
    });

    const result = await healthService.getHealth();

    expect(result.ok).toBe(false);
  });
});
