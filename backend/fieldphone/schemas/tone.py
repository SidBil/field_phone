"""Module 6: Tone Analysis schemas."""

from __future__ import annotations

from pydantic import BaseModel


class F0TrackRequest(BaseModel):
    """Request for F0 track extraction on a token."""

    token_id: int


class F0DataPoint(BaseModel):
    """A single F0 measurement point."""

    time_s: float
    f0_hz: float
    syllable_index: int


class F0TrackResponse(BaseModel):
    """Response with F0 track data for a token."""

    token_id: int
    f0_track: list[F0DataPoint]
    syllable_boundaries: list[float]
    duration_s: float


class ToneConsistencyResult(BaseModel):
    """Result of tone consistency check for a token."""

    token_id: int
    transcribed_tones: str
    f0_pattern_summary: str
    divergence_score: float
    details: str


class ToneQueryToken(BaseModel):
    """Simplified token for tone query results (subset of QueryResultToken)."""

    token_id: int
    orthographic_form: str
    tone_pattern: str
    audio_url: str


class ToneQueryRequest(BaseModel):
    """Request for tone pattern query, e.g. 'L before H'."""

    pattern: str


class ToneQueryResponse(BaseModel):
    """Response for tone pattern query."""

    tokens: list[ToneQueryToken]
    total_count: int
