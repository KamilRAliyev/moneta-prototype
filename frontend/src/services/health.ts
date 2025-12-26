import { apiClient } from "./api";

export interface HealthInfo {
  ok: boolean;
  timestamp?: string;
  version?: string;
}

/**
 * Health check service
 */
export const healthService = {
  /**
   * Get health status
   */
  async getHealth(): Promise<HealthInfo> {
    const response = await apiClient.get<HealthInfo>("/health");
    return response.data;
  },
};
