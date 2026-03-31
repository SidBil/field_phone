import { useState } from "react";
import { SessionImport } from "@/components/ingestion/SessionImport";
import { WaveformEditor } from "@/components/ingestion/WaveformEditor";
import { BoundaryAdjuster } from "@/components/ingestion/BoundaryAdjuster";

export function IngestPage() {
  const [activeSessionId, setActiveSessionId] = useState<number | undefined>();

  return (
    <div>
      <div className="page-header">
        <h1>Import & Segment</h1>
        <p>Import whole-session recordings, segment by silence detection, and adjust token boundaries.</p>
      </div>
      <div className="flex flex-col gap-6">
        <SessionImport />
        <div className="flex items-center gap-4">
          <label className="form-label" style={{ marginBottom: 0 }}>View Session:</label>
          <input
            type="number"
            className="form-input"
            style={{ width: 120 }}
            placeholder="Session ID"
            value={activeSessionId ?? ""}
            onChange={(e) => setActiveSessionId(e.target.value ? parseInt(e.target.value) : undefined)}
          />
        </div>
        <WaveformEditor sessionId={activeSessionId} />
        <BoundaryAdjuster sessionId={activeSessionId} />
      </div>
    </div>
  );
}
