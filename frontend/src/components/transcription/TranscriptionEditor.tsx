import { useState, useEffect, type FormEvent } from "react";
import { createTranscription, getTokenTranscriptions } from "@/api/client";
import type { Transcription } from "@/types";

interface TranscriptionEditorProps {
  tokenId?: number;
  onTranscriptionCreated?: () => void;
}

export function TranscriptionEditor({ tokenId, onTranscriptionCreated }: TranscriptionEditorProps) {
  const [ipaForm, setIpaForm] = useState("");
  const [tonePattern, setTonePattern] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [history, setHistory] = useState<Transcription[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!tokenId) { setHistory([]); return; }
    getTokenTranscriptions(tokenId).then(setHistory).catch(() => {});
  }, [tokenId]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!tokenId || !ipaForm.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await createTranscription({
        token_id: tokenId,
        ipa_form: ipaForm,
        tone_pattern: tonePattern || undefined,
        transcriber: "default",
        notes: notes || undefined,
      });
      setIpaForm("");
      setTonePattern("");
      setNotes("");
      const updated = await getTokenTranscriptions(tokenId);
      setHistory(updated);
      onTranscriptionCreated?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="card">
      <div className="card-header"><h2>Transcription</h2></div>
      <div className="card-body">
        {!tokenId ? (
          <p className="text-sm text-muted">Select a token to transcribe.</p>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="flex gap-4">
              <div className="form-group" style={{ flex: 2 }}>
                <label className="form-label">IPA Form</label>
                <input type="text" className="form-input form-input-ipa" value={ipaForm} onChange={(e) => setIpaForm(e.target.value)} placeholder="Enter IPA transcription" required />
              </div>
              <div className="form-group" style={{ flex: 1 }}>
                <label className="form-label">Tone Pattern</label>
                <input type="text" className="form-input" value={tonePattern} onChange={(e) => setTonePattern(e.target.value)} placeholder="e.g. HLH" />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Notes</label>
              <textarea className="form-textarea" value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} />
            </div>
            {error && <p className="text-sm" style={{ color: "var(--color-danger)" }}>{error}</p>}
            <button type="submit" className="btn btn-primary" disabled={saving || !ipaForm.trim()}>{saving ? "Saving..." : "Save Transcription"}</button>
          </form>
        )}

        {history.length > 0 && (
          <div className="mt-4">
            <h3 className="text-sm" style={{ fontWeight: 600, marginBottom: 8 }}>History ({history.length} records)</h3>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>IPA</th>
                    <th>Tone</th>
                    <th>Classifier</th>
                    <th>Date</th>
                    <th>Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((t) => (
                    <tr key={t.id}>
                      <td className="cell-ipa" style={{ fontWeight: 500 }}>{t.ipa_form}</td>
                      <td className="cell-mono">{t.tone_pattern || "—"}</td>
                      <td>
                        {t.classifier_top_candidate ? (
                          <span className={`flag-indicator ${t.ipa_form === t.classifier_top_candidate ? "match" : "divergence"}`}>
                            {t.classifier_top_candidate} ({((t.classifier_confidence ?? 0) * 100).toFixed(0)}%)
                          </span>
                        ) : "—"}
                      </td>
                      <td className="text-xs text-muted">{new Date(t.created_at).toLocaleString()}</td>
                      <td className="text-xs">{t.notes || ""}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
