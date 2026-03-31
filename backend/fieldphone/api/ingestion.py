"""Module 1: Data Ingestion API routes."""

from datetime import datetime
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

import librosa

from fieldphone.config import settings
from fieldphone.database import get_db
from fieldphone.models.session import RecordingSession
from fieldphone.models.token import Token
from fieldphone.models.speaker import Speaker
from fieldphone.schemas.ingestion import (
    BoundaryAdjustment,
    SegmentationResult,
    SegmentBoundary,
    SessionImportResponse,
)
from fieldphone.services.segmentation import detect_silence_boundaries, extract_token
from fieldphone.services.deviation_detector import classify_segment

router = APIRouter()


@router.post("/sessions/import", response_model=SessionImportResponse)
async def import_session(
    audio: UploadFile = File(...),
    speaker_id: int = Form(...),
    date: str = Form(...),
    script_id: int | None = Form(None),
    notes: str | None = Form(None),
    db: Session = Depends(get_db),
) -> SessionImportResponse:
    """Import a new recording session."""
    speaker = db.query(Speaker).filter(Speaker.id == speaker_id).first()
    if not speaker:
        raise HTTPException(status_code=404, detail=f"Speaker {speaker_id} not found")

    # Save uploaded audio
    session_date = datetime.fromisoformat(date)
    filename = f"{speaker_id}_{session_date.strftime('%Y%m%d')}_{audio.filename}"
    audio_dest = settings.sessions_dir / filename
    settings.sessions_dir.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(audio_dest, "wb") as f:
        content = await audio.read()
        await f.write(content)

    # Create session record
    rec_session = RecordingSession(
        speaker_id=speaker_id,
        script_id=script_id,
        date=session_date,
        raw_recording_path=str(audio_dest),
        notes=notes,
    )
    db.add(rec_session)
    db.flush()

    # Auto-segment
    boundaries = detect_silence_boundaries(
        str(audio_dest),
        threshold_db=settings.silence_threshold_db,
        min_silence_ms=settings.min_silence_duration_ms,
        min_token_ms=settings.min_token_duration_ms,
    )

    # Extract tokens
    off_script_count = 0
    token_dir = settings.audio_dir / str(rec_session.id)
    token_dir.mkdir(parents=True, exist_ok=True)

    for i, (start_s, end_s) in enumerate(boundaries):
        token_filename = f"token_{i:04d}.wav"
        token_path = token_dir / token_filename
        extract_token(str(audio_dest), start_s, end_s, str(token_path))

        # Check for script deviation
        label, confidence = classify_segment(str(audio_dest), start_s, end_s)
        is_off = label == "free_speech" and confidence > 0.6

        token = Token(
            session_id=rec_session.id,
            speaker_id=speaker_id,
            audio_path=str(token_path.relative_to(settings.audio_dir)),
            position_in_script=i,
            is_off_script=is_off,
            start_time_s=start_s,
            end_time_s=end_s,
            duration_s=round(end_s - start_s, 4),
        )
        db.add(token)
        if is_off:
            off_script_count += 1

    db.commit()

    return SessionImportResponse(
        session_id=rec_session.id,
        token_count=len(boundaries),
        off_script_count=off_script_count,
    )


@router.post("/sessions/{session_id}/segment", response_model=SegmentationResult)
async def segment_session(session_id: int, db: Session = Depends(get_db)) -> SegmentationResult:
    """Run segmentation on a session's recording."""
    rec_session = db.query(RecordingSession).filter(RecordingSession.id == session_id).first()
    if not rec_session:
        raise HTTPException(status_code=404, detail="Session not found")

    boundaries = detect_silence_boundaries(
        rec_session.raw_recording_path,
        threshold_db=settings.silence_threshold_db,
        min_silence_ms=settings.min_silence_duration_ms,
        min_token_ms=settings.min_token_duration_ms,
    )

    y, sr = librosa.load(rec_session.raw_recording_path, sr=None)
    total_duration = len(y) / sr

    return SegmentationResult(
        boundaries=[SegmentBoundary(start_s=s, end_s=e) for s, e in boundaries],
        total_duration_s=round(total_duration, 4),
    )


@router.put("/sessions/{session_id}/boundaries")
async def adjust_boundaries(
    session_id: int,
    adjustments: list[BoundaryAdjustment],
    db: Session = Depends(get_db),
) -> dict:
    """Apply user-reviewed boundary adjustments."""
    rec_session = db.query(RecordingSession).filter(RecordingSession.id == session_id).first()
    if not rec_session:
        raise HTTPException(status_code=404, detail="Session not found")

    tokens = (
        db.query(Token)
        .filter(Token.session_id == session_id)
        .order_by(Token.position_in_script)
        .all()
    )

    token_dir = settings.audio_dir / str(session_id)
    token_dir.mkdir(parents=True, exist_ok=True)

    for adj in adjustments:
        if adj.token_index < 0 or adj.token_index >= len(tokens):
            continue
        token = tokens[adj.token_index]

        # Re-extract with new boundaries
        token_filename = f"token_{adj.token_index:04d}.wav"
        token_path = token_dir / token_filename
        extract_token(
            rec_session.raw_recording_path,
            adj.new_start_s, adj.new_end_s,
            str(token_path),
        )

        token.start_time_s = adj.new_start_s
        token.end_time_s = adj.new_end_s
        token.duration_s = round(adj.new_end_s - adj.new_start_s, 4)
        token.audio_path = str(token_path.relative_to(settings.audio_dir))

    db.commit()
    return {"adjusted": len(adjustments)}


@router.get("/sessions")
async def list_sessions(db: Session = Depends(get_db)) -> list[dict]:
    """List all recording sessions."""
    sessions = db.query(RecordingSession).order_by(RecordingSession.date.desc()).all()
    return [
        {
            "id": s.id,
            "speaker_id": s.speaker_id,
            "speaker_name": s.speaker.name if s.speaker else None,
            "script_id": s.script_id,
            "date": s.date.isoformat(),
            "notes": s.notes,
            "token_count": len(s.tokens),
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}")
async def get_session(session_id: int, db: Session = Depends(get_db)) -> dict:
    """Get full session details including all tokens."""
    rec_session = db.query(RecordingSession).filter(RecordingSession.id == session_id).first()
    if not rec_session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "id": rec_session.id,
        "speaker_id": rec_session.speaker_id,
        "speaker_name": rec_session.speaker.name if rec_session.speaker else None,
        "script_id": rec_session.script_id,
        "date": rec_session.date.isoformat(),
        "notes": rec_session.notes,
        "created_at": rec_session.created_at.isoformat(),
        "tokens": [
            {
                "id": t.id,
                "audio_url": f"/audio/{t.audio_path}" if t.audio_path else None,
                "orthographic_form": t.orthographic_form,
                "normalized_form": t.normalized_form,
                "position_in_script": t.position_in_script,
                "is_off_script": t.is_off_script,
                "start_time_s": t.start_time_s,
                "end_time_s": t.end_time_s,
                "duration_s": t.duration_s,
                "transcription_count": len(t.transcriptions),
            }
            for t in sorted(rec_session.tokens, key=lambda x: x.position_in_script or 0)
        ],
    }
