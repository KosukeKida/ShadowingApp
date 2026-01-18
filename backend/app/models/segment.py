from sqlalchemy import String, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Segment(Base):
    """Segment (セグメント/文単位) model."""

    __tablename__ = "segments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    material_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("materials.id"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    audio_path: Mapped[str | None] = mapped_column(String(500), nullable=True)  # TTS audio for PDF
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    material: Mapped["Material"] = relationship("Material", back_populates="segments")
    practices: Mapped[list["Practice"]] = relationship(
        "Practice", back_populates="segment", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Segment(id={self.id}, text='{self.text[:30]}...', start={self.start_time})>"
