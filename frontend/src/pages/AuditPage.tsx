import { ConsistencyReport } from "@/components/audit/ConsistencyReport";
import { DivergenceReport } from "@/components/audit/DivergenceReport";

export function AuditPage() {
  return (
    <div>
      <div className="page-header">
        <h1>Audit</h1>
        <p>Review consistency flags, acoustic-transcription divergences, and speaker comparisons.</p>
      </div>
      <div className="flex flex-col gap-6">
        <ConsistencyReport />
        <DivergenceReport />
      </div>
    </div>
  );
}
