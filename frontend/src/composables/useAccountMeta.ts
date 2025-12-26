import { ref, type Ref } from "vue";
import { accountsService } from "../services/accounts";
import type { MetaOptionsResponse } from "../types/accounts";

// Module-level cache
let cachedMeta: MetaOptionsResponse | null = null;
let isLoadingMeta: Ref<boolean> = ref(false);
let errorMeta: Ref<string | null> = ref(null);

/**
 * Composable for fetching and caching account meta options
 *
 * Meta options are cached in-memory after first fetch.
 * This ensures dropdowns are populated without repeated API calls.
 */
export function useAccountMeta() {
  /**
   * Fetch meta options (cached after first call)
   */
  const fetchMeta = async (): Promise<MetaOptionsResponse> => {
    // Return cached data if available
    if (cachedMeta) {
      return cachedMeta;
    }

    // If already loading, wait for it
    if (isLoadingMeta.value) {
      // Wait for loading to complete
      return new Promise((resolve, reject) => {
        const checkInterval = setInterval(() => {
          if (!isLoadingMeta.value) {
            clearInterval(checkInterval);
            if (cachedMeta) {
              resolve(cachedMeta);
            } else if (errorMeta.value) {
              reject(new Error(errorMeta.value));
            }
          }
        }, 50);
      });
    }

    // Fetch from API
    isLoadingMeta.value = true;
    errorMeta.value = null;

    try {
      const data = await accountsService.getAccountMetaOptions();
      cachedMeta = data;
      return data;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to fetch meta options";
      errorMeta.value = errorMessage;
      throw err;
    } finally {
      isLoadingMeta.value = false;
    }
  };

  /**
   * Clear the cache (useful for testing or forced refresh)
   */
  const clearCache = () => {
    cachedMeta = null;
    errorMeta.value = null;
  };

  return {
    fetchMeta,
    clearCache,
    isLoading: isLoadingMeta,
    error: errorMeta,
    cached: () => cachedMeta,
  };
}
