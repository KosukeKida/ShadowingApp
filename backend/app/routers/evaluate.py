from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.database import get_db
from app.models import Practice, Segment
from app.services.transcribe import TranscribeService
from app.services.evaluator import EvaluatorService

router = APIRouter(prefix="/api/practice", tags=["evaluate"])


class EvaluationRequest(BaseModel):
    """Evaluation request schema."""

    pass  # No additional fields needed


class EvaluationResponse(BaseModel):
    """Evaluation response schema."""

    practice_id: int
    transcribed_text: str
    original_text: str
    evaluation: dict


@router.post("/{practice_id}/evaluate", response_model=EvaluationResponse)
async def evaluate_practice(
    practice_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Evaluate practice recording using Whisper and LLM."""
    result = await db.execute(
        select(Practice)
        .options(selectinload(Practice.segment))
        .where(Practice.id == practice_id)
    )
    practice = result.scalar_one_or_none()

    if not practice:
        raise HTTPException(status_code=404, detail="Practice not found")

    transcribe_service = TranscribeService()
    evaluator_service = EvaluatorService()

    try:
        # Transcribe the recording
        transcription = await transcribe_service.transcribe_single(
            practice.recording_path
        )
        transcribed_text = transcription["text"]

        # Get original text from segment
        original_text = practice.segment.text

        # Evaluate using LLM
        evaluation = await evaluator_service.evaluate(
            original_text=original_text,
            transcribed_text=transcribed_text,
        )

        # Update practice record
        practice.transcribed_text = transcribed_text
        practice.evaluation = evaluation
        await db.commit()

        return EvaluationResponse(
            practice_id=practice_id,
            transcribed_text=transcribed_text,
            original_text=original_text,
            evaluation=evaluation,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
