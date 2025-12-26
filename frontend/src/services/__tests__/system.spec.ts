import { describe, it, expect, beforeEach, vi } from "vitest";
import { systemService } from "../system";
import { apiClient } from "../api";
import type { SystemInfo } from "../system";

// Mock the API client
vi.mock("../api", () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

const mockedApiClient = vi.mocked(apiClient);

describe("System Service", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calls getSystemInfo and returns system info", async () => {
    const mockSystemInfo: SystemInfo = {
      app_version: "0.1.0",
      environment: "development",
      database_connected: true,
    };

    mockedApiClient.get.mockResolvedValue({
      data: mockSystemInfo,
      status: 200,
      statusText: "OK",
      headers: {},
      config: {} as any,
    });

    const result = await systemService.getSystemInfo();

    expect(mockedApiClient.get).toHaveBeenCalledWith("/system/info");
    expect(result).toEqual(mockSystemInfo);
    expect(result.app_version).toBe("0.1.0");
    expect(result.environment).toBe("development");
    expect(result.database_connected).toBe(true);
  });

  it("handles API errors", async () => {
    const mockError = new Error("Network error");
    mockedApiClient.get.mockRejectedValue(mockError);

    await expect(systemService.getSystemInfo()).rejects.toThrow(
      "Network error",
    );
    expect(mockedApiClient.get).toHaveBeenCalledWith("/system/info");
  });

  it("handles disconnected database status", async () => {
    const mockSystemInfo: SystemInfo = {
      app_version: "0.1.0",
      environment: "development",
      database_connected: false,
    };

    mockedApiClient.get.mockResolvedValue({
      data: mockSystemInfo,
      status: 200,
      statusText: "OK",
      headers: {},
      config: {} as any,
    });

    const result = await systemService.getSystemInfo();

    expect(result.database_connected).toBe(false);
  });
});
