import { useState } from "react";
import { TranscriptionEditor } from "@/components/transcription/TranscriptionEditor";
import { ShorthandInput } from "@/components/transcription/ShorthandInput";
import { SideBySidePlayer } from "@/components/transcription/SideBySidePlayer";
import { ClassifierSidebar } from "@/components/classifier/ClassifierSidebar";

export function TranscribePage() {
  const [tokenId, setTokenId] = useState<number | undefined>();
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div>
      <div className="page-header">
        <h1>Transcribe</h1>
        <p>Transcribe tokens with shorthand expansion, real-time classifier feedback, and comparative listening.</p>
      </div>
      <div className="flex items-center gap-4 mb-4">
        <label className="form-label" style={{ marginBottom: 0 }}>Token ID:</label>
        <input
          type="number"
          className="form-input"
          style={{ width: 120 }}
          placeholder="Token ID"
          value={tokenId ?? ""}
          onChange={(e) => setTokenId(e.target.value ? parseInt(e.target.value) : undefined)}
        />
      </div>
      <div className="page-grid page-grid-sidebar">
        <div className="flex flex-col gap-6">
          <ShorthandInput />
          <TranscriptionEditor
            key={refreshKey}
            tokenId={tokenId}
            onTranscriptionCreated={() => setRefreshKey((k) => k + 1)}
          />
          <SideBySidePlayer audioUrls={[]} />
        </div>
        <ClassifierSidebar tokenId={tokenId} />
      </div>
    </div>
  );
}
