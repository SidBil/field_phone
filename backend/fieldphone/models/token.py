from datetime import datetime

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fieldphone.database import Base


class Token(Base):
    """A single segmented audio token (word/phrase) extracted from a session recording."""

    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    speaker_id: Mapped[int] = mapped_column(ForeignKey("speakers.id"))
    audio_path: Mapped[str] = mapped_column(String(1024))
    orthographic_form: Mapped[str | None] = mapped_column(String(512))
    normalized_form: Mapped[str | None] = mapped_column(String(512))
    position_in_script: Mapped[int | None] = mapped_column(Integer)
    is_off_script: Mapped[bool] = mapped_column(Boolean, default=False)

    start_time_s: Mapped[float] = mapped_column(Float)
    end_time_s: Mapped[float] = mapped_column(Float)
    duration_s: Mapped[float] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    session = relationship("RecordingSession", back_populates="tokens")
    speaker = relationship("Speaker", back_populates="tokens")
    transcriptions = relationship(
        "Transcription", back_populates="token", order_by="Transcription.created_at"
    )
    audit_flags = relationship(
        "AuditFlag", back_populates="token", foreign_keys="[AuditFlag.token_id]"
    )
