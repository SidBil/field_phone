import { useState } from "react";
import { QueryInput } from "@/components/query/QueryInput";
import { ResultsTable } from "@/components/query/ResultsTable";
import { ComparativePlayer } from "@/components/query/ComparativePlayer";
import { searchTokens, searchComparative } from "@/api/client";
import type { QueryMode, QueryResponse, ComparativeQueryResponse } from "@/types";

export function QueryPage() {
  const [results, setResults] = useState<QueryResponse | null>(null);
  const [comparative, setComparative] = useState<ComparativeQueryResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSearch(queryText: string, mode: QueryMode) {
    setLoading(true);
    setComparative(null);
    try {
      const res = await searchTokens({ query_text: queryText, mode, exclude_context: false });
      setResults(res);
    } catch {
      setResults(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleComparativeSearch(queryText: string, mode: QueryMode, contextBefore?: string, contextAfter?: string) {
    setLoading(true);
    setResults(null);
    try {
      const res = await searchComparative({
        query_text: queryText,
        mode,
        context_before: contextBefore,
        context_after: contextAfter,
        exclude_context: false,
      });
      setComparative(res);
    } catch {
      setComparative(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Phonetic Query</h1>
        <p>Search the database by phonetic description and listen across matching tokens.</p>
      </div>
      <div className="flex flex-col gap-6">
        <QueryInput onSearch={handleSearch} onComparativeSearch={handleComparativeSearch} loading={loading} />
        {results && (
          <ResultsTable tokens={results.tokens} resolvedQuery={results.query_resolved_to} totalCount={results.total_count} />
        )}
        {comparative && (
          <ComparativePlayer groupA={comparative.group_a} groupB={comparative.group_b} criterion={comparative.grouping_criterion} />
        )}
      </div>
    </div>
  );
}
