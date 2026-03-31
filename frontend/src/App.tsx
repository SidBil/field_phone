import { Routes, Route, Navigate } from "react-router-dom";
import { MainLayout } from "./components/layout/MainLayout";
import { IngestPage } from "./pages/IngestPage";
import { QueryPage } from "./pages/QueryPage";
import { TranscribePage } from "./pages/TranscribePage";
import { AuditPage } from "./pages/AuditPage";
import { TonePage } from "./pages/TonePage";

export function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route index element={<Navigate to="/ingest" replace />} />
        <Route path="ingest" element={<IngestPage />} />
        <Route path="query" element={<QueryPage />} />
        <Route path="transcribe" element={<TranscribePage />} />
        <Route path="audit" element={<AuditPage />} />
        <Route path="tone" element={<TonePage />} />
      </Route>
    </Routes>
  );
}
