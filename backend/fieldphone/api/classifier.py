"""Module 3: Acoustic Vowel Classifier API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fieldphone.config import settings
from fieldphone.database import get_db
from fieldphone.models.token import Token
from fieldphone.models.transcription import Transcription
from fieldphone.models.speaker import Speaker
from fieldphone.schemas.classifier import (
    ClassifierRequest,
    ClassifierResponse,
    ConsistencyCheckRequest,
    ConsistencyCheckResult,
    IPACandidate,
)
from fieldphone.services.formant_extraction import extract_formants
from fieldphone.services.speaker_normalization import lobanov_normalize, compute_speaker_stats
from fieldphone.services.vowel_classifier import classify_vowel, get_confidence_tier
from fieldphone.services.divergence import compute_divergence

router = APIRouter()


def _run_classifier(token: Token, speaker: Speaker, language_prior: str | None, db: Session) -> ClassifierResponse:
    """Run the full classification pipeline on a token."""
    audio_path = str(settings.audio_dir / token.audio_path) if token.audio_path else None
    if not audio_path:
        raise HTTPException(status_code=400, detail="Token has no audio")

    formants = extract_formants(
        audio_path,
        max_formant_hz=settings.max_formant_hz,
        num_formants=settings.num_formants,
        window_length_s=settings.formant_window_length_s,
    )

    if formants["f1"] is None or formants["f2"] is None:
        raise HTTPException(status_code=422, detail="Could not extract formants from token")

    f1_mean = speaker.f1_mean or 500.0
    f1_std = speaker.f1_std or 150.0
    f2_mean = speaker.f2_mean or 1500.0
    f2_std = speaker.f2_std or 400.0

    f1_norm, f2_norm = lobanov_normalize(
        formants["f1"], formants["f2"],
        f1_mean, f1_std, f2_mean, f2_std,
    )

    prior = language_prior or speaker.language
    candidates = classify_vowel(f1_norm, f2_norm, language_prior=prior)

    top_conf = candidates[0]["confidence"] if candidates else 0.0
    tier = get_confidence_tier(top_conf, settings.classifier_high_confidence, settings.classifier_low_confidence)

    suggested = None
    if tier == "uncertain":
        # Find acoustically similar tokens for comparative listening
        similar = (
            db.query(Token)
            .filter(Token.speaker_id == speaker.id, Token.id != token.id)
            .limit(15)
            .all()
        )
        suggested = [t.id for t in similar]

    ipa_candidates = [
        IPACandidate(
            symbol=c["symbol"],
            confidence=c["confidence"],
            f1_hz=formants["f1"],
            f2_hz=formants["f2"],
            f1_normalized=f1_norm,
            f2_normalized=f2_norm,
        )
        for c in candidates[:10]
    ]

    return ClassifierResponse(
        token_id=token.id,
        candidates=ipa_candidates,
        confidence_tier=tier,
        suggested_comparisons=suggested,
    )


@router.post("/classify", response_model=ClassifierResponse)
async def classify_token_endpoint(request: ClassifierRequest, db: Session = Depends(get_db)) -> ClassifierResponse:
    """Run the acoustic vowel classifier on a token."""
    token = db.query(Token).filter(Token.id == request.token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    speaker = db.query(Speaker).filter(Speaker.id == token.speaker_id).first()
    if not speaker:
        raise HTTPException(status_code=404, detail="Speaker not found")

    return _run_classifier(token, speaker, request.language_prior, db)


@router.post("/consistency-check", response_model=list[ConsistencyCheckResult])
async def consistency_check(request: ConsistencyCheckRequest, db: Session = Depends(get_db)) -> list[ConsistencyCheckResult]:
    """Run acoustic-transcription consistency check."""
    if request.scope == "token":
        if not request.target_id:
            raise HTTPException(status_code=400, detail="target_id required for token scope")
        token_ids = [request.target_id]
    elif request.scope == "session":
        if not request.target_id:
            raise HTTPException(status_code=400, detail="target_id required for session scope")
        tokens = db.query(Token).filter(Token.session_id == request.target_id).all()
        token_ids = [t.id for t in tokens]
    else:
        tokens = db.query(Token).all()
        token_ids = [t.id for t in tokens]

    results = []
    for tid in token_ids:
        div = compute_divergence(tid, db)
        if div["transcribed_as"]:
            results.append(ConsistencyCheckResult(
                token_id=div["token_id"],
                transcribed_as=div["transcribed_as"],
                classifier_top=div["classifier_top"],
                divergence_score=div["divergence_score"],
            ))

    return results


@router.get("/speakers/{speaker_id}/normalization")
async def get_speaker_normalization(speaker_id: int, db: Session = Depends(get_db)) -> dict:
    """Get or compute speaker normalization statistics."""
    speaker = db.query(Speaker).filter(Speaker.id == speaker_id).first()
    if not speaker:
        raise HTTPException(status_code=404, detail="Speaker not found")

    # If stats exist, return them
    if speaker.f1_mean is not None:
        return {
            "speaker_id": speaker_id,
            "f1_mean": speaker.f1_mean,
            "f1_std": speaker.f1_std,
            "f2_mean": speaker.f2_mean,
            "f2_std": speaker.f2_std,
            "computed": False,
        }

    # Compute from speaker's tokens
    tokens = db.query(Token).filter(Token.speaker_id == speaker_id).all()
    formant_list = []
    for token in tokens:
        if not token.audio_path:
            continue
        try:
            audio_path = str(settings.audio_dir / token.audio_path)
            f = extract_formants(
                audio_path,
                max_formant_hz=settings.max_formant_hz,
                num_formants=settings.num_formants,
                window_length_s=settings.formant_window_length_s,
            )
            if f["f1"] is not None and f["f2"] is not None:
                formant_list.append(f)
        except Exception:
            continue

    if not formant_list:
        raise HTTPException(status_code=422, detail="No formants could be extracted for this speaker")

    stats = compute_speaker_stats(formant_list)
    speaker.f1_mean = stats["f1_mean"]
    speaker.f1_std = stats["f1_std"]
    speaker.f2_mean = stats["f2_mean"]
    speaker.f2_std = stats["f2_std"]
    db.commit()

    return {"speaker_id": speaker_id, **stats, "computed": True}
