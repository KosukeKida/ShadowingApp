import re
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Material, Segment


class PdfService:
    """Service for extracting text from PDF files."""

    def __init__(self):
        settings.ensure_directories()

    async def extract_text(self, file: UploadFile) -> list[dict]:
        """Extract text from PDF and split into segments."""
        import fitz  # PyMuPDF

        # Save uploaded file temporarily
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        temp_path = settings.materials_dir / f"temp_{timestamp}.pdf"

        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        try:
            # Extract text from PDF
            doc = fitz.open(temp_path)
            full_text = ""

            for page in doc:
                full_text += page.get_text()

            doc.close()

            # Split into sentences
            segments = self._split_into_sentences(full_text)

            return segments

        finally:
            # Clean up temp file
            temp_path.unlink(missing_ok=True)

    def _split_into_sentences(self, text: str, max_segments: int = 10) -> list[dict]:
        """Split text into sentences.

        Args:
            text: Full text to split
            max_segments: Maximum number of segments to return (default 50)
        """
        # Clean up text
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Split by sentence endings
        sentence_pattern = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_pattern, text)

        # Filter out empty sentences and create segments
        segments = []
        for sentence in sentences:
            sentence = sentence.strip()
            # Skip very short segments and segments that look like headers/page numbers
            if sentence and len(sentence) > 10 and not sentence.isdigit():
                segments.append({
                    "text": sentence,
                })
                # Limit number of segments for performance
                if len(segments) >= max_segments:
                    break

        return segments

    async def save_material(
        self,
        db: AsyncSession,
        title: str,
        audio_path: str,
        duration: float,
        segments: list[dict],
    ) -> Material:
        """Save material and segments to database."""
        material = Material(
            title=title,
            source_type="pdf",
            source_url=None,
            audio_path=audio_path,
            duration=duration,
        )
        db.add(material)
        await db.flush()

        for i, seg in enumerate(segments):
            segment = Segment(
                material_id=material.id,
                text=seg["text"],
                start_time=seg.get("start", 0.0),
                end_time=seg.get("end", 0.0),
                audio_path=seg.get("audio_path"),
                order=i,
            )
            db.add(segment)

        await db.commit()
        await db.refresh(material)

        return material
