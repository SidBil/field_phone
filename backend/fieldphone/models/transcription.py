from datetime import datetime

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fieldphone.database import Base


class Transcription(Base):
    """
    An immutable transcription record. Transcriptions are never edited —
    a new disagreeing judgment creates a new record, preserving the full
    history of auditory judgments for each token.
    """

    __tablename__ = "transcriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    token_id: Mapped[int] = mapped_column(ForeignKey("tokens.id"))
    ipa_form: Mapped[str] = mapped_column(String(512))
    tone_pattern: Mapped[str | None] = mapped_column(String(255))
    transcriber: Mapped[str] = mapped_column(String(255))

    classifier_top_candidate: Mapped[str | None] = mapped_column(String(64))
    classifier_confidence: Mapped[float | None] = mapped_column(Float)
    classifier_all_candidates: Mapped[str | None] = mapped_column(Text)

    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    token = relationship("Token", back_populates="transcriptions")
