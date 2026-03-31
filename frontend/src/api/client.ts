const BASE_URL = "/api";

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`API ${response.status}: ${detail}`);
  }

  return response.json() as Promise<T>;
}

function uploadFile<T>(
  path: string,
  formData: FormData,
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  return fetch(url, { method: "POST", body: formData }).then(async (res) => {
    if (!res.ok) {
      const detail = await res.text().catch(() => res.statusText);
      throw new Error(`API ${res.status}: ${detail}`);
    }
    return res.json() as Promise<T>;
  });
}

// ── Speakers ──

import type { Speaker } from "@/types";

export function listSpeakers() {
  return request<Speaker[]>("/speakers/");
}

export function createSpeaker(data: { name: string; language: string; dialect?: string; notes?: string }) {
  return request<Speaker>("/speakers/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ── Module 1: Ingestion ──

export function importSession(formData: FormData) {
  return uploadFile<{ session_id: number; token_count: number }>(
    "/ingestion/sessions/import",
    formData,
  );
}

export function segmentSession(sessionId: number) {
  return request<{ boundaries: Array<{ start_s: number; end_s: number }> }>(
    `/ingestion/sessions/${sessionId}/segment`,
    { method: "POST" },
  );
}

export function adjustBoundaries(
  sessionId: number,
  adjustments: Array<{ token_index: number; new_start_s: number; new_end_s: number }>,
) {
  return request(`/ingestion/sessions/${sessionId}/boundaries`, {
    method: "PUT",
    body: JSON.stringify(adjustments),
  });
}

export function listSessions() {
  return request<Array<{ id: number; date: string; speaker_id: number }>>("/ingestion/sessions");
}

export function getSession(sessionId: number) {
  return request(`/ingestion/sessions/${sessionId}`);
}

// ── Module 2: Query ──

import type {
  PhoneticQuery,
  QueryResponse,
  ComparativeQueryResponse,
} from "@/types";

export function searchTokens(query: PhoneticQuery) {
  return request<QueryResponse>("/query/search", {
    method: "POST",
    body: JSON.stringify(query),
  });
}

export function searchComparative(query: PhoneticQuery) {
  return request<ComparativeQueryResponse>("/query/search/comparative", {
    method: "POST",
    body: JSON.stringify(query),
  });
}

// ── Module 3: Classifier ──

import type { ClassifierResponse } from "@/types";

export function classifyToken(tokenId: number, languagePrior?: string) {
  return request<ClassifierResponse>("/classifier/classify", {
    method: "POST",
    body: JSON.stringify({ token_id: tokenId, language_prior: languagePrior }),
  });
}

export function getSpeakerNormalization(speakerId: number) {
  return request(`/classifier/speakers/${speakerId}/normalization`);
}

// ── Module 4: Transcription ──

import type {
  TranscriptionCreate,
  Transcription,
  ShorthandExpansionResponse,
} from "@/types";

export function createTranscription(data: TranscriptionCreate) {
  return request<Transcription>("/transcription/transcriptions", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getTokenTranscriptions(tokenId: number) {
  return request<Transcription[]>(`/transcription/tokens/${tokenId}/transcriptions`);
}

export function expandShorthand(inputText: string, language: string) {
  return request<ShorthandExpansionResponse>("/transcription/shorthand/expand", {
    method: "POST",
    body: JSON.stringify({ input_text: inputText, language }),
  });
}

// ── Module 5: Audit ──

import type { AuditReport, AuditFlag as AuditFlagType } from "@/types";

export function getAuditFlags(flagType?: string, resolved?: boolean) {
  const params = new URLSearchParams();
  if (flagType) params.set("flag_type", flagType);
  if (resolved !== undefined) params.set("resolved", String(resolved));
  const qs = params.toString();
  return request<AuditReport>(`/audit/flags${qs ? `?${qs}` : ""}`);
}

export function resolveFlag(flagId: number, resolutionNotes: string) {
  return request<AuditFlagType>(`/audit/flags/${flagId}/resolve`, {
    method: "PUT",
    body: JSON.stringify({ resolution_notes: resolutionNotes }),
  });
}

export function runConsistencyCheck() {
  return request("/audit/run/consistency", { method: "POST" });
}

export function runDivergenceReport() {
  return request("/audit/run/divergence", { method: "POST" });
}

export function compareSpeakers(speakerAId: number, speakerBId: number, form?: string) {
  return request("/audit/speakers/compare", {
    method: "POST",
    body: JSON.stringify({
      speaker_a_id: speakerAId,
      speaker_b_id: speakerBId,
      orthographic_form: form,
    }),
  });
}

// ── Module 6: Tone ──

import type { F0TrackResponse, ToneConsistencyResult } from "@/types";

export function getF0Track(tokenId: number) {
  return request<F0TrackResponse>("/tone/f0-track", {
    method: "POST",
    body: JSON.stringify({ token_id: tokenId }),
  });
}

export function checkToneConsistency(tokenId: number) {
  return request<ToneConsistencyResult>("/tone/consistency-check", {
    method: "POST",
    body: JSON.stringify({ token_id: tokenId }),
  });
}

export function searchTonePatterns(pattern: string) {
  return request("/tone/search", {
    method: "POST",
    body: JSON.stringify({ pattern }),
  });
}
