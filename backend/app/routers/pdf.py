import traceback
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.services.pdf import PdfService
from app.services.tts import TtsService

router = APIRouter(prefix="/api/materials/pdf", tags=["pdf"])


class PdfImportResponse(BaseModel):
    """PDF import response schema."""

    material_id: int
    title: str
    segment_count: int
    message: str


@router.post("", response_model=PdfImportResponse)
async def import_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Import PDF and generate TTS audio."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    pdf_service = PdfService()
    tts_service = TtsService()

    try:
        # Extract text from PDF
        text_segments = await pdf_service.extract_text(file)

        # Generate TTS audio for each segment
        audio_segments = await tts_service.generate_audio_segments(text_segments)

        # Calculate total duration from segments
        total_duration = sum(seg["duration"] for seg in audio_segments)

        # Use first segment's audio as material audio (for compatibility)
        # Individual segment audios are used for practice
        material_audio_path = audio_segments[0]["audio_path"] if audio_segments else ""

        # Save to database
        material = await pdf_service.save_material(
            db=db,
            title=file.filename.replace(".pdf", ""),
            audio_path=material_audio_path,
            duration=total_duration,
            segments=audio_segments,
        )

        return PdfImportResponse(
            material_id=material.id,
            title=material.title,
            segment_count=len(audio_segments),
            message="Successfully imported PDF with TTS audio",
        )

    except Exception as e:
        error_detail = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(f"PDF Import Error: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)
