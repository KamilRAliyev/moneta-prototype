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
    // Mock backend response format
    const mockBackendResponse = {
      status: "ok",
      server_time: "2025-01-01 00:00:00",
      app_version: "0.1.0",
    };

    mockedApiClient.get.mockResolvedValue({
      data: mockBackendResponse,
      status: 200,
      statusText: "OK",
      headers: {},
      config: {} as any,
    });

    const result = await healthService.getHealth();

    expect(mockedApiClient.get).toHaveBeenCalledWith("/health");
    expect(result.ok).toBe(true);
    expect(result.timestamp).toBe("2025-01-01 00:00:00");
    expect(result.version).toBe("0.1.0");
  });

  it("handles API errors", async () => {
    const mockError = new Error("Network error");
    mockedApiClient.get.mockRejectedValue(mockError);

    await expect(healthService.getHealth()).rejects.toThrow("Network error");
    expect(mockedApiClient.get).toHaveBeenCalledWith("/health");
  });

  it("handles unhealthy status", async () => {
    // Mock backend response with non-ok status
    const mockBackendResponse = {
      status: "error",
      server_time: "2025-01-01 00:00:00",
      app_version: "0.1.0",
    };

    mockedApiClient.get.mockResolvedValue({
      data: mockBackendResponse,
      status: 200,
      statusText: "OK",
      headers: {},
      config: {} as any,
    });

    const result = await healthService.getHealth();

    expect(result.ok).toBe(false);
  });
});
