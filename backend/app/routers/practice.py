from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Segment, Practice, Material
from app.config import settings

router = APIRouter(prefix="/api", tags=["practice"])


class PracticeResponse(BaseModel):
    """Practice response schema."""

    id: int
    segment_id: int
    recording_path: str
    transcribed_text: str | None
    evaluation: dict | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/segments/{segment_id}/audio")
async def get_segment_audio(segment_id: int, db: AsyncSession = Depends(get_db)):
    """Get audio file for a segment."""
    result = await db.execute(
        select(Segment)
        .options(selectinload(Segment.material))
        .where(Segment.id == segment_id)
    )
    segment = result.scalar_one_or_none()

    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")

    # For TTS segments (PDF), use segment audio
    if segment.audio_path:
        path = Path(segment.audio_path)
        if path.exists():
            return FileResponse(path, media_type="audio/mpeg")

    # For YouTube segments, use the material's main audio file
    if segment.material and segment.material.audio_path:
        path = Path(segment.material.audio_path)
        if path.exists():
            # Determine media type based on file extension
            ext = path.suffix.lower()
            media_types = {
                ".mp3": "audio/mpeg",
                ".m4a": "audio/mp4",
                ".wav": "audio/wav",
                ".webm": "audio/webm",
                ".ogg": "audio/ogg",
            }
            media_type = media_types.get(ext, "audio/mpeg")
            return FileResponse(path, media_type=media_type)

    raise HTTPException(status_code=404, detail="Audio not available")


@router.post("/segments/{segment_id}/practice", response_model=PracticeResponse)
async def upload_practice(
    segment_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload practice recording."""
    result = await db.execute(select(Segment).where(Segment.id == segment_id))
    segment = result.scalar_one_or_none()

    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")

    # Save recording file
    settings.ensure_directories()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"practice_{segment_id}_{timestamp}.webm"
    recording_path = settings.recordings_dir / filename

    content = await file.read()
    with open(recording_path, "wb") as f:
        f.write(content)

    # Create practice record
    practice = Practice(
        segment_id=segment_id,
        recording_path=str(recording_path),
    )
    db.add(practice)
    await db.commit()
    await db.refresh(practice)

    return practice


@router.get("/practice/{practice_id}", response_model=PracticeResponse)
async def get_practice(practice_id: int, db: AsyncSession = Depends(get_db)):
    """Get practice record."""
    result = await db.execute(select(Practice).where(Practice.id == practice_id))
    practice = result.scalar_one_or_none()

    if not practice:
        raise HTTPException(status_code=404, detail="Practice not found")

    return practice


@router.get("/segments/{segment_id}/practices", response_model=list[PracticeResponse])
async def list_practices(segment_id: int, db: AsyncSession = Depends(get_db)):
    """List all practices for a segment."""
    result = await db.execute(
        select(Practice)
        .where(Practice.segment_id == segment_id)
        .order_by(Practice.created_at.desc())
    )
    practices = result.scalars().all()
    return practices
