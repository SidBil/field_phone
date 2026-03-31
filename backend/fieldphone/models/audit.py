from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fieldphone.database import Base


class FlagType(PyEnum):
    CONSISTENCY = "consistency"
    DIVERGENCE = "divergence"
    OFF_SCRIPT = "off_script"
    TONE_MISMATCH = "tone_mismatch"


class FlagSeverity(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AuditFlag(Base):
    """
    A flag raised by automated consistency/quality checks. Never modifies
    data — only surfaces problems for the linguist to review.
    """

    __tablename__ = "audit_flags"

    id: Mapped[int] = mapped_column(primary_key=True)
    token_id: Mapped[int] = mapped_column(ForeignKey("tokens.id"))
    related_token_id: Mapped[int | None] = mapped_column(ForeignKey("tokens.id"))
    flag_type: Mapped[FlagType] = mapped_column(Enum(FlagType))
    severity: Mapped[FlagSeverity] = mapped_column(Enum(FlagSeverity))
    description: Mapped[str] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    token = relationship("Token", back_populates="audit_flags", foreign_keys=[token_id])
    related_token = relationship("Token", foreign_keys=[related_token_id])
