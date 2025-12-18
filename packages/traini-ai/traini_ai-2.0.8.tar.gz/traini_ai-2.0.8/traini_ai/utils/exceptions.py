"""Custom exceptions for Dog Emotion SDK"""


class DogEmotionSDKError(Exception):
    """Base exception for Dog Emotion SDK"""
    pass


class InvalidInputError(DogEmotionSDKError):
    """Raised when input validation fails"""
    pass


class APIError(DogEmotionSDKError):
    """Raised when API request fails"""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(DogEmotionSDKError):
    """Raised when authentication fails"""
    pass


class ProcessingError(DogEmotionSDKError):
    """Raised when processing fails"""
    pass


class ModelNotFoundError(DogEmotionSDKError):
    """Raised when specified model is not found"""
    pass
