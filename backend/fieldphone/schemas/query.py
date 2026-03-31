"""Module 2: Phonetic Query Engine schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class PhoneticQuery(BaseModel):
    """Request schema for phonetic search."""

    query_text: str
    mode: Literal["natural_language", "regex"]
    context_before: str | None = None
    context_after: str | None = None
    exclude_context: bool = False


class QueryResultToken(BaseModel):
    """A single token matching a phonetic query."""

    token_id: int
    speaker_name: str
    session_date: datetime
    orthographic_form: str
    ipa_form: str
    audio_url: str
    classifier_confidence: float | None = None
    acoustic_similarity: float | None = None


class QueryResponse(BaseModel):
    """Response for a phonetic query."""

    tokens: list[QueryResultToken]
    total_count: int
    query_resolved_to: str


class ComparativeQueryResponse(BaseModel):
    """Response for a comparative phonetic query (e.g., A vs B grouping)."""

    group_a: list[QueryResultToken]
    group_b: list[QueryResultToken]
    grouping_criterion: str
