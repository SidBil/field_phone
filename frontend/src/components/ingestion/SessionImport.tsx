import { useState, useRef, useEffect, type FormEvent, type ChangeEvent } from "react";
import { importSession, listSpeakers, createSpeaker } from "@/api/client";
import type { Speaker } from "@/types";

export function SessionImport() {
  const [file, setFile] = useState<File | null>(null);
  const [speakerId, setSpeakerId] = useState("");
  const [date, setDate] = useState("");
  const [scriptId, setScriptId] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    session_id: number;
    token_count: number;
    off_script_count: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const [speakers, setSpeakers] = useState<Speaker[]>([]);
  const [showNewSpeaker, setShowNewSpeaker] = useState(false);
  const [newName, setNewName] = useState("");
  const [newLang, setNewLang] = useState("");
  const [creatingSpeaker, setCreatingSpeaker] = useState(false);

  useEffect(() => {
    listSpeakers().then(setSpeakers).catch(() => {});
  }, []);

  async function handleAddSpeaker() {
    if (!newName.trim() || !newLang.trim()) return;
    setCreatingSpeaker(true);
    try {
      const speaker = await createSpeaker({ name: newName, language: newLang });
      setSpeakers((prev) => [...prev, speaker]);
      setSpeakerId(String(speaker.id));
      setShowNewSpeaker(false);
      setNewName("");
      setNewLang("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create speaker");
    } finally {
      setCreatingSpeaker(false);
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!file || !speakerId || !date) return;

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("audio", file);
    formData.append("speaker_id", speakerId);
    formData.append("date", date);
    if (scriptId) formData.append("script_id", scriptId);
    if (notes) formData.append("notes", notes);

    try {
      const res = await importSession(formData);
      setResult(
        res as {
          session_id: number;
          token_count: number;
          off_script_count: number;
        },
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed");
    } finally {
      setLoading(false);
    }
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (f) setFile(f);
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2>Import Session</h2>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Audio File</label>
            <div
              className="file-upload"
              onClick={() => fileRef.current?.click()}
            >
              <input
                ref={fileRef}
                type="file"
                accept="audio/*"
                onChange={handleFileChange}
                style={{ display: "none" }}
              />
              <p className="file-upload-label">
                {file ? (
                  <>
                    {file.name} ({(file.size / 1024 / 1024).toFixed(1)} MB)
                  </>
                ) : (
                  <>
                    Click to select or <strong>drag & drop</strong> an audio
                    file
                  </>
                )}
              </p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="form-group" style={{ flex: 2 }}>
              <label className="form-label">Speaker</label>
              {!showNewSpeaker ? (
                <div className="flex gap-2">
                  <select
                    className="form-select"
                    value={speakerId}
                    onChange={(e) => setSpeakerId(e.target.value)}
                    required
                  >
                    <option value="">Select a speaker...</option>
                    {speakers.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name} ({s.language})
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    className="btn btn-sm"
                    onClick={() => setShowNewSpeaker(true)}
                  >
                    + New
                  </button>
                </div>
              ) : (
                <div
                  style={{
                    padding: 12,
                    border: "1px solid var(--color-border)",
                    borderRadius: "var(--radius)",
                    background: "var(--color-bg)",
                  }}
                >
                  <div className="flex gap-2" style={{ marginBottom: 8 }}>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="Name"
                      value={newName}
                      onChange={(e) => setNewName(e.target.value)}
                      style={{ flex: 1 }}
                    />
                    <input
                      type="text"
                      className="form-input"
                      placeholder="Language"
                      value={newLang}
                      onChange={(e) => setNewLang(e.target.value)}
                      style={{ flex: 1 }}
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      className="btn btn-primary btn-sm"
                      onClick={handleAddSpeaker}
                      disabled={creatingSpeaker || !newName.trim() || !newLang.trim()}
                    >
                      {creatingSpeaker ? "Creating..." : "Create Speaker"}
                    </button>
                    <button
                      type="button"
                      className="btn btn-sm"
                      onClick={() => setShowNewSpeaker(false)}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Date</label>
              <input
                type="date"
                className="form-input"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                required
              />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Script ID (optional)</label>
              <input
                type="number"
                className="form-input"
                value={scriptId}
                onChange={(e) => setScriptId(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Notes (optional)</label>
            <textarea
              className="form-textarea"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !file || !speakerId || !date}
          >
            {loading ? "Importing..." : "Import Session"}
          </button>
        </form>

        {error && (
          <p
            className="text-sm"
            style={{ color: "var(--color-danger)", marginTop: 12 }}
          >
            {error}
          </p>
        )}

        {result && (
          <div
            style={{
              marginTop: 16,
              padding: 12,
              background: "var(--color-accent-light)",
              borderRadius: "var(--radius)",
            }}
          >
            <p className="text-sm">
              <strong>Session #{result.session_id}</strong> imported
              successfully. {result.token_count} tokens extracted,{" "}
              {result.off_script_count ?? 0} flagged as off-script.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
