import asyncio
from pathlib import Path
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Material, Segment


class YouTubeService:
    """Service for downloading videos from YouTube."""

    def __init__(self):
        settings.ensure_directories()

    async def download(self, url: str) -> dict:
        """Download audio from YouTube URL using yt-dlp."""
        import yt_dlp

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_template = str(settings.materials_dir / f"youtube_{timestamp}.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': output_template,
            'writethumbnail': True,
            'quiet': True,
            'no_warnings': True,
        }

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(
            None, self._download_sync, url, ydl_opts
        )

        title = info.get("title", "Unknown")
        duration = info.get("duration", 0)
        ext = info.get("ext", "m4a")

        # Find the downloaded audio file
        audio_path = str(settings.materials_dir / f"youtube_{timestamp}.{ext}")

        # Find thumbnail if exists
        thumbnail_path = None
        for ext in [".jpg", ".png", ".webp"]:
            thumb_file = settings.materials_dir / f"youtube_{timestamp}{ext}"
            if thumb_file.exists():
                thumbnail_path = str(thumb_file)
                break

        return {
            "title": title,
            "audio_path": audio_path,
            "duration": duration,
            "thumbnail_path": thumbnail_path,
        }

    def _download_sync(self, url: str, ydl_opts: dict) -> dict:
        """Synchronous download function."""
        import yt_dlp

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return info

    async def save_material(
        self,
        db: AsyncSession,
        title: str,
        source_url: str,
        audio_path: str,
        duration: float,
        thumbnail_path: str | None,
        segments: list[dict],
    ) -> Material:
        """Save material and segments to database."""
        material = Material(
            title=title,
            source_type="youtube",
            source_url=source_url,
            audio_path=audio_path,
            duration=duration,
            thumbnail_path=thumbnail_path,
        )
        db.add(material)
        await db.flush()

        for i, seg in enumerate(segments):
            segment = Segment(
                material_id=material.id,
                text=seg["text"],
                start_time=seg["start"],
                end_time=seg["end"],
                order=i,
            )
            db.add(segment)

        await db.commit()
        await db.refresh(material)

        return material
