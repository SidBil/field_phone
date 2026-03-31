from datetime import datetime

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fieldphone.database import Base


class Script(Base):
    """An elicitation script: an ordered list of target forms to be read by a speaker."""

    __tablename__ = "scripts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    word_list: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    sessions = relationship("RecordingSession", back_populates="script")
