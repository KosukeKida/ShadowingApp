from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Base paths
    app_name: str = "Shadowing App"
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = base_dir / "data"
    materials_dir: Path = data_dir / "materials"
    recordings_dir: Path = data_dir / "recordings"

    # Database
    database_url: str = f"sqlite+aiosqlite:///{data_dir}/shadowing.db"

    # Whisper settings
    whisper_model: str = "base"  # tiny, base, small, medium, large
    whisper_device: str = "cpu"  # cpu or cuda
    whisper_compute_type: str = "int8"  # float16, int8

    # TTS settings
    tts_voice: str = "en-US-JennyNeural"  # Microsoft Edge TTS voice
    tts_rate: str = "+0%"  # Speech rate adjustment

    # LLM settings
    llm_provider: str = "ollama"  # ollama or claude
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    claude_api_key: str = ""

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.materials_dir.mkdir(parents=True, exist_ok=True)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
