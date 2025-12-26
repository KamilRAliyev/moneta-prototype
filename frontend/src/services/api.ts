import axios, {
  type AxiosInstance,
  type AxiosError,
  type AxiosRequestConfig,
} from "axios";

// API base URL - defaults to localhost:8000 in development
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_VERSION = "/api/v1";

/**
 * Create and configure axios instance
 */
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: `${API_BASE_URL}${API_VERSION}`,
    headers: {
      "Content-Type": "application/json",
    },
    timeout: 10000, // 10 seconds
  });

  // Request interceptor
  client.interceptors.request.use(
    (config) => {
      // Add auth token here if needed in the future
      // const token = getAuthToken();
      // if (token) {
      //   config.headers.Authorization = `Bearer ${token}`;
      // }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    },
  );

  // Response interceptor
  client.interceptors.response.use(
    (response) => {
      return response;
    },
    (error: AxiosError) => {
      // Handle common errors
      if (error.response) {
        // Server responded with error status
        const status = error.response.status;
        const data = error.response.data as {
          error?: string;
          message?: string;
          details?: unknown;
        };

        switch (status) {
          case 401:
            // Unauthorized - handle auth redirect if needed
            console.error("Unauthorized access");
            break;
          case 403:
            console.error("Forbidden access");
            break;
          case 404:
            console.error("Resource not found");
            break;
          case 422:
            console.error("Validation error:", data.details);
            break;
          case 500:
            console.error("Server error");
            break;
        }
      } else if (error.request) {
        // Request made but no response received
        console.error("Network error - no response from server");
      } else {
        // Error setting up request
        console.error("Request setup error:", error.message);
      }

      return Promise.reject(error);
    },
  );

  return client;
};

// Export singleton instance
export const apiClient = createApiClient();

// Export types for convenience
export type { AxiosError, AxiosRequestConfig };
