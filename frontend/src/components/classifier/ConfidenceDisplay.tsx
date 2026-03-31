interface ConfidenceDisplayProps {
  candidates?: Array<{ symbol: string; confidence: number }>;
}

export function ConfidenceDisplay({ candidates }: ConfidenceDisplayProps) {
  if (!candidates?.length) return null;

  const maxConf = candidates[0]?.confidence ?? 1;

  return (
    <div>
      {candidates.map((c, i) => (
        <div key={`${c.symbol}-${i}`} className="classifier-candidate">
          <span className="classifier-symbol">{c.symbol}</span>
          <div className="classifier-candidate-info">
            <div className="confidence-bar">
              <div className="confidence-bar-track">
                <div
                  className={`confidence-bar-fill ${c.confidence >= 0.75 ? "high" : c.confidence >= 0.5 ? "low" : "uncertain"}`}
                  style={{ width: `${(c.confidence / maxConf) * 100}%` }}
                />
              </div>
              <span className="confidence-value">{(c.confidence * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
