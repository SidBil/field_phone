import { useState, useEffect } from "react";
import { getSession, adjustBoundaries } from "@/api/client";
import { useAudioPlayer } from "@/hooks/useAudioPlayer";

interface BoundaryAdjusterProps {
  sessionId?: number;
}

interface TokenRow {
  id: number;
  index: number;
  audio_url: string | null;
  start_s: number;
  end_s: number;
  duration_s: number;
  orthographic_form: string | null;
  is_off_script: boolean;
  newStart: string;
  newEnd: string;
  modified: boolean;
}

export function BoundaryAdjuster({ sessionId }: BoundaryAdjusterProps) {
  const [rows, setRows] = useState<TokenRow[]>([]);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const { toggle, currentUrl, isPlaying } = useAudioPlayer();

  useEffect(() => {
    if (!sessionId) return;
    getSession(sessionId).then((data: unknown) => {
      const d = data as { tokens?: Array<{
        id: number;
        audio_url: string | null;
        start_time_s: number;
        end_time_s: number;
        duration_s: number;
        orthographic_form: string | null;
        is_off_script: boolean;
      }> };
      setRows(
        (d.tokens || []).map((t, i) => ({
          id: t.id,
          index: i,
          audio_url: t.audio_url,
          start_s: t.start_time_s,
          end_s: t.end_time_s,
          duration_s: t.duration_s,
          orthographic_form: t.orthographic_form,
          is_off_script: t.is_off_script,
          newStart: t.start_time_s.toFixed(3),
          newEnd: t.end_time_s.toFixed(3),
          modified: false,
        }))
      );
    });
  }, [sessionId]);

  function updateRow(index: number, field: "newStart" | "newEnd", value: string) {
    setRows((prev) =>
      prev.map((r) =>
        r.index === index
          ? {
              ...r,
              [field]: value,
              modified: field === "newStart" ? value !== r.start_s.toFixed(3) || r.newEnd !== r.end_s.toFixed(3) : r.newStart !== r.start_s.toFixed(3) || value !== r.end_s.toFixed(3),
            }
          : r
      )
    );
  }

  async function handleSave() {
    if (!sessionId) return;
    const modified = rows.filter((r) => r.modified);
    if (modified.length === 0) return;

    setSaving(true);
    setMessage(null);
    try {
      await adjustBoundaries(
        sessionId,
        modified.map((r) => ({
          token_index: r.index,
          new_start_s: parseFloat(r.newStart),
          new_end_s: parseFloat(r.newEnd),
        }))
      );
      setMessage(`${modified.length} boundaries adjusted.`);
      setRows((prev) =>
        prev.map((r) =>
          r.modified
            ? { ...r, start_s: parseFloat(r.newStart), end_s: parseFloat(r.newEnd), duration_s: parseFloat(r.newEnd) - parseFloat(r.newStart), modified: false }
            : r
        )
      );
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  if (!sessionId) return null;

  const modifiedCount = rows.filter((r) => r.modified).length;

  return (
    <div className="card">
      <div className="card-header">
        <h2>Boundary Adjustment</h2>
        {modifiedCount > 0 && (
          <button className="btn btn-primary btn-sm" onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : `Save ${modifiedCount} change${modifiedCount > 1 ? "s" : ""}`}
          </button>
        )}
      </div>
      <div className="card-body">
        {message && <p className="text-sm mb-4" style={{ color: "var(--color-accent)" }}>{message}</p>}
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Play</th>
                <th>Start (s)</th>
                <th>End (s)</th>
                <th>Duration</th>
                <th>Form</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} style={row.modified ? { background: "var(--color-accent-light)" } : undefined}>
                  <td className="text-muted">{row.index + 1}</td>
                  <td>
                    {row.audio_url && (
                      <button
                        className={`play-btn ${currentUrl === row.audio_url && isPlaying ? "playing" : ""}`}
                        onClick={() => toggle(row.audio_url!)}
                      >
                        {currentUrl === row.audio_url && isPlaying ? "■" : "▶"}
                      </button>
                    )}
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.001"
                      className="form-input"
                      style={{ width: 90, padding: "4px 6px", fontSize: 12 }}
                      value={row.newStart}
                      onChange={(e) => updateRow(row.index, "newStart", e.target.value)}
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.001"
                      className="form-input"
                      style={{ width: 90, padding: "4px 6px", fontSize: 12 }}
                      value={row.newEnd}
                      onChange={(e) => updateRow(row.index, "newEnd", e.target.value)}
                    />
                  </td>
                  <td className="font-mono text-sm">{row.duration_s.toFixed(3)}s</td>
                  <td className="cell-ipa">{row.orthographic_form || "—"}</td>
                  <td>
                    {row.is_off_script ? (
                      <span className="badge badge-warning">Off-script</span>
                    ) : (
                      <span className="badge badge-neutral">OK</span>
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
