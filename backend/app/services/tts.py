import asyncio
from pathlib import Path
from datetime import datetime

from app.config import settings


class TtsService:
    """Service for text-to-speech using edge-tts."""

    def __init__(self):
        settings.ensure_directories()

    async def generate_audio(self, text: str, output_path: str) -> dict:
        """Generate audio from text using edge-tts."""
        import edge_tts

        communicate = edge_tts.Communicate(
            text,
            settings.tts_voice,
            rate=settings.tts_rate,
        )
        await communicate.save(output_path)

        # Get duration using mutagen
        duration = self._get_duration(output_path)

        return {
            "path": output_path,
            "duration": duration,
        }

    async def generate_audio_segments(
        self, text_segments: list[dict]
    ) -> list[dict]:
        """Generate audio for multiple text segments."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        results = []
        current_time = 0.0
        total = len(text_segments)

        print(f"Generating TTS for {total} segments...")

        for i, seg in enumerate(text_segments):
            output_path = str(
                settings.materials_dir / f"tts_{timestamp}_{i:04d}.mp3"
            )

            print(f"  [{i+1}/{total}] Generating: {seg['text'][:50]}...")
            audio_info = await self.generate_audio(seg["text"], output_path)

            results.append({
                "text": seg["text"],
                "audio_path": output_path,
                "start": current_time,
                "end": current_time + audio_info["duration"],
                "duration": audio_info["duration"],
            })

            current_time += audio_info["duration"]

        print(f"TTS generation complete. Total duration: {current_time:.1f}s")
        return results

    async def combine_segments(self, segments: list[dict]) -> dict:
        """Combine multiple audio segments into one file using pydub."""
        if not segments:
            raise ValueError("No segments to combine")

        from pydub import AudioSegment

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_path = str(settings.materials_dir / f"combined_{timestamp}.mp3")

        # Combine audio segments
        combined = AudioSegment.empty()
        for seg in segments:
            audio = AudioSegment.from_mp3(seg['audio_path'])
            combined += audio

        # Export combined audio
        combined.export(output_path, format="mp3")

        # Get total duration
        duration = len(combined) / 1000.0  # pydub uses milliseconds

        return {
            "path": output_path,
            "duration": duration,
        }

    def _get_duration(self, audio_path: str) -> float:
        """Get audio duration using mutagen."""
        try:
            from mutagen.mp3 import MP3
            audio = MP3(audio_path)
            return audio.info.length
        except Exception:
            # Fallback: estimate based on file size (rough approximation)
            try:
                import os
                file_size = os.path.getsize(audio_path)
                # Assume ~128kbps for MP3: 128000 bits/s = 16000 bytes/s
                return file_size / 16000.0
            except Exception:
                return 0.0
