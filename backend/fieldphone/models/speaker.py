from datetime import datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fieldphone.database import Base


class Speaker(Base):
    __tablename__ = "speakers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(100))
    dialect: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    sessions = relationship("RecordingSession", back_populates="speaker")
    tokens = relationship("Token", back_populates="speaker")

    # Per-speaker formant statistics for Lobanov normalization
    f1_mean: Mapped[float | None] = mapped_column()
    f1_std: Mapped[float | None] = mapped_column()
    f2_mean: Mapped[float | None] = mapped_column()
    f2_std: Mapped[float | None] = mapped_column()
