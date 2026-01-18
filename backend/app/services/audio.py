import asyncio
from pathlib import Path

from app.config import settings


class AudioService:
    """Service for audio processing utilities."""

    def __init__(self):
        settings.ensure_directories()

    async def extract_segment(
        self,
        source_path: str,
        start_time: float,
        end_time: float,
        output_path: str,
    ) -> str:
        """Extract a segment from audio file."""
        duration = end_time - start_time

        cmd = [
            "ffmpeg",
            "-i", source_path,
            "-ss", str(start_time),
            "-t", str(duration),
            "-c", "copy",
            output_path,
            "-y",
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"Failed to extract segment: {stderr.decode()}")

        return output_path

    async def convert_to_wav(self, source_path: str, output_path: str) -> str:
        """Convert audio to WAV format for processing."""
        cmd = [
            "ffmpeg",
            "-i", source_path,
            "-ar", "16000",  # 16kHz sample rate
            "-ac", "1",     # Mono
            "-c:a", "pcm_s16le",
            output_path,
            "-y",
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"Failed to convert audio: {stderr.decode()}")

        return output_path

    async def get_waveform_data(
        self, audio_path: str, samples: int = 1000
    ) -> list[float]:
        """Get waveform data for visualization."""
        # This is a simplified version - for production use a proper audio library
        cmd = [
            "ffprobe",
            "-f", "lavfi",
            "-i", f"amovie={audio_path},astats=metadata=1:reset=1",
            "-show_entries", "frame_tags=lavfi.astats.Overall.RMS_level",
            "-of", "csv=p=0",
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate()

        if process.returncode != 0:
            # Return empty data on error
            return [0.0] * samples

        # Parse output
        values = []
        for line in stdout.decode().strip().split('\n'):
            try:
                values.append(float(line))
            except ValueError:
                continue

        # Resample to desired number of samples
        if len(values) == 0:
            return [0.0] * samples

        if len(values) >= samples:
            step = len(values) / samples
            return [values[int(i * step)] for i in range(samples)]
        else:
            return values + [0.0] * (samples - len(values))
