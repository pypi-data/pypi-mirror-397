"""
Traini AI SDK
A comprehensive SDK for dog emotion analysis and human-dog communication
"""

__version__ = "2.0.8"
__author__ = "Traini AI Team"

from .client import TrainiClient
from .modules.image_analyzer import ImageAnalyzer
from .modules.video_analyzer import VideoAnalyzer
from .modules.human_to_dog import HumanToDogTranslator
from .modules.dog_to_human import DogToHumanTranslator
from .modules.integrated_analysis_with_emotion import IntegratedImageAnalysisWithEmotion

# Backward compatible aliases
DogEmotionClient = TrainiClient

__all__ = [
    "TrainiClient",
    "DogEmotionClient",  # Backward compatible
    "ImageAnalyzer",
    "VideoAnalyzer",
    "HumanToDogTranslator",
    "DogToHumanTranslator",
    "IntegratedImageAnalysisWithEmotion",
]
