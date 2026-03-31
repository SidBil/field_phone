"""Module 6: Tone Analysis API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fieldphone.config import settings
from fieldphone.database import get_db
from fieldphone.models.token import Token
from fieldphone.models.transcription import Transcription
from fieldphone.schemas.tone import (
    F0DataPoint,
    F0TrackRequest,
    F0TrackResponse,
    ToneConsistencyResult,
    ToneQueryRequest,
    ToneQueryResponse,
    ToneQueryToken,
)
from fieldphone.services.f0_extraction import align_f0_with_syllables, extract_f0
from fieldphone.services.tone_analysis import check_tone_consistency, query_tone_patterns

router = APIRouter()


@router.post("/f0-track", response_model=F0TrackResponse)
async def extract_f0_track(
    request: F0TrackRequest,
    db: Session = Depends(get_db),
) -> F0TrackResponse:
    """Extract F0 track for a token."""
    token = db.query(Token).filter(Token.id == request.token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    audio_path = str(settings.audio_dir / token.audio_path) if token.audio_path else None
    if not audio_path:
        raise HTTPException(status_code=400, detail="Token has no audio")

    f0_track = extract_f0(audio_path)
    if not f0_track:
        raise HTTPException(status_code=422, detail="Could not extract F0 from token")

    # Use even syllable boundaries based on duration (placeholder until real segmentation)
    duration = token.duration_s
    # Estimate syllable count from transcription length
    latest_trans = (
        db.query(Transcription)
        .filter(Transcription.token_id == token.id)
        .order_by(Transcription.created_at.desc())
        .first()
    )

    n_syllables = 1
    if latest_trans and latest_trans.ipa_form:
        vowels = set("aeiouɪʊɛɔəæɑɒœøɜɞʌɤɯɨʉɵʏ")
        n_syllables = max(1, sum(1 for c in latest_trans.ipa_form if c in vowels))

    syllable_boundaries = [round(i * duration / n_syllables, 4) for i in range(n_syllables + 1)]
    aligned = align_f0_with_syllables(f0_track, syllable_boundaries)

    return F0TrackResponse(
        token_id=token.id,
        f0_track=[F0DataPoint(**pt) for pt in aligned],
        syllable_boundaries=syllable_boundaries,
        duration_s=duration,
    )


@router.post("/consistency-check", response_model=ToneConsistencyResult)
async def tone_consistency_check(
    request: F0TrackRequest,
    db: Session = Depends(get_db),
) -> ToneConsistencyResult:
    """Check consistency between tone transcription and F0."""
    token = db.query(Token).filter(Token.id == request.token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    latest_trans = (
        db.query(Transcription)
        .filter(Transcription.token_id == token.id)
        .order_by(Transcription.created_at.desc())
        .first()
    )

    if not latest_trans or not latest_trans.tone_pattern:
        raise HTTPException(status_code=422, detail="No tone transcription for this token")

    audio_path = str(settings.audio_dir / token.audio_path) if token.audio_path else None
    if not audio_path:
        raise HTTPException(status_code=400, detail="Token has no audio")

    f0_track = extract_f0(audio_path)

    # Align with syllables
    duration = token.duration_s
    tone_pattern = latest_trans.tone_pattern
    n_syllables = max(1, len(tone_pattern.replace(" ", "")))
    syllable_boundaries = [round(i * duration / n_syllables, 4) for i in range(n_syllables + 1)]
    aligned = align_f0_with_syllables(f0_track, syllable_boundaries)

    result = check_tone_consistency(aligned, tone_pattern)

    return ToneConsistencyResult(
        token_id=token.id,
        transcribed_tones=tone_pattern,
        f0_pattern_summary=_summarize_f0(aligned, n_syllables),
        divergence_score=result["divergence_score"],
        details=result["details"],
    )


def _summarize_f0(f0_track: list[dict], n_syllables: int) -> str:
    """Create a brief text summary of the F0 pattern."""
    syllable_means: dict[int, list[float]] = {}
    for pt in f0_track:
        idx = pt.get("syllable_index", 0)
        syllable_means.setdefault(idx, []).append(pt["f0_hz"])

    parts = []
    for i in range(n_syllables):
        vals = syllable_means.get(i, [])
        if vals:
            mean = sum(vals) / len(vals)
            parts.append(f"S{i}={mean:.0f}Hz")
        else:
            parts.append(f"S{i}=?")

    return " ".join(parts)


@router.post("/search", response_model=ToneQueryResponse)
async def search_by_tone(
    request: ToneQueryRequest,
    db: Session = Depends(get_db),
) -> ToneQueryResponse:
    """Search for tokens matching a tone pattern."""
    results = query_tone_patterns(request.pattern, db)

    return ToneQueryResponse(
        tokens=[ToneQueryToken(**r) for r in results],
        total_count=len(results),
    )
