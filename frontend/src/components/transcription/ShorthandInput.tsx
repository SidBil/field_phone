import { useState, useCallback } from "react";
import { expandShorthand as expandShorthandLocal } from "@/utils/shorthand";

interface ShorthandInputProps {
  onChange?: (expanded: string) => void;
  value?: string;
}

const LEGEND = [
  { from: "U", to: "ʊ" }, { from: "I", to: "ɪ" },
  { from: "E", to: "ɛ" }, { from: "O", to: "ɔ" },
  { from: "@", to: "ə" }, { from: "N", to: "ŋ" },
];

export function ShorthandInput({ onChange, value }: ShorthandInputProps) {
  const [raw, setRaw] = useState(value || "");
  const [preview, setPreview] = useState("");

  const handleChange = useCallback((text: string) => {
    setRaw(text);
    const { expanded } = expandShorthandLocal(text);
    setPreview(expanded);
    onChange?.(expanded);
  }, [onChange]);

  return (
    <div className="card">
      <div className="card-header"><h2>Shorthand Input</h2></div>
      <div className="card-body">
        <div className="form-group">
          <label className="form-label">Type with shortcuts</label>
          <input
            type="text"
            className="form-input form-input-ipa"
            value={raw}
            onChange={(e) => handleChange(e.target.value)}
            placeholder="e.g. kUmI → kʊmɪ"
          />
        </div>
        {preview && preview !== raw && (
          <p className="cell-ipa mt-2" style={{ fontSize: 18, color: "var(--color-accent)" }}>
            → {preview}
          </p>
        )}
        <div className="shorthand-legend mt-2">
          {LEGEND.map((l) => (
            <span key={l.from}>
              <span>{l.from}</span>
              <span className="arrow">→</span>
              <span className="cell-ipa">{l.to}</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
