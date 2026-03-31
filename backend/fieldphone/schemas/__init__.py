"""FieldPhone API schemas — request/response models for all modules."""

from __future__ import annotations

from fieldphone.schemas.audit import (
    AuditFlagResolve,
    AuditFlagSchema,
    AuditReport,
    SpeakerComparisonRequest,
    SpeakerComparisonResult,
)
from fieldphone.schemas.classifier import (
    ClassifierRequest,
    ClassifierResponse,
    ConsistencyCheckRequest,
    ConsistencyCheckResult,
    IPACandidate,
)
from fieldphone.schemas.ingestion import (
    BoundaryAdjustment,
    SegmentBoundary,
    SegmentationResult,
    SessionImportRequest,
    SessionImportResponse,
)
from fieldphone.schemas.query import (
    ComparativeQueryResponse,
    PhoneticQuery,
    QueryResponse,
    QueryResultToken,
)
from fieldphone.schemas.tone import (
    F0DataPoint,
    F0TrackRequest,
    F0TrackResponse,
    ToneConsistencyResult,
    ToneQueryRequest,
    ToneQueryResponse,
    ToneQueryToken,
)
from fieldphone.schemas.transcription import (
    ShorthandExpansionMapping,
    ShorthandExpansionRequest,
    ShorthandExpansionResponse,
    TranscriptionCreate,
    TranscriptionResponse,
)

__all__ = [
    # Ingestion
    "SessionImportRequest",
    "SessionImportResponse",
    "SegmentBoundary",
    "SegmentationResult",
    "BoundaryAdjustment",
    # Query
    "PhoneticQuery",
    "QueryResultToken",
    "QueryResponse",
    "ComparativeQueryResponse",
    # Classifier
    "ClassifierRequest",
    "ClassifierResponse",
    "IPACandidate",
    "ConsistencyCheckRequest",
    "ConsistencyCheckResult",
    # Transcription
    "TranscriptionCreate",
    "TranscriptionResponse",
    "ShorthandExpansionRequest",
    "ShorthandExpansionResponse",
    "ShorthandExpansionMapping",
    # Audit
    "AuditFlagSchema",
    "AuditReport",
    "AuditFlagResolve",
    "SpeakerComparisonRequest",
    "SpeakerComparisonResult",
    # Tone
    "F0TrackRequest",
    "F0TrackResponse",
    "F0DataPoint",
    "ToneConsistencyResult",
    "ToneQueryRequest",
    "ToneQueryResponse",
    "ToneQueryToken",
]
