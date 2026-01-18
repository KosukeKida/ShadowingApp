from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Practice(Base):
    """Practice (練習記録) model."""

    __tablename__ = "practices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    segment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("segments.id"), nullable=False
    )
    recording_path: Mapped[str] = mapped_column(String(500), nullable=False)
    transcribed_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    evaluation: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationships
    segment: Mapped["Segment"] = relationship("Segment", back_populates="practices")

    def __repr__(self) -> str:
        return f"<Practice(id={self.id}, segment_id={self.segment_id}, created_at={self.created_at})>"
