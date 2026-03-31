import { useState, useEffect } from "react";
import { getSession } from "@/api/client";
import { useAudioPlayer } from "@/hooks/useAudioPlayer";

interface WaveformEditorProps {
  sessionId?: number;
}

interface TokenInfo {
  id: number;
  audio_url: string | null;
  start_time_s: number;
  end_time_s: number;
  duration_s: number;
  orthographic_form: string | null;
  is_off_script: boolean;
  position_in_script: number | null;
}

export function WaveformEditor({ sessionId }: WaveformEditorProps) {
  const [tokens, setTokens] = useState<TokenInfo[]>([]);
  const [totalDuration, setTotalDuration] = useState(0);
  const [loading, setLoading] = useState(false);
  const { toggle, currentUrl, isPlaying } = useAudioPlayer();

  useEffect(() => {
    if (!sessionId) return;
    setLoading(true);
    getSession(sessionId)
      .then((data: unknown) => {
        const d = data as { tokens?: TokenInfo[] };
        setTokens(d.tokens || []);
        if (d.tokens?.length) {
          const maxEnd = Math.max(...d.tokens.map((t: TokenInfo) => t.end_time_s));
          setTotalDuration(maxEnd);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [sessionId]);

  if (!sessionId) {
    return (
      <div className="card">
        <div className="card-header"><h2>Waveform</h2></div>
        <div className="card-body">
          <div className="empty-state">
            <h3>No session selected</h3>
            <p>Import a session to view its waveform and token boundaries.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2>Waveform — Session #{sessionId}</h2>
        <span className="badge badge-info">{tokens.length} tokens</span>
      </div>
      <div className="card-body">
        {loading ? (
          <p className="text-sm text-muted">Loading...</p>
        ) : (
          <>
            <div className="waveform-container" style={{ display: "flex", alignItems: "stretch", gap: 2, minHeight: 80, padding: 8 }}>
              {tokens.map((token, i) => {
                const widthPct = totalDuration > 0 ? (token.duration_s / totalDuration) * 100 : 100 / tokens.length;
                const isActive = token.audio_url ? currentUrl === token.audio_url && isPlaying : false;
                return (
                  <div
                    key={token.id}
                    style={{
                      width: `${widthPct}%`,
                      background: token.is_off_script ? "rgba(239,68,68,0.3)" : isActive ? "rgba(59,130,246,0.6)" : "rgba(59,130,246,0.25)",
                      borderRadius: 3,
                      cursor: token.audio_url ? "pointer" : "default",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 10,
                      color: "#94a3b8",
                      transition: "background 150ms",
                      minWidth: 4,
                    }}
                    title={`Token ${i}: ${token.start_time_s.toFixed(2)}s – ${token.end_time_s.toFixed(2)}s${token.orthographic_form ? ` (${token.orthographic_form})` : ""}`}
                    onClick={() => token.audio_url && toggle(token.audio_url)}
                  >
                    {widthPct > 3 && (i + 1)}
                  </div>
                );
              })}
            </div>
            <div className="flex justify-between mt-2">
              <span className="text-xs text-muted">0.00s</span>
              <span className="text-xs text-muted">{totalDuration.toFixed(2)}s</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
