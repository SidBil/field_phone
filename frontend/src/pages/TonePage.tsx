import { useState } from "react";
import { PitchTrackView } from "@/components/tone/PitchTrackView";
import { ToneQueryResults } from "@/components/tone/ToneQueryResults";

export function TonePage() {
  const [tokenId, setTokenId] = useState<number | undefined>();

  return (
    <div>
      <div className="page-header">
        <h1>Tone Analysis</h1>
        <p>Extract F0 tracks, check tone-transcription consistency, and search by tonal patterns.</p>
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
      <div className="flex flex-col gap-6">
        <PitchTrackView tokenId={tokenId} />
        <ToneQueryResults />
      </div>
    </div>
  );
}
