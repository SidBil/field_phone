"""Module 5: Consistency & Quality Audit API routes."""

import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session as DBSession

from fieldphone.config import settings
from fieldphone.database import get_db
from fieldphone.models.audit import AuditFlag, FlagType
from fieldphone.models.speaker import Speaker
from fieldphone.models.token import Token
from fieldphone.schemas.audit import (
    AuditFlagResolve,
    AuditFlagSchema,
    AuditReport,
    SpeakerComparisonRequest,
    SpeakerComparisonResult,
)
from fieldphone.services.consistency import check_all
from fieldphone.services.divergence import rank_divergences
from fieldphone.services.formant_extraction import extract_formants

router = APIRouter()


@router.get("/flags", response_model=AuditReport)
async def list_audit_flags(
    flag_type: str | None = Query(None),
    resolved: bool | None = Query(None),
    db: DBSession = Depends(get_db),
) -> AuditReport:
    """List audit flags, filterable by type and resolved status."""
    query = db.query(AuditFlag)

    if flag_type:
        try:
            ft = FlagType(flag_type)
            query = query.filter(AuditFlag.flag_type == ft)
        except ValueError:
            pass

    if resolved is not None:
        query = query.filter(AuditFlag.resolved == resolved)

    flags = query.order_by(AuditFlag.created_at.desc()).all()
    unresolved = sum(1 for f in flags if not f.resolved)

    return AuditReport(
        flags=[AuditFlagSchema.model_validate(f) for f in flags],
        total_count=len(flags),
        unresolved_count=unresolved,
    )


@router.put("/flags/{flag_id}/resolve")
async def resolve_flag(
    flag_id: int,
    body: AuditFlagResolve,
    db: DBSession = Depends(get_db),
) -> dict:
    """Mark an audit flag as resolved."""
    flag = db.query(AuditFlag).filter(AuditFlag.id == flag_id).first()
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")

    flag.resolved = True
    flag.resolution_notes = body.resolution_notes
    db.commit()

    return {"id": flag_id, "resolved": True}


@router.post("/run/consistency")
async def run_consistency_check(db: DBSession = Depends(get_db)) -> dict:
    """Trigger inter-session consistency check across the corpus."""
    conflicts = check_all(db)
    return {"conflicts_found": len(conflicts), "conflicts": conflicts}


@router.post("/run/divergence")
async def run_divergence_report(db: DBSession = Depends(get_db)) -> dict:
    """Trigger acoustic-transcription divergence report."""
    divergences = rank_divergences(db, limit=50)
    return {"divergences_found": len(divergences), "divergences": divergences}


@router.post("/speakers/compare", response_model=list[SpeakerComparisonResult])
async def compare_speakers(
    request: SpeakerComparisonRequest,
    db: DBSession = Depends(get_db),
) -> list[SpeakerComparisonResult]:
    """Compare token productions across two speakers."""
    speaker_a = db.query(Speaker).filter(Speaker.id == request.speaker_a_id).first()
    speaker_b = db.query(Speaker).filter(Speaker.id == request.speaker_b_id).first()
    if not speaker_a or not speaker_b:
        raise HTTPException(status_code=404, detail="Speaker not found")

    query_a = db.query(Token).filter(Token.speaker_id == request.speaker_a_id)
    query_b = db.query(Token).filter(Token.speaker_id == request.speaker_b_id)

    if request.orthographic_form:
        query_a = query_a.filter(Token.normalized_form == request.orthographic_form)
        query_b = query_b.filter(Token.normalized_form == request.orthographic_form)

    tokens_a = query_a.all()
    tokens_b = query_b.all()

    # Group by normalized form
    forms_a: dict[str, list[Token]] = {}
    for t in tokens_a:
        if t.normalized_form:
            forms_a.setdefault(t.normalized_form, []).append(t)

    forms_b: dict[str, list[Token]] = {}
    for t in tokens_b:
        if t.normalized_form:
            forms_b.setdefault(t.normalized_form, []).append(t)

    common_forms = set(forms_a.keys()) & set(forms_b.keys())

    results = []
    for form in sorted(common_forms):
        a_tokens = forms_a[form]
        b_tokens = forms_b[form]

        # Compute acoustic divergence based on formant differences
        a_formants = []
        b_formants = []
        for t in a_tokens:
            if not t.audio_path:
                continue
            try:
                f = extract_formants(str(settings.audio_dir / t.audio_path))
                if f["f1"] and f["f2"]:
                    a_formants.append((f["f1"], f["f2"]))
            except Exception:
                pass
        for t in b_tokens:
            if not t.audio_path:
                continue
            try:
                f = extract_formants(str(settings.audio_dir / t.audio_path))
                if f["f1"] and f["f2"]:
                    b_formants.append((f["f1"], f["f2"]))
            except Exception:
                pass

        divergence = 0.0
        if a_formants and b_formants:
            a_f1 = sum(f[0] for f in a_formants) / len(a_formants)
            a_f2 = sum(f[1] for f in a_formants) / len(a_formants)
            b_f1 = sum(f[0] for f in b_formants) / len(b_formants)
            b_f2 = sum(f[1] for f in b_formants) / len(b_formants)
            divergence = round(math.sqrt((a_f1 - b_f1) ** 2 + (a_f2 - b_f2) ** 2), 2)

        results.append(SpeakerComparisonResult(
            orthographic_form=form,
            speaker_a_tokens=[t.id for t in a_tokens],
            speaker_b_tokens=[t.id for t in b_tokens],
            acoustic_divergence=divergence,
        ))

    return results
