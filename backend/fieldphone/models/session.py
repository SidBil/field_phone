from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fieldphone.database import Base


class RecordingSession(Base):
    """A single recording session with one speaker, optionally following a script."""

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    speaker_id: Mapped[int] = mapped_column(ForeignKey("speakers.id"))
    script_id: Mapped[int | None] = mapped_column(ForeignKey("scripts.id"))
    date: Mapped[datetime] = mapped_column()
    raw_recording_path: Mapped[str] = mapped_column(String(1024))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    speaker = relationship("Speaker", back_populates="sessions")
    script = relationship("Script", back_populates="sessions")
    tokens = relationship("Token", back_populates="session")
