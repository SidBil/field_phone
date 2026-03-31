"""Module 4: Transcription Interface API routes."""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fieldphone.config import settings
from fieldphone.database import get_db
from fieldphone.models.token import Token
from fieldphone.models.transcription import Transcription
from fieldphone.schemas.transcription import (
    ShorthandExpansionMapping,
    ShorthandExpansionRequest,
    ShorthandExpansionResponse,
    TranscriptionCreate,
    TranscriptionResponse,
)
from fieldphone.services.shorthand import expand, load_shorthand_map

router = APIRouter()


@router.post("/transcriptions", response_model=TranscriptionResponse)
async def create_transcription(
    request: TranscriptionCreate,
    db: Session = Depends(get_db),
) -> TranscriptionResponse:
    """Create a new immutable transcription record."""
    token = db.query(Token).filter(Token.id == request.token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    transcription = Transcription(
        token_id=request.token_id,
        ipa_form=request.ipa_form,
        tone_pattern=request.tone_pattern,
        transcriber=request.transcriber,
        notes=request.notes,
    )

    # Try to run classifier and attach results
    try:
        from fieldphone.services.formant_extraction import extract_formants
        from fieldphone.services.speaker_normalization import lobanov_normalize
        from fieldphone.services.vowel_classifier import classify_vowel

        speaker = token.speaker
        audio_path = str(settings.audio_dir / token.audio_path) if token.audio_path else None
        if audio_path and speaker:
            formants = extract_formants(audio_path)
            if formants["f1"] is not None and formants["f2"] is not None:
                f1_norm, f2_norm = lobanov_normalize(
                    formants["f1"], formants["f2"],
                    speaker.f1_mean or 500.0, speaker.f1_std or 150.0,
                    speaker.f2_mean or 1500.0, speaker.f2_std or 400.0,
                )
                candidates = classify_vowel(f1_norm, f2_norm, language_prior=speaker.language)
                if candidates:
                    transcription.classifier_top_candidate = candidates[0]["symbol"]
                    transcription.classifier_confidence = candidates[0]["confidence"]
                    transcription.classifier_all_candidates = json.dumps(
                        [{"symbol": c["symbol"], "confidence": c["confidence"]} for c in candidates[:5]]
                    )
    except Exception:
        pass  # Classifier failure should not block transcription creation

    db.add(transcription)
    db.commit()
    db.refresh(transcription)

    return TranscriptionResponse.model_validate(transcription)


@router.get("/tokens/{token_id}/transcriptions", response_model=list[TranscriptionResponse])
async def get_token_transcriptions(
    token_id: int,
    db: Session = Depends(get_db),
) -> list[TranscriptionResponse]:
    """Get the full transcription history for a token (newest first)."""
    token = db.query(Token).filter(Token.id == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    transcriptions = (
        db.query(Transcription)
        .filter(Transcription.token_id == token_id)
        .order_by(Transcription.created_at.desc())
        .all()
    )

    return [TranscriptionResponse.model_validate(t) for t in transcriptions]


@router.post("/shorthand/expand", response_model=ShorthandExpansionResponse)
async def expand_shorthand_endpoint(
    request: ShorthandExpansionRequest,
) -> ShorthandExpansionResponse:
    """Expand shorthand notation to IPA."""
    config_path = settings.configs_dir / "shorthand.yaml"
    if not config_path.exists():
        config_path = settings.configs_dir / "shorthand.example.yaml"

    if config_path.exists():
        shorthand_map = load_shorthand_map(str(config_path))
    else:
        shorthand_map = {}

    expanded, applied = expand(request.input_text, shorthand_map)

    return ShorthandExpansionResponse(
        expanded_text=expanded,
        expansions_applied=[
            ShorthandExpansionMapping(from_=a["from"], to=a["to"])
            for a in applied
        ],
    )
