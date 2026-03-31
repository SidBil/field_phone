import { useCallback, useState } from "react";
import { searchTokens, searchComparative } from "@/api/client";
import type {
  PhoneticQuery,
  QueryResponse,
  ComparativeQueryResponse,
} from "@/types";

/**
 * Hook wrapping the phonetic query API with loading/error state.
 */
export function usePhoneticQuery() {
  const [results, setResults] = useState<QueryResponse | null>(null);
  const [comparativeResults, setComparativeResults] =
    useState<ComparativeQueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (query: PhoneticQuery) => {
    setLoading(true);
    setError(null);
    setComparativeResults(null);
    try {
      const data = await searchTokens(query);
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query failed");
      setResults(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const searchCompare = useCallback(async (query: PhoneticQuery) => {
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const data = await searchComparative(query);
      setComparativeResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query failed");
      setComparativeResults(null);
    } finally {
      setLoading(false);
    }
  }, []);

  return { results, comparativeResults, loading, error, search, searchCompare };
}
