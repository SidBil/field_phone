import { useState } from "react";
import type { QueryResultToken } from "@/types";
import { useAudioPlayer } from "@/hooks/useAudioPlayer";

interface ResultsTableProps {
  tokens?: QueryResultToken[];
  resolvedQuery?: string;
  totalCount?: number;
}

type SortKey = "speaker_name" | "session_date" | "orthographic_form" | "ipa_form" | "classifier_confidence";

export function ResultsTable({ tokens, resolvedQuery, totalCount }: ResultsTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("session_date");
  const [sortAsc, setSortAsc] = useState(false);
  const { toggle, currentUrl, isPlaying } = useAudioPlayer();

  if (!tokens || tokens.length === 0) {
    return (
      <div className="card">
        <div className="card-header"><h2>Results</h2></div>
        <div className="card-body">
          <div className="empty-state">
            <h3>No results</h3>
            <p>Run a query to see matching tokens here.</p>
          </div>
        </div>
      </div>
    );
  }

  function handleSort(key: SortKey) {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(true);
    }
  }

  const sorted = [...tokens].sort((a, b) => {
    const aVal = a[sortKey] ?? "";
    const bVal = b[sortKey] ?? "";
    const cmp = typeof aVal === "number" && typeof bVal === "number"
      ? aVal - bVal
      : String(aVal).localeCompare(String(bVal));
    return sortAsc ? cmp : -cmp;
  });

  return (
    <div className="card">
      <div className="card-header">
        <h2>Results ({totalCount ?? tokens.length})</h2>
        {resolvedQuery && <span className="text-xs text-muted font-mono">Pattern: {resolvedQuery}</span>}
      </div>
      <div className="card-body" style={{ padding: 0 }}>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th style={{ width: 44 }}>Play</th>
                <th onClick={() => handleSort("speaker_name")}>Speaker</th>
                <th onClick={() => handleSort("session_date")}>Date</th>
                <th onClick={() => handleSort("orthographic_form")}>Orthographic</th>
                <th onClick={() => handleSort("ipa_form")}>IPA</th>
                <th onClick={() => handleSort("classifier_confidence")}>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((token) => (
                <tr key={token.token_id}>
                  <td>
                    <button
                      className={`play-btn ${currentUrl === token.audio_url && isPlaying ? "playing" : ""}`}
                      onClick={() => toggle(token.audio_url)}
                    >
                      {currentUrl === token.audio_url && isPlaying ? "■" : "▶"}
                    </button>
                  </td>
                  <td>{token.speaker_name}</td>
                  <td className="text-sm">{new Date(token.session_date).toLocaleDateString()}</td>
                  <td className="cell-ipa">{token.orthographic_form}</td>
                  <td className="cell-ipa" style={{ fontWeight: 500 }}>{token.ipa_form}</td>
                  <td>
                    {token.classifier_confidence != null ? (
                      <div className="confidence-bar">
                        <div className="confidence-bar-track">
                          <div
                            className={`confidence-bar-fill ${token.classifier_confidence >= 0.75 ? "high" : token.classifier_confidence >= 0.5 ? "low" : "uncertain"}`}
                            style={{ width: `${token.classifier_confidence * 100}%` }}
                          />
                        </div>
                        <span className="confidence-value">{(token.classifier_confidence * 100).toFixed(0)}%</span>
                      </div>
                    ) : (
                      <span className="text-muted">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
