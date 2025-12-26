import { apiClient } from "./api";

export interface SystemInfo {
  app_version: string;
  environment: string;
  database_connected: boolean;
}

/**
 * System information service
 */
export const systemService = {
  /**
   * Get system information
   */
  async getSystemInfo(): Promise<SystemInfo> {
    const response = await apiClient.get<SystemInfo>("/system/info");
    return response.data;
  },
};
