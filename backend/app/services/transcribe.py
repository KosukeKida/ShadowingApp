import asyncio
from functools import lru_cache

from app.config import settings


class TranscribeService:
    """Service for transcribing audio using faster-whisper."""

    _model = None

    @classmethod
    def get_model(cls):
        """Get or create Whisper model (singleton)."""
        if cls._model is None:
            from faster_whisper import WhisperModel

            cls._model = WhisperModel(
                settings.whisper_model,
                device=settings.whisper_device,
                compute_type=settings.whisper_compute_type,
            )
        return cls._model

    async def transcribe(self, audio_path: str) -> list[dict]:
        """Transcribe audio file and return segments."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._transcribe_sync, audio_path)

    def _transcribe_sync(self, audio_path: str) -> list[dict]:
        """Synchronous transcription."""
        model = self.get_model()

        segments_iter, info = model.transcribe(
            audio_path,
            language="en",
            task="transcribe",
            word_timestamps=True,
        )

        segments = []
        for segment in segments_iter:
            segments.append({
                "text": segment.text.strip(),
                "start": segment.start,
                "end": segment.end,
            })

        return segments

    async def transcribe_single(self, audio_path: str) -> dict:
        """Transcribe audio file and return single text."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._transcribe_single_sync, audio_path
        )

    def _transcribe_single_sync(self, audio_path: str) -> dict:
        """Synchronous single transcription."""
        model = self.get_model()

        segments_iter, info = model.transcribe(
            audio_path,
            language="en",
            task="transcribe",
        )

        text_parts = []
        for segment in segments_iter:
            text_parts.append(segment.text.strip())

        return {
            "text": " ".join(text_parts),
            "language": info.language,
            "duration": info.duration,
        }
