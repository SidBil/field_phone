"""Acoustic-transcription divergence for re-elicitation prioritization."""

from sqlalchemy.orm import Session

from fieldphone.models.token import Token
from fieldphone.models.transcription import Transcription
from fieldphone.models.audit import AuditFlag, FlagType, FlagSeverity
from fieldphone.services.formant_extraction import extract_formants
from fieldphone.services.speaker_normalization import lobanov_normalize
from fieldphone.services.vowel_classifier import classify_vowel


def compute_divergence(token_id: int, db_session: Session) -> dict:
    """Compare classifier output against human transcription for a single token.
    
    Runs the full pipeline: formant extraction → normalization → classification,
    then compares the classifier's top candidate against the transcribed form.
    """
    token = db_session.query(Token).filter(Token.id == token_id).first()
    if not token:
        return {"token_id": token_id, "transcribed_as": "", "classifier_top": "", "divergence_score": 0.0}
    
    # Get latest transcription
    latest_trans = (
        db_session.query(Transcription)
        .filter(Transcription.token_id == token_id)
        .order_by(Transcription.created_at.desc())
        .first()
    )
    transcribed_as = latest_trans.ipa_form if latest_trans else ""
    
    # Extract formants
    try:
        formants = extract_formants(token.audio_path)
    except Exception:
        return {
            "token_id": token_id,
            "transcribed_as": transcribed_as,
            "classifier_top": "",
            "divergence_score": 0.0,
        }
    
    if formants["f1"] is None or formants["f2"] is None:
        return {
            "token_id": token_id,
            "transcribed_as": transcribed_as,
            "classifier_top": "",
            "divergence_score": 0.0,
        }
    
    # Normalize using speaker stats
    speaker = token.speaker
    f1_mean = speaker.f1_mean or 500.0
    f1_std = speaker.f1_std or 150.0
    f2_mean = speaker.f2_mean or 1500.0
    f2_std = speaker.f2_std or 400.0
    
    f1_norm, f2_norm = lobanov_normalize(
        formants["f1"], formants["f2"],
        f1_mean, f1_std, f2_mean, f2_std,
    )
    
    # Classify
    candidates = classify_vowel(f1_norm, f2_norm, language_prior=speaker.language)
    classifier_top = candidates[0]["symbol"] if candidates else ""
    classifier_conf = candidates[0]["confidence"] if candidates else 0.0
    
    # Compute divergence: 1.0 if completely different, 0.0 if matching
    # Check if the transcribed vowel appears in the top candidates
    if not transcribed_as or not classifier_top:
        divergence = 0.0
    elif transcribed_as == classifier_top:
        divergence = 0.0
    else:
        # Find where the transcribed vowel ranks in the candidate list
        transcribed_rank = None
        for i, c in enumerate(candidates):
            if c["symbol"] == transcribed_as:
                transcribed_rank = i
                break
        
        if transcribed_rank is not None:
            # Lower divergence if it's in the top candidates
            divergence = min(1.0, transcribed_rank / len(candidates))
        else:
            # Not in candidates at all — high divergence
            divergence = 1.0 - classifier_conf * 0.1
    
    return {
        "token_id": token_id,
        "transcribed_as": transcribed_as,
        "classifier_top": classifier_top,
        "divergence_score": round(divergence, 4),
    }


def rank_divergences(
    db_session: Session,
    limit: int = 50,
) -> list[dict]:
    """Return the top N tokens ranked by divergence score (highest = most urgent).
    
    Also creates AuditFlag records for tokens with high divergence.
    """
    tokens = db_session.query(Token).all()
    
    results = []
    for token in tokens:
        div = compute_divergence(token.id, db_session)
        if div["divergence_score"] > 0.0:
            results.append(div)
    
    results.sort(key=lambda d: d["divergence_score"], reverse=True)
    results = results[:limit]
    
    # Create audit flags for high-divergence tokens
    for div in results:
        if div["divergence_score"] >= 0.5:
            existing = (
                db_session.query(AuditFlag)
                .filter(
                    AuditFlag.token_id == div["token_id"],
                    AuditFlag.flag_type == FlagType.DIVERGENCE,
                    AuditFlag.resolved == False,
                )
                .first()
            )
            if not existing:
                severity = FlagSeverity.HIGH if div["divergence_score"] >= 0.75 else FlagSeverity.MEDIUM
                flag = AuditFlag(
                    token_id=div["token_id"],
                    flag_type=FlagType.DIVERGENCE,
                    severity=severity,
                    description=(
                        f"Transcribed as /{div['transcribed_as']}/ but classifier "
                        f"suggests /{div['classifier_top']}/ "
                        f"(divergence: {div['divergence_score']:.2f})"
                    ),
                    resolved=False,
                )
                db_session.add(flag)
    
    db_session.commit()
    return results
