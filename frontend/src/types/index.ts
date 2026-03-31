// ── Speakers ──

export interface Speaker {
  id: number;
  name: string;
  language: string;
  dialect?: string;
  notes?: string;
  created_at: string;
  f1_mean?: number;
  f1_std?: number;
  f2_mean?: number;
  f2_std?: number;
}

// ── Scripts ──

export interface Script {
  id: number;
  name: string;
  language: string;
  description?: string;
  word_list: string[];
  created_at: string;
}

// ── Sessions ──

export interface RecordingSession {
  id: number;
  speaker_id: number;
  script_id?: number;
  date: string;
  raw_recording_path: string;
  notes?: string;
  created_at: string;
  speaker?: Speaker;
  tokens?: Token[];
}

// ── Tokens ──

export interface Token {
  id: number;
  session_id: number;
  speaker_id: number;
  audio_path: string;
  orthographic_form?: string;
  normalized_form?: string;
  position_in_script?: number;
  is_off_script: boolean;
  start_time_s: number;
  end_time_s: number;
  duration_s: number;
  created_at: string;
}

// ── Transcriptions (immutable records) ──

export interface Transcription {
  id: number;
  token_id: number;
  ipa_form: string;
  tone_pattern?: string;
  transcriber: string;
  classifier_top_candidate?: string;
  classifier_confidence?: number;
  classifier_all_candidates?: string;
  notes?: string;
  created_at: string;
}

// ── Module 1: Ingestion ──

export interface SegmentBoundary {
  start_s: number;
  end_s: number;
  proposed: boolean;
}

export interface SegmentationResult {
  boundaries: SegmentBoundary[];
  total_duration_s: number;
}

export interface BoundaryAdjustment {
  token_index: number;
  new_start_s: number;
  new_end_s: number;
}

export interface SessionImportResponse {
  session_id: number;
  token_count: number;
  off_script_count: number;
}

// ── Module 2: Phonetic Query ──

export type QueryMode = "natural_language" | "regex";

export interface PhoneticQuery {
  query_text: string;
  mode: QueryMode;
  context_before?: string;
  context_after?: string;
  exclude_context: boolean;
}

export interface QueryResultToken {
  token_id: number;
  speaker_name: string;
  session_date: string;
  orthographic_form: string;
  ipa_form: string;
  audio_url: string;
  classifier_confidence?: number;
  acoustic_similarity?: number;
}

export interface QueryResponse {
  tokens: QueryResultToken[];
  total_count: number;
  query_resolved_to: string;
}

export interface ComparativeQueryResponse {
  group_a: QueryResultToken[];
  group_b: QueryResultToken[];
  grouping_criterion: string;
}

// ── Module 3: Classifier ──

export interface IPACandidate {
  symbol: string;
  confidence: number;
  f1_hz: number;
  f2_hz: number;
  f1_normalized: number;
  f2_normalized: number;
}

export type ConfidenceTier = "high" | "low" | "uncertain";

export interface ClassifierResponse {
  token_id: number;
  candidates: IPACandidate[];
  confidence_tier: ConfidenceTier;
  suggested_comparisons?: number[];
}

// ── Module 4: Transcription ──

export interface TranscriptionCreate {
  token_id: number;
  ipa_form: string;
  tone_pattern?: string;
  transcriber: string;
  notes?: string;
}

export interface ShorthandExpansion {
  from: string;
  to: string;
}

export interface ShorthandExpansionResponse {
  expanded_text: string;
  expansions_applied: ShorthandExpansion[];
}

// ── Module 5: Audit ──

export type FlagType =
  | "consistency"
  | "divergence"
  | "off_script"
  | "tone_mismatch";
export type FlagSeverity = "low" | "medium" | "high";

export interface AuditFlag {
  id: number;
  token_id: number;
  related_token_id?: number;
  flag_type: FlagType;
  severity: FlagSeverity;
  description: string;
  resolved: boolean;
  resolution_notes?: string;
  created_at: string;
}

export interface AuditReport {
  flags: AuditFlag[];
  total_count: number;
  unresolved_count: number;
}

export interface SpeakerComparisonResult {
  orthographic_form: string;
  speaker_a_tokens: number[];
  speaker_b_tokens: number[];
  acoustic_divergence: number;
}

// ── Module 6: Tone ──

export interface F0DataPoint {
  time_s: number;
  f0_hz: number;
  syllable_index: number;
}

export interface F0TrackResponse {
  token_id: number;
  f0_track: F0DataPoint[];
  syllable_boundaries: number[];
  duration_s: number;
}

export interface ToneConsistencyResult {
  token_id: number;
  transcribed_tones: string;
  f0_pattern_summary: string;
  divergence_score: number;
  details: string;
}
