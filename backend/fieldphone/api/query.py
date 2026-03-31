"""Module 2: Phonetic Query Engine API routes."""

import regex

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fieldphone.config import settings
from fieldphone.database import get_db
from fieldphone.models.token import Token
from fieldphone.models.transcription import Transcription
from fieldphone.models.speaker import Speaker
from fieldphone.models.session import RecordingSession
from fieldphone.schemas.query import (
    ComparativeQueryResponse,
    PhoneticQuery,
    QueryResponse,
    QueryResultToken,
)
from fieldphone.services.query_parser import parse_natural_language, validate_regex
from fieldphone.services.phonetic_classes import load_class_definitions

router = APIRouter()


def _get_class_defs() -> dict:
    """Load phonetic class definitions, falling back to empty dict."""
    config_path = settings.configs_dir / "phonetic_classes.yaml"
    if not config_path.exists():
        config_path = settings.configs_dir / "phonetic_classes.example.yaml"
    if config_path.exists():
        return load_class_definitions(str(config_path))
    return {}


def _execute_search(pattern: str, db: Session, context_before: str | None, context_after: str | None, exclude_context: bool) -> list[QueryResultToken]:
    """Run a regex search against all transcriptions in the database."""
    try:
        compiled = regex.compile(pattern, regex.UNICODE)
    except regex.error as e:
        raise HTTPException(status_code=400, detail=f"Invalid pattern: {e}")

    # Build full pattern with context
    if context_before or context_after:
        full_pattern = ""
        if context_before:
            full_pattern += context_before
        full_pattern += pattern
        if context_after:
            full_pattern += context_after
        try:
            compiled = regex.compile(full_pattern, regex.UNICODE)
        except regex.error:
            pass  # Fall back to original pattern

    # Query all tokens with transcriptions
    rows = (
        db.query(Token, Transcription, Speaker, RecordingSession)
        .join(Transcription, Token.id == Transcription.token_id)
        .join(Speaker, Token.speaker_id == Speaker.id)
        .join(RecordingSession, Token.session_id == RecordingSession.id)
        .all()
    )

    results = []
    seen = set()
    for token, trans, speaker, session in rows:
        if token.id in seen:
            continue
        if compiled.search(trans.ipa_form):
            seen.add(token.id)
            results.append(QueryResultToken(
                token_id=token.id,
                speaker_name=speaker.name,
                session_date=session.date,
                orthographic_form=token.orthographic_form or "",
                ipa_form=trans.ipa_form,
                audio_url=f"/audio/{token.audio_path}" if token.audio_path else "",
                classifier_confidence=trans.classifier_confidence,
            ))

    return results


@router.post("/search", response_model=QueryResponse)
async def search(query: PhoneticQuery, db: Session = Depends(get_db)) -> QueryResponse:
    """Execute a phonetic query."""
    if query.mode == "natural_language":
        class_defs = _get_class_defs()
        pattern = parse_natural_language(query.query_text, class_defs)
    else:
        try:
            pattern = validate_regex(query.query_text)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    tokens = _execute_search(pattern, db, query.context_before, query.context_after, query.exclude_context)

    return QueryResponse(
        tokens=tokens,
        total_count=len(tokens),
        query_resolved_to=pattern,
    )


@router.post("/search/comparative", response_model=ComparativeQueryResponse)
async def search_comparative(query: PhoneticQuery, db: Session = Depends(get_db)) -> ComparativeQueryResponse:
    """Execute a comparative query, splitting results into two groups based on context."""
    if query.mode == "natural_language":
        class_defs = _get_class_defs()
        pattern = parse_natural_language(query.query_text, class_defs)
    else:
        try:
            pattern = validate_regex(query.query_text)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # Group A: matches with context
    group_a = _execute_search(pattern, db, query.context_before, query.context_after, False)
    # Group B: matches without context (or with excluded context)
    group_b = _execute_search(pattern, db, None, None, False)

    # Remove group A tokens from group B
    a_ids = {t.token_id for t in group_a}
    group_b = [t for t in group_b if t.token_id not in a_ids]

    criterion = "with context" if (query.context_before or query.context_after) else "all tokens"
    return ComparativeQueryResponse(
        group_a=group_a,
        group_b=group_b,
        grouping_criterion=criterion,
    )
