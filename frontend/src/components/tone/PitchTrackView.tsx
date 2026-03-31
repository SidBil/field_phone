import { useState, useEffect } from "react";
import { getF0Track } from "@/api/client";
import type { F0DataPoint } from "@/types";

interface PitchTrackViewProps {
  tokenId?: number;
}

export function PitchTrackView({ tokenId }: PitchTrackViewProps) {
  const [f0Track, setF0Track] = useState<F0DataPoint[]>([]);
  const [syllableBounds, setSyllableBounds] = useState<number[]>([]);
  const [duration, setDuration] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!tokenId) { setF0Track([]); return; }
    setLoading(true);
    getF0Track(tokenId)
      .then((res) => {
        setF0Track(res.f0_track);
        setSyllableBounds(res.syllable_boundaries);
        setDuration(res.duration_s);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [tokenId]);

  if (!tokenId) {
    return (
      <div className="card">
        <div className="card-header"><h2>Pitch Track</h2></div>
        <div className="card-body">
          <p className="text-sm text-muted">Select a token to view its F0 contour.</p>
        </div>
      </div>
    );
  }

  const svgW = 600;
  const svgH = 180;
  const pad = { top: 10, right: 10, bottom: 30, left: 50 };
  const plotW = svgW - pad.left - pad.right;
  const plotH = svgH - pad.top - pad.bottom;

  const f0Values = f0Track.map((p) => p.f0_hz);
  const f0Min = f0Values.length ? Math.min(...f0Values) - 10 : 75;
  const f0Max = f0Values.length ? Math.max(...f0Values) + 10 : 300;
  const lastPoint = f0Track.length ? f0Track[f0Track.length - 1] : undefined;
  const tMax = duration || (lastPoint ? lastPoint.time_s : 1);

  function xScale(t: number) { return pad.left + (t / tMax) * plotW; }
  function yScale(f: number) { return pad.top + plotH - ((f - f0Min) / (f0Max - f0Min)) * plotH; }

  const pathD = f0Track.map((p, i) => `${i === 0 ? "M" : "L"} ${xScale(p.time_s).toFixed(1)} ${yScale(p.f0_hz).toFixed(1)}`).join(" ");

  return (
    <div className="card">
      <div className="card-header"><h2>Pitch Track</h2>{loading && <span className="text-xs text-muted">Loading...</span>}</div>
      <div className="card-body">
        <svg viewBox={`0 0 ${svgW} ${svgH}`} style={{ width: "100%", height: "auto" }}>
          {/* Grid lines */}
          {[f0Min, (f0Min + f0Max) / 2, f0Max].map((f) => (
            <g key={f}>
              <line x1={pad.left} y1={yScale(f)} x2={svgW - pad.right} y2={yScale(f)} stroke="#e2e8f0" strokeWidth={0.5} />
              <text x={pad.left - 4} y={yScale(f) + 4} textAnchor="end" fontSize={10} fill="#94a3b8">{f.toFixed(0)}</text>
            </g>
          ))}
          {/* Syllable boundaries */}
          {syllableBounds.map((t, i) => (
            <line key={i} x1={xScale(t)} y1={pad.top} x2={xScale(t)} y2={svgH - pad.bottom} stroke="#cbd5e1" strokeWidth={0.5} strokeDasharray="4,3" />
          ))}
          {/* F0 contour */}
          {pathD && <path d={pathD} fill="none" stroke="#3b82f6" strokeWidth={2} />}
          {/* Dots */}
          {f0Track.map((p, i) => (
            <circle key={i} cx={xScale(p.time_s)} cy={yScale(p.f0_hz)} r={2} fill="#3b82f6" />
          ))}
          {/* Axes */}
          <line x1={pad.left} y1={svgH - pad.bottom} x2={svgW - pad.right} y2={svgH - pad.bottom} stroke="#64748b" strokeWidth={1} />
          <line x1={pad.left} y1={pad.top} x2={pad.left} y2={svgH - pad.bottom} stroke="#64748b" strokeWidth={1} />
          <text x={svgW / 2} y={svgH - 4} textAnchor="middle" fontSize={11} fill="#64748b">Time (s)</text>
          <text x={12} y={svgH / 2} textAnchor="middle" fontSize={11} fill="#64748b" transform={`rotate(-90, 12, ${svgH / 2})`}>F0 (Hz)</text>
        </svg>
      </div>
    </div>
  );
}
