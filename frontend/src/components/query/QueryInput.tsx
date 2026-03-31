import { useState, type FormEvent } from "react";
import type { QueryMode } from "@/types";

interface QueryInputProps {
  onSearch?: (queryText: string, mode: QueryMode) => void;
  onComparativeSearch?: (queryText: string, mode: QueryMode, contextBefore?: string, contextAfter?: string) => void;
  loading?: boolean;
}

export function QueryInput({ onSearch, onComparativeSearch, loading }: QueryInputProps) {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<QueryMode>("natural_language");
  const [comparative, setComparative] = useState(false);
  const [contextBefore, setContextBefore] = useState("");
  const [contextAfter, setContextAfter] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    if (comparative && onComparativeSearch) {
      onComparativeSearch(query, mode, contextBefore || undefined, contextAfter || undefined);
    } else if (onSearch) {
      onSearch(query, mode);
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2>Query</h2>
        <div className="toggle-group">
          <button
            className={`toggle-btn ${mode === "natural_language" ? "active" : ""}`}
            onClick={() => setMode("natural_language")}
          >
            Natural Language
          </button>
          <button
            className={`toggle-btn ${mode === "regex" ? "active" : ""}`}
            onClick={() => setMode("regex")}
          >
            Regex
          </button>
        </div>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">
              {mode === "natural_language" ? "Phonetic Description" : "Regex Pattern"}
            </label>
            <input
              type="text"
              className="form-input form-input-ipa"
              placeholder={mode === "natural_language" ? "e.g. mid vowel followed by a nasal" : "e.g. [eɛ][mnŋ]"}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          <div className="flex items-center gap-2 mb-4">
            <label className="text-sm">
              <input
                type="checkbox"
                checked={comparative}
                onChange={(e) => setComparative(e.target.checked)}
                style={{ marginRight: 6 }}
              />
              Comparative search (A/B split by context)
            </label>
          </div>

          {comparative && (
            <div className="flex gap-4" style={{ marginBottom: 14 }}>
              <div className="form-group" style={{ flex: 1 }}>
                <label className="form-label">Context Before</label>
                <input
                  type="text"
                  className="form-input form-input-ipa"
                  placeholder="e.g. high vowel"
                  value={contextBefore}
                  onChange={(e) => setContextBefore(e.target.value)}
                />
              </div>
              <div className="form-group" style={{ flex: 1 }}>
                <label className="form-label">Context After</label>
                <input
                  type="text"
                  className="form-input form-input-ipa"
                  placeholder="e.g. nasal"
                  value={contextAfter}
                  onChange={(e) => setContextAfter(e.target.value)}
                />
              </div>
            </div>
          )}

          <button type="submit" className="btn btn-primary" disabled={loading || !query.trim()}>
            {loading ? "Searching..." : "Search"}
          </button>
        </form>
      </div>
    </div>
  );
}
