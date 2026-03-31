"""Module 4: Transcription Interface schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TranscriptionCreate(BaseModel):
    """Request to create a new transcription record."""

    token_id: int
    ipa_form: str
    tone_pattern: str | None = None
    transcriber: str
    notes: str | None = None


class TranscriptionResponse(BaseModel):
    """Response schema for a transcription record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    token_id: int
    ipa_form: str
    tone_pattern: str | None = None
    transcriber: str
    classifier_top_candidate: str | None = None
    classifier_confidence: float | None = None
    notes: str | None = None
    created_at: datetime


class ShorthandExpansionRequest(BaseModel):
    """Request to expand shorthand notation in transcription input."""

    input_text: str
    language: str


class ShorthandExpansionMapping(BaseModel):
    """A single shorthand expansion (keys: 'from', 'to')."""

    model_config = ConfigDict(populate_by_name=True)

    from_: str = Field(alias="from")
    to: str


class ShorthandExpansionResponse(BaseModel):
    """Response with expanded text and applied expansions."""

    expanded_text: str
    expansions_applied: list[ShorthandExpansionMapping]
