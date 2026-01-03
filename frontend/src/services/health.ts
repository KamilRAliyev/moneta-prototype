import { apiClient } from "./api";

export interface HealthInfo {
  ok: boolean;
  timestamp?: string;
  version?: string;
  pythonVersion?: string;
  uptimeSeconds?: number;
}

interface BackendHealthResponse {
  status: string;
  server_time?: string;
  app_version?: string;
  python_version?: string;
  uptime_seconds?: number;
  [key: string]: unknown;
}

/**
 * Health check service
 */
export const healthService = {
  /**
   * Get health status
   */
  async getHealth(): Promise<HealthInfo> {
    const response = await apiClient.get<BackendHealthResponse>("/health");
    // Map backend response format to frontend expected format
    return {
      ok: response.data.status === "ok",
      timestamp: response.data.server_time,
      version: response.data.app_version,
      pythonVersion: response.data.python_version,
      uptimeSeconds: response.data.uptime_seconds,
    };
  },
};
