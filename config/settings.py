"""Configuration module for Autonomous YouTube Pipeline."""

import os
from pathlib import Path
from typing import Optional

# Try loading python-dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure Homebrew and standard macOS tool paths are accessible
for p in ["/opt/homebrew/bin", "/usr/local/bin"]:
    if p not in os.environ.get("PATH", "") and os.path.exists(p):
        os.environ["PATH"] = f"{p}:{os.environ.get('PATH', '')}"

class Settings:
    """Central configuration class with paths and API keys."""

    # Project Directories
    BASE_DIR: Path = BASE_DIR
    TOPICS_DIR: Path = BASE_DIR / "topics"
    SCRIPTS_DIR: Path = BASE_DIR / "scripts"
    AUDIO_DIR: Path = BASE_DIR / "audio"
    IMAGES_DIR: Path = BASE_DIR / "images"
    VIDEOS_DIR: Path = BASE_DIR / "videos"
    THUMBNAILS_DIR: Path = BASE_DIR / "thumbnails"
    METADATA_DIR: Path = BASE_DIR / "metadata"
    LOGS_DIR: Path = BASE_DIR / "logs"
    CONFIG_DIR: Path = BASE_DIR / "config"
    MUSIC_DIR: Path = BASE_DIR / "music"

    # Runtime Configuration
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # LLM Settings (Gemini / OpenAI / Anthropic)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # Voiceover / Speech Synthesis Settings
    TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "google_tts").lower()
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GOOGLE_TTS_VOICE_NAME: str = os.getenv("GOOGLE_TTS_VOICE_NAME", "en-US-Journey-F")
    GOOGLE_TTS_LANGUAGE_CODE: str = os.getenv("GOOGLE_TTS_LANGUAGE_CODE", "en-US")
    GOOGLE_TTS_SPEAKING_RATE: float = float(os.getenv("GOOGLE_TTS_SPEAKING_RATE", "1.05"))
    ELEVENLABS_API_KEY: Optional[str] = os.getenv("ELEVENLABS_API_KEY")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    OPENAI_TTS_VOICE: str = os.getenv("OPENAI_TTS_VOICE", "alloy")

    # Visuals & Slide Generation Settings
    IMAGE_PROVIDER: str = os.getenv("IMAGE_PROVIDER", "slide_engine").lower()
    IMAGEN_API_KEY: Optional[str] = os.getenv("IMAGEN_API_KEY", os.getenv("GEMINI_API_KEY"))

    # Video Production Specifications
    VIDEO_RESOLUTION_WIDTH: int = int(os.getenv("VIDEO_RESOLUTION_WIDTH", "1920"))
    VIDEO_RESOLUTION_HEIGHT: int = int(os.getenv("VIDEO_RESOLUTION_HEIGHT", "1080"))
    VIDEO_FPS: int = int(os.getenv("VIDEO_FPS", "30"))
    MIN_WORDS: int = int(os.getenv("MIN_WORDS", "1400"))
    MAX_WORDS: int = int(os.getenv("MAX_WORDS", "1800"))
    WORDS_PER_MINUTE: int = int(os.getenv("WORDS_PER_MINUTE", "145"))
    MUSIC_VOLUME: float = float(os.getenv("MUSIC_VOLUME", "0.08"))

    # YouTube Data API v3 Settings
    YOUTUBE_CLIENT_SECRETS_FILE: Path = BASE_DIR / os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "config/client_secrets.json")
    YOUTUBE_TOKEN_FILE: Path = BASE_DIR / os.getenv("YOUTUBE_TOKEN_FILE", "config/token.json")
    YOUTUBE_DEFAULT_PRIVACY: str = os.getenv("YOUTUBE_DEFAULT_PRIVACY", "private")
    YOUTUBE_CATEGORY_ID: str = os.getenv("YOUTUBE_CATEGORY_ID", "28")
    YOUTUBE_AI_DISCLOSURE: bool = os.getenv("YOUTUBE_AI_DISCLOSURE", "true").lower() == "true"

    @classmethod
    def ensure_directories(cls) -> None:
        """Create all required pipeline storage directories if missing."""
        directories = [
            cls.TOPICS_DIR,
            cls.SCRIPTS_DIR,
            cls.AUDIO_DIR,
            cls.IMAGES_DIR,
            cls.VIDEOS_DIR,
            cls.THUMBNAILS_DIR,
            cls.METADATA_DIR,
            cls.LOGS_DIR,
            cls.CONFIG_DIR,
            cls.MUSIC_DIR,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

settings = Settings()
