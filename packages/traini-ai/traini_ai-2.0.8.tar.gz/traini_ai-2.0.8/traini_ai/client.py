"""
Main client class for Traini AI SDK
"""

from typing import Optional, Dict, Any
from .modules.image_analyzer import ImageAnalyzer
from .modules.video_analyzer import VideoAnalyzer
from .modules.human_to_dog import HumanToDogTranslator
from .modules.dog_to_human import DogToHumanTranslator
from .utils.config import Config


class TrainiClient:
    """
    Main client for Traini AI SDK

    Example:
        >>> from traini_ai import TrainiClient
        >>> client = TrainiClient(api_key="your_api_key")
        >>> result = client.analyze_image("path/to/dog.jpg")
        >>> print(result['text'])
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Traini AI SDK client

        Args:
            api_key: API key for authentication (if using cloud services)
            base_url: Base URL for API endpoints (if using cloud services)
            config: Additional configuration options
        """
        self.config = Config(api_key=api_key, base_url=base_url, **(config or {}))

        # Initialize modules
        self.image_analyzer = ImageAnalyzer(self.config)
        self.video_analyzer = VideoAnalyzer(self.config)
        self.human_to_dog = HumanToDogTranslator(self.config)
        self.dog_to_human = DogToHumanTranslator(self.config)

    def analyze_image(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze dog emotion from image

        Args:
            image_path: Path to image file or URL
            **kwargs: Additional parameters
                - language: Output language (default: 'en')
                - detail_level: 'simple' or 'detailed' (default: 'simple')
                - return_confidence: Return confidence scores (default: False)

        Returns:
            Dict containing 'audio' (bytes) and 'text' (str)

        Example:
            >>> result = client.analyze_image("dog.jpg", return_confidence=True)
            >>> print(f"Emotion: {result['emotion']}, Confidence: {result['confidence']}")
        """
        return self.image_analyzer.analyze(image_path, **kwargs)

    def analyze_video(self, video_path: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze dog emotion from video

        Args:
            video_path: Path to video file or URL
            **kwargs: Additional parameters
                - sample_rate: Frames per second to analyze (default: 1)
                - return_timeline: Return frame-by-frame timeline (default: False)

        Returns:
            Dict containing 'audio' (bytes) and 'text' (str)

        Example:
            >>> result = client.analyze_video("video.mp4", return_timeline=True)
            >>> print(f"Dominant emotion: {result['dominant_emotion']}")
        """
        return self.video_analyzer.analyze(video_path, **kwargs)

    def translate_human_to_dog(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """
        Translate human speech to dog-understandable format

        Args:
            audio_path: Path to audio file or bytes
            **kwargs: Additional parameters
                - tone: 'friendly', 'commanding', 'playful', 'calm' (default: 'friendly')
                - include_transcription: Include original speech text (default: False)

        Returns:
            Dict containing 'audio' (bytes) and 'text' (str)

        Example:
            >>> result = client.translate_human_to_dog("speech.wav", tone='friendly')
            >>> print(result['text'])
        """
        return self.human_to_dog.translate(audio_path, **kwargs)

    def translate_dog_to_human(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """
        Translate dog sounds to human language

        Args:
            audio_path: Path to audio file or bytes
            **kwargs: Additional parameters
                - language: Output language (default: 'en')
                - include_sound_type: Include sound classification (default: False)

        Returns:
            Dict containing 'audio' (bytes) and 'text' (str)

        Example:
            >>> result = client.translate_dog_to_human("bark.wav", include_sound_type=True)
            >>> print(f"Sound type: {result['sound_type']}, Meaning: {result['text']}")
        """
        return self.dog_to_human.translate(audio_path, **kwargs)


# Backward compatibility alias
DogEmotionClient = TrainiClient
