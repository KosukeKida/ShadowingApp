import traceback
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, HttpUrl

from app.database import get_db
from app.services.youtube import YouTubeService
from app.services.transcribe import TranscribeService

router = APIRouter(prefix="/api/materials/youtube", tags=["youtube"])


class YouTubeImportRequest(BaseModel):
    """YouTube import request schema."""

    url: str


class YouTubeImportResponse(BaseModel):
    """YouTube import response schema."""

    material_id: int
    title: str
    message: str


@router.post("", response_model=YouTubeImportResponse)
async def import_youtube(
    request: YouTubeImportRequest,
    db: AsyncSession = Depends(get_db),
):
    """Import video from YouTube URL."""
    youtube_service = YouTubeService()
    transcribe_service = TranscribeService()

    try:
        # Download audio from YouTube
        download_result = await youtube_service.download(request.url)

        # Transcribe audio to get segments
        segments = await transcribe_service.transcribe(download_result["audio_path"])

        # Save to database
        material = await youtube_service.save_material(
            db=db,
            title=download_result["title"],
            source_url=request.url,
            audio_path=download_result["audio_path"],
            duration=download_result["duration"],
            thumbnail_path=download_result.get("thumbnail_path"),
            segments=segments,
        )

        return YouTubeImportResponse(
            material_id=material.id,
            title=material.title,
            message="Successfully imported from YouTube",
        )

    except Exception as e:
        error_detail = f"{type(e).__name__}: {str(e)}"
        print(f"YouTube Import Error: {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_detail)
