"""Configuration management for Dog Emotion SDK"""

from typing import Optional, Dict, Any
import os


class Config:
    """Configuration class for SDK settings"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize configuration

        Args:
            api_key: API key for authentication
            base_url: Base URL for API endpoints
            **kwargs: Additional configuration options
        """
        self.api_key = api_key or os.getenv("TRAINI_API_KEY")
        self.base_url = base_url or os.getenv(
            "TRAINI_BASE_URL",
            "https://api.traini.ai/v1"
        )

        # Model configurations
        self.image_model = kwargs.get("image_model", "dog-emotion-v1")
        self.video_model = kwargs.get("video_model", "dog-emotion-video-v1")
        self.tts_model = kwargs.get("tts_model", "bark-tts-v1")
        self.stt_model = kwargs.get("stt_model", "whisper-dog-v1")

        # Processing options
        self.timeout = kwargs.get("timeout", 30)
        self.max_retries = kwargs.get("max_retries", 3)
        self.verbose = kwargs.get("verbose", False)

        # Audio settings
        self.audio_format = kwargs.get("audio_format", "wav")
        self.sample_rate = kwargs.get("sample_rate", 16000)

        # Additional custom configs
        self.custom_config = {
            k: v for k, v in kwargs.items()
            if k not in self.__dict__
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "image_model": self.image_model,
            "video_model": self.video_model,
            "tts_model": self.tts_model,
            "stt_model": self.stt_model,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "verbose": self.verbose,
            "audio_format": self.audio_format,
            "sample_rate": self.sample_rate,
            **self.custom_config
        }
