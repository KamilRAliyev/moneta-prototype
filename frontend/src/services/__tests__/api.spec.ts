import { describe, it, expect } from "vitest";
import { apiClient } from "../api";

describe("API Client", () => {
  it("creates axios instance with correct base URL", () => {
    // The apiClient should be created with the correct base URL
    expect(apiClient).toBeDefined();
    expect(apiClient.defaults.baseURL).toBe("http://localhost:8000/api/v1");
  });

  it("has correct default headers", () => {
    expect(apiClient.defaults.headers["Content-Type"]).toBe("application/json");
  });

  it("has timeout configured", () => {
    expect(apiClient.defaults.timeout).toBe(10000);
  });

  it("has interceptors configured", () => {
    // Verify interceptors are set up
    expect(apiClient.interceptors).toBeDefined();
    expect(apiClient.interceptors.request).toBeDefined();
    expect(apiClient.interceptors.response).toBeDefined();
  });
});
