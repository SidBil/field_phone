"""Speaker management API routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from fieldphone.database import get_db
from fieldphone.models.speaker import Speaker

router = APIRouter()


class SpeakerCreate(BaseModel):
    name: str
    language: str
    dialect: str | None = None
    notes: str | None = None


class SpeakerResponse(BaseModel):
    id: int
    name: str
    language: str
    dialect: str | None
    notes: str | None

    class Config:
        from_attributes = True


@router.get("/", response_model=list[SpeakerResponse])
async def list_speakers(db: Session = Depends(get_db)) -> list[SpeakerResponse]:
    """List all speakers."""
    speakers = db.query(Speaker).order_by(Speaker.name).all()
    return [SpeakerResponse.model_validate(s) for s in speakers]


@router.post("/", response_model=SpeakerResponse)
async def create_speaker(
    body: SpeakerCreate,
    db: Session = Depends(get_db),
) -> SpeakerResponse:
    """Create a new speaker."""
    speaker = Speaker(
        name=body.name,
        language=body.language,
        dialect=body.dialect,
        notes=body.notes,
    )
    db.add(speaker)
    db.commit()
    db.refresh(speaker)
    return SpeakerResponse.model_validate(speaker)


@router.get("/{speaker_id}", response_model=SpeakerResponse)
async def get_speaker(speaker_id: int, db: Session = Depends(get_db)) -> SpeakerResponse:
    """Get a speaker by ID."""
    speaker = db.query(Speaker).filter(Speaker.id == speaker_id).first()
    if not speaker:
        raise HTTPException(status_code=404, detail="Speaker not found")
    return SpeakerResponse.model_validate(speaker)
