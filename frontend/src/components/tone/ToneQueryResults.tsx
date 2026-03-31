import { useState, type FormEvent } from "react";
import { searchTonePatterns } from "@/api/client";
import { useAudioPlayer } from "@/hooks/useAudioPlayer";

interface ToneQueryResultsProps {
  pattern?: string;
}

export function ToneQueryResults({ pattern: initialPattern }: ToneQueryResultsProps) {
  const [pattern, setPattern] = useState(initialPattern || "");
  const [results, setResults] = useState<Array<{ token_id: number; orthographic_form: string; tone_pattern: string; audio_url: string }>>([]);
  const [loading, setLoading] = useState(false);
  const { toggle, currentUrl, isPlaying } = useAudioPlayer();

  async function handleSearch(e: FormEvent) {
    e.preventDefault();
    if (!pattern.trim()) return;
    setLoading(true);
    try {
      const res = await searchTonePatterns(pattern) as { tokens?: Array<{ token_id: number; orthographic_form: string; tone_pattern: string; audio_url: string }> };
      setResults(res.tokens || []);
    } catch { setResults([]); }
    finally { setLoading(false); }
  }

  return (
    <div className="card">
      <div className="card-header"><h2>Tone Query</h2></div>
      <div className="card-body">
        <form onSubmit={handleSearch} className="flex gap-2 items-center mb-4">
          <input type="text" className="form-input" style={{ flex: 1 }} placeholder='e.g. "L before H" or "HLH"' value={pattern} onChange={(e) => setPattern(e.target.value)} />
          <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? "..." : "Search"}</button>
        </form>
        {results.length === 0 ? (
          <p className="text-sm text-muted">No results. Enter a tone pattern to search.</p>
        ) : (
          <div className="table-container">
            <table>
              <thead><tr><th>Play</th><th>Form</th><th>Tone</th></tr></thead>
              <tbody>
                {results.map((r) => (
                  <tr key={r.token_id}>
                    <td><button className={`play-btn ${currentUrl === r.audio_url && isPlaying ? "playing" : ""}`} onClick={() => toggle(r.audio_url)}>{currentUrl === r.audio_url && isPlaying ? "■" : "▶"}</button></td>
                    <td className="cell-ipa">{r.orthographic_form}</td>
                    <td className="cell-mono">{r.tone_pattern}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
