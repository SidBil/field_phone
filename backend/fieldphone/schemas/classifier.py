"""Module 3: Acoustic Vowel Classifier schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ClassifierRequest(BaseModel):
    """Request to run the acoustic vowel classifier on a token."""

    token_id: int
    language_prior: str | None = None


class IPACandidate(BaseModel):
    """A single IPA vowel candidate from the classifier."""

    symbol: str
    confidence: float
    f1_hz: float
    f2_hz: float
    f1_normalized: float
    f2_normalized: float


class ClassifierResponse(BaseModel):
    """Response from the acoustic vowel classifier."""

    token_id: int
    candidates: list[IPACandidate]
    confidence_tier: Literal["high", "low", "uncertain"]
    suggested_comparisons: list[int] | None = None


class ConsistencyCheckRequest(BaseModel):
    """Request to run consistency check between classifier and transcriptions."""

    scope: Literal["token", "session", "all"]
    target_id: int | None = None


class ConsistencyCheckResult(BaseModel):
    """Result for a single token in consistency check."""

    token_id: int
    transcribed_as: str
    classifier_top: str
    divergence_score: float
