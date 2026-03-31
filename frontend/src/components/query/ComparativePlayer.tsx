import type { QueryResultToken } from "@/types";
import { useAudioPlayer } from "@/hooks/useAudioPlayer";

interface ComparativePlayerProps {
  groupA?: QueryResultToken[];
  groupB?: QueryResultToken[];
  criterion?: string;
}

export function ComparativePlayer({ groupA, groupB, criterion }: ComparativePlayerProps) {
  const { toggle, currentUrl, isPlaying } = useAudioPlayer();

  if (!groupA?.length && !groupB?.length) {
    return null;
  }

  function renderGroup(tokens: QueryResultToken[], label: string, className: string) {
    return (
      <div className={`comparative-column ${className}`}>
        <h3>{label} ({tokens.length})</h3>
        {tokens.map((token) => (
          <div key={token.token_id} className="flex items-center gap-2" style={{ padding: "4px 0", borderBottom: "1px solid var(--color-border)" }}>
            <button
              className={`play-btn ${currentUrl === token.audio_url && isPlaying ? "playing" : ""}`}
              onClick={() => toggle(token.audio_url)}
            >
              {currentUrl === token.audio_url && isPlaying ? "■" : "▶"}
            </button>
            <span className="cell-ipa" style={{ flex: 1 }}>{token.ipa_form}</span>
            <span className="text-xs text-muted">{token.speaker_name}</span>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2>Comparative Listening</h2>
        {criterion && <span className="badge badge-info">{criterion}</span>}
      </div>
      <div className="card-body">
        <div className="comparative-layout">
          {renderGroup(groupA || [], "Group A", "group-a")}
          {renderGroup(groupB || [], "Group B", "group-b")}
        </div>
      </div>
    </div>
  );
}
