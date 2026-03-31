"""Module 5: Consistency & Quality Audit schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditFlagSchema(BaseModel):
    """Schema for an audit flag raised by consistency/quality checks."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    token_id: int
    related_token_id: int | None = None
    flag_type: str
    severity: str
    description: str
    resolved: bool
    resolution_notes: str | None = None
    created_at: datetime


class AuditReport(BaseModel):
    """Summary audit report with flags."""

    flags: list[AuditFlagSchema]
    total_count: int
    unresolved_count: int


class AuditFlagResolve(BaseModel):
    """Request to resolve an audit flag."""

    resolution_notes: str


class SpeakerComparisonRequest(BaseModel):
    """Request to compare two speakers' productions."""

    speaker_a_id: int
    speaker_b_id: int
    orthographic_form: str | None = None


class SpeakerComparisonResult(BaseModel):
    """Result of comparing two speakers for a given form."""

    orthographic_form: str
    speaker_a_tokens: list[int]
    speaker_b_tokens: list[int]
    acoustic_divergence: float
