"""Module 1: Data Ingestion schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SessionImportRequest(BaseModel):
    """Request schema for importing a recording session (audio file comes via UploadFile)."""

    script_id: int | None = None
    speaker_id: int
    date: datetime
    notes: str | None = None


class SegmentBoundary(BaseModel):
    """A single segment boundary in the audio."""

    start_s: float
    end_s: float
    proposed: bool = True


class SegmentationResult(BaseModel):
    """Result of automatic segmentation."""

    boundaries: list[SegmentBoundary]
    total_duration_s: float


class BoundaryAdjustment(BaseModel):
    """Adjustment to a segment boundary."""

    token_index: int
    new_start_s: float
    new_end_s: float


class SessionImportResponse(BaseModel):
    """Response after successfully importing a session."""

    session_id: int
    token_count: int
    off_script_count: int
