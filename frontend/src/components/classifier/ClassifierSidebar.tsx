import { useState, useEffect } from "react";
import { classifyToken } from "@/api/client";
import type { ConfidenceTier } from "@/types";
import { ConfidenceDisplay } from "./ConfidenceDisplay";

interface ClassifierSidebarProps {
  tokenId?: number;
  languagePrior?: string;
}

export function ClassifierSidebar({ tokenId, languagePrior }: ClassifierSidebarProps) {
  const [candidates, setCandidates] = useState<Array<{ symbol: string; confidence: number }>>([]);
  const [tier, setTier] = useState<ConfidenceTier | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestedIds, setSuggestedIds] = useState<number[]>([]);

  useEffect(() => {
    if (!tokenId) {
      setCandidates([]);
      setTier(null);
      return;
    }

    setLoading(true);
    setError(null);
    classifyToken(tokenId, languagePrior)
      .then((res) => {
        setCandidates(res.candidates);
        setTier(res.confidence_tier);
        setSuggestedIds(res.suggested_comparisons || []);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Classification failed"))
      .finally(() => setLoading(false));
  }, [tokenId, languagePrior]);

  return (
    <div className="card classifier-sidebar">
      <div className="card-header">
        <h2>Classifier</h2>
        {tier && (
          <span className={`badge ${tier === "high" ? "badge-success" : tier === "low" ? "badge-warning" : "badge-danger"}`}>
            {tier}
          </span>
        )}
      </div>
      <div className="card-body">
        {!tokenId && (
          <p className="text-sm text-muted">Select a token to see classifier results.</p>
        )}
        {loading && <p className="text-sm text-muted">Classifying...</p>}
        {error && <p className="text-sm" style={{ color: "var(--color-danger)" }}>{error}</p>}
        {candidates.length > 0 && (
          <ConfidenceDisplay candidates={candidates.slice(0, 8)} />
        )}
        {suggestedIds.length > 0 && tier === "uncertain" && (
          <div style={{ marginTop: 12 }}>
            <p className="text-xs text-muted">
              Low confidence — {suggestedIds.length} similar tokens available for comparative listening.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
