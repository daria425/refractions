import { useState, useEffect, useCallback } from "react";
import type { VariantSchema } from "../types";
import apiClient from "../api/apiClient";
// CHANGE: Proper React hook to fetch variants schema from backend
export default function useVariantData(requestId: string) {
  const [fetchedVariants, setFetchedVariants] = useState<VariantSchema | null>(
    null
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchVariants = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get(`/schema/variants/${requestId}`); // will add requestId later
      setFetchedVariants(response.data as VariantSchema);
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        "Error fetching variants";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // initial load
    fetchVariants();
  }, [fetchVariants]);

  return { fetchedVariants, loading, error, refetch: fetchVariants };
}
