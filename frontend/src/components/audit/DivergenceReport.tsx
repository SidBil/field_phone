import { useState, useEffect } from "react";
import { getAuditFlags, runDivergenceReport, resolveFlag } from "@/api/client";
import type { AuditFlag } from "@/types";

export function DivergenceReport() {
  const [flags, setFlags] = useState<AuditFlag[]>([]);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [resolving, setResolving] = useState<number | null>(null);

  function loadFlags() {
    setLoading(true);
    getAuditFlags("divergence", false)
      .then((report) => setFlags(report.flags))
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  useEffect(() => { loadFlags(); }, []);

  async function handleRun() {
    setRunning(true);
    try {
      await runDivergenceReport();
      loadFlags();
    } finally {
      setRunning(false);
    }
  }

  async function handleResolve(flagId: number) {
    const notes = prompt("Resolution notes:");
    if (notes === null) return;
    setResolving(flagId);
    try {
      await resolveFlag(flagId, notes);
      setFlags((prev) => prev.filter((f) => f.id !== flagId));
    } finally {
      setResolving(null);
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2>Divergence Report ({flags.length})</h2>
        <button className="btn btn-sm" onClick={handleRun} disabled={running}>{running ? "Running..." : "Run Report"}</button>
      </div>
      <div className="card-body" style={{ padding: 0 }}>
        {loading ? <p className="text-sm text-muted" style={{ padding: 16 }}>Loading...</p> : flags.length === 0 ? (
          <div className="empty-state"><h3>No divergences</h3><p>Run a divergence report to compare acoustic evidence against transcriptions.</p></div>
        ) : (
          <div className="table-container">
            <table>
              <thead><tr><th>Severity</th><th>Description</th><th>Token</th><th>Date</th><th>Action</th></tr></thead>
              <tbody>
                {flags.map((f) => (
                  <tr key={f.id}>
                    <td><span className={`badge badge-${f.severity === "high" ? "danger" : f.severity === "medium" ? "warning" : "neutral"}`}>{f.severity}</span></td>
                    <td className="text-sm">{f.description}</td>
                    <td className="cell-mono">#{f.token_id}</td>
                    <td className="text-xs text-muted">{new Date(f.created_at).toLocaleDateString()}</td>
                    <td><button className="btn btn-sm" onClick={() => handleResolve(f.id)} disabled={resolving === f.id}>{resolving === f.id ? "..." : "Resolve"}</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
