"""Input validation utilities"""

import os
from pathlib import Path
from typing import Union
from .exceptions import InvalidInputError


SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
SUPPORTED_AUDIO_FORMATS = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}


def validate_image(image_path: Union[str, Path, bytes]) -> bool:
    """
    Validate image input

    Args:
        image_path: Path to image file, URL, or bytes

    Returns:
        True if valid

    Raises:
        InvalidInputError: If validation fails
    """
    if isinstance(image_path, bytes):
        if len(image_path) == 0:
            raise InvalidInputError("Image bytes cannot be empty")
        return True

    if isinstance(image_path, str) and image_path.startswith(('http://', 'https://')):
        # URL validation
        return True

    # File path validation
    path = Path(image_path)
    if not path.exists():
        raise InvalidInputError(f"Image file not found: {image_path}")

    if path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
        raise InvalidInputError(
            f"Unsupported image format: {path.suffix}. "
            f"Supported formats: {SUPPORTED_IMAGE_FORMATS}"
        )

    return True


def validate_video(video_path: Union[str, Path, bytes]) -> bool:
    """
    Validate video input

    Args:
        video_path: Path to video file, URL, or bytes

    Returns:
        True if valid

    Raises:
        InvalidInputError: If validation fails
    """
    if isinstance(video_path, bytes):
        if len(video_path) == 0:
            raise InvalidInputError("Video bytes cannot be empty")
        return True

    if isinstance(video_path, str) and video_path.startswith(('http://', 'https://')):
        return True

    path = Path(video_path)
    if not path.exists():
        raise InvalidInputError(f"Video file not found: {video_path}")

    if path.suffix.lower() not in SUPPORTED_VIDEO_FORMATS:
        raise InvalidInputError(
            f"Unsupported video format: {path.suffix}. "
            f"Supported formats: {SUPPORTED_VIDEO_FORMATS}"
        )

    return True


def validate_audio(audio_path: Union[str, Path, bytes]) -> bool:
    """
    Validate audio input

    Args:
        audio_path: Path to audio file, URL, or bytes

    Returns:
        True if valid

    Raises:
        InvalidInputError: If validation fails
    """
    if isinstance(audio_path, bytes):
        if len(audio_path) == 0:
            raise InvalidInputError("Audio bytes cannot be empty")
        return True

    if isinstance(audio_path, str) and audio_path.startswith(('http://', 'https://')):
        return True

    path = Path(audio_path)
    if not path.exists():
        raise InvalidInputError(f"Audio file not found: {audio_path}")

    if path.suffix.lower() not in SUPPORTED_AUDIO_FORMATS:
        raise InvalidInputError(
            f"Unsupported audio format: {path.suffix}. "
            f"Supported formats: {SUPPORTED_AUDIO_FORMATS}"
        )

    return True
