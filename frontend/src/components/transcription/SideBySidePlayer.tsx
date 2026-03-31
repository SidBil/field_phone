import { useAudioPlayer } from "@/hooks/useAudioPlayer";

interface SideBySidePlayerProps {
  tokenIds?: number[];
  audioUrls?: Array<{ tokenId: number; url: string; label?: string }>;
}

export function SideBySidePlayer({ audioUrls }: SideBySidePlayerProps) {
  const { toggle, currentUrl, isPlaying } = useAudioPlayer();

  if (!audioUrls?.length) {
    return (
      <div className="card">
        <div className="card-header"><h2>Compare</h2></div>
        <div className="card-body">
          <p className="text-sm text-muted">No tokens selected for comparison.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2>Compare ({audioUrls.length} tokens)</h2>
      </div>
      <div className="card-body">
        {audioUrls.map((item) => (
          <div key={item.tokenId} className="flex items-center gap-2" style={{ padding: "6px 0", borderBottom: "1px solid var(--color-border)" }}>
            <button
              className={`play-btn ${currentUrl === item.url && isPlaying ? "playing" : ""}`}
              onClick={() => toggle(item.url)}
            >
              {currentUrl === item.url && isPlaying ? "■" : "▶"}
            </button>
            <span className="cell-ipa" style={{ flex: 1 }}>{item.label || `Token #${item.tokenId}`}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
