"""
Enhanced Image analysis module with ensemble model support
Provides both single model and ensemble model options for dog emotion detection
"""

from typing import Dict, Any, Union, Optional
from pathlib import Path
import base64

from .base import BaseModule
from ..utils.validators import validate_image
from ..utils.exceptions import ProcessingError
from ..models import DogEmotionModel, EnsembleDogEmotionModel


class ImageAnalyzerEnsemble(BaseModule):
    """
    Enhanced Image Analyzer with Ensemble Model Support

    This module can use either:
    - Single model (faster, 74-76% accuracy)
    - Ensemble of 4 models (slower, 76-88% accuracy, more robust)

    The ensemble model provides:
    - Higher accuracy through model voting
    - Better handling of difficult emotions (alert, angry, sad, etc.)
    - More reliable confidence scores
    """

    def __init__(self, config, model_dir: Optional[Union[str, Path]] = None,
                 use_ensemble: bool = True,
                 model_weights: Optional[list] = None,
                 voting_strategy: str = 'weighted'):
        """
        Initialize ImageAnalyzerEnsemble

        Args:
            config: Configuration object
            model_dir: Directory containing model files
            use_ensemble: If True, use ensemble of 4 models. If False, use single model.
            model_weights: Optional weights for ensemble models (only used if use_ensemble=True)
                          Order: [AttentionResNet50, ResNet50, ResNet101, EfficientNet]
                          Example: [0.3, 0.3, 0.2, 0.2] to give more weight to first two models
            voting_strategy: Voting strategy for ensemble - 'weighted', 'soft', or 'hard'
                           - 'weighted': Weighted average based on model_weights (default)
                           - 'soft': Simple average of all model probabilities
                           - 'hard': Majority voting (each model votes for top emotion)
        """
        super().__init__(config)
        self.use_ensemble = use_ensemble

        if use_ensemble:
            self.emotion_model = EnsembleDogEmotionModel(
                model_dir,
                model_weights=model_weights,
                voting_strategy=voting_strategy
            )
            self.logger.info(f"ImageAnalyzer initialized with ENSEMBLE model ({self.emotion_model.ensemble_size} models, strategy={voting_strategy})")
        else:
            self.emotion_model = DogEmotionModel(model_dir)
            self.logger.info("ImageAnalyzer initialized with SINGLE model")

    def analyze(
        self,
        image_path: Union[str, Path, bytes],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze dog emotion from image

        Args:
            image_path: Path to image file, URL, or image bytes
            **kwargs: Additional parameters
                - language: Output language (default: 'en')
                - detail_level: 'simple' or 'detailed' (default: 'simple')
                - return_confidence: Whether to return confidence scores (default: False)
                - return_all_predictions: Return all emotion probabilities (default: False)
                - return_model_details: Return individual model predictions (ensemble only, default: False)

        Returns:
            Dict with keys:
                - text: Description of detected emotion
                - audio: Audio narration as bytes
                - emotion: Detected emotion label
                - confidence: Confidence score
                - all_predictions: All emotion probabilities (if requested)
                - model_predictions: Individual model results (ensemble only, if requested)
                - ensemble_size: Number of models used (ensemble only)

        Example:
            >>> analyzer = ImageAnalyzerEnsemble(config, use_ensemble=True)
            >>> result = analyzer.analyze("dog.jpg", return_confidence=True)
            >>> print(f"{result['emotion']}: {result['confidence']:.2%}")
            'happy: 85.3%'
        """
        self.logger.info(f"Analyzing image: {image_path}")

        # Validate input
        validate_image(image_path)

        # Process image
        return self.process(image_path, **kwargs)

    def process(
        self,
        input_data: Union[str, Path, bytes],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process image and detect emotions

        Args:
            input_data: Image data
            **kwargs: Additional parameters

        Returns:
            Analysis results
        """
        try:
            # Load image
            if isinstance(input_data, bytes):
                image_bytes = input_data
            else:
                image_bytes = self._load_file(str(input_data))

            # Extract parameters
            language = kwargs.get('language', 'en')
            detail_level = kwargs.get('detail_level', 'simple')
            return_confidence = kwargs.get('return_confidence', True)  # Default True for ensemble
            return_all_predictions = kwargs.get('return_all_predictions', False)
            return_model_details = kwargs.get('return_model_details', False)

            # Detect emotion using model
            emotion_result = self._detect_emotion(image_bytes)

            # Generate text description
            text = self._generate_description(
                emotion_result,
                language=language,
                detail_level=detail_level
            )

            # Generate audio narration
            audio = self._generate_audio(text)

            # Build result
            result = {
                'text': text,
                'audio': audio,
                'emotion': emotion_result['emotion'],
                'confidence': emotion_result['confidence']
            }

            # Add ensemble info
            if 'ensemble_size' in emotion_result:
                result['ensemble_size'] = emotion_result['ensemble_size']
                result['model_type'] = 'ensemble'
            else:
                result['model_type'] = 'single'

            # Optional: all predictions
            if return_all_predictions:
                result['all_predictions'] = emotion_result['all_predictions']

            # Optional: individual model predictions (ensemble only)
            if return_model_details and 'model_predictions' in emotion_result:
                result['model_predictions'] = emotion_result['model_predictions']

            self.logger.info(
                f"Analysis complete: {emotion_result['emotion']} "
                f"({emotion_result['confidence']:.2%} confidence)"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            raise ProcessingError(f"Failed to process image: {str(e)}")

    def _detect_emotion(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Detect emotion from image using ML model

        Args:
            image_bytes: Image data

        Returns:
            Dict with emotion and confidence
        """
        try:
            # Use the trained model to predict emotion
            result = self.emotion_model.predict(image_bytes)
            return result
        except Exception as e:
            self.logger.error(f"Error in emotion detection: {str(e)}")
            raise ProcessingError(f"Emotion detection failed: {str(e)}")

    def _generate_description(
        self,
        emotion_result: Dict[str, Any],
        language: str = 'en',
        detail_level: str = 'simple'
    ) -> str:
        """
        Generate text description of emotion

        Args:
            emotion_result: Emotion detection results
            language: Output language
            detail_level: Level of detail

        Returns:
            Text description
        """
        emotion = emotion_result['emotion']
        confidence = emotion_result['confidence']

        # Emotion descriptions in different languages
        emotion_descriptions = {
            'en': {
                'happy': 'happy and excited',
                'sad': 'sad or down',
                'angry': 'angry or aggressive',
                'alert': 'alert and attentive',
                'relaxed': 'relaxed and calm',
                'fear': 'fearful or scared',
                'anxiety': 'anxious or nervous',
                'anticipation': 'anticipating something',
                'appeasement': 'showing appeasement',
                'caution': 'being cautious',
                'confident': 'confident and self-assured',
                'curiosity': 'curious and interested',
                'sleepy': 'sleepy or tired'
            },
            'zh': {
                'happy': '快乐和兴奋',
                'sad': '悲伤或沮丧',
                'angry': '生气或有攻击性',
                'alert': '警觉和专注',
                'relaxed': '放松和平静',
                'fear': '害怕或恐惧',
                'anxiety': '焦虑或紧张',
                'anticipation': '期待某事',
                'appeasement': '表现出安抚',
                'caution': '保持谨慎',
                'confident': '自信和笃定',
                'curiosity': '好奇和感兴趣',
                'sleepy': '困倦或疲惫'
            }
        }

        # Get emotion description
        emotion_desc = emotion_descriptions.get(language, emotion_descriptions['en'])
        emotion_text = emotion_desc.get(emotion, emotion)

        # Build description based on detail level
        if detail_level == 'detailed':
            if language == 'zh':
                if self.use_ensemble:
                    text = (f"这只狗看起来{emotion_text}。\n"
                           f"置信度：{confidence*100:.1f}%\n"
                           f"（由{emotion_result.get('ensemble_size', 1)}个AI模型综合判断）")
                else:
                    text = (f"这只狗看起来{emotion_text}。\n"
                           f"置信度：{confidence*100:.1f}%")
            else:
                if self.use_ensemble:
                    text = (f"The dog appears {emotion_text}.\n"
                           f"Confidence: {confidence*100:.1f}%\n"
                           f"(Analyzed by {emotion_result.get('ensemble_size', 1)} AI models)")
                else:
                    text = (f"The dog appears {emotion_text}.\n"
                           f"Confidence: {confidence*100:.1f}%")
        else:
            # Simple
            if language == 'zh':
                text = f"这只狗看起来{emotion_text}。"
            else:
                text = f"The dog appears {emotion_text}."

        return text

    def switch_model(self, use_ensemble: bool):
        """
        Switch between single and ensemble model

        Args:
            use_ensemble: True for ensemble, False for single model
        """
        if use_ensemble == self.use_ensemble:
            self.logger.info(f"Already using {'ensemble' if use_ensemble else 'single'} model")
            return

        self.use_ensemble = use_ensemble

        if use_ensemble:
            self.emotion_model = EnsembleDogEmotionModel()
            self.logger.info(f"Switched to ENSEMBLE model ({self.emotion_model.ensemble_size} models)")
        else:
            self.emotion_model = DogEmotionModel()
            self.logger.info("Switched to SINGLE model")

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about current model

        Returns:
            Dict with model information
        """
        info = {
            'model_type': 'ensemble' if self.use_ensemble else 'single',
            'classes': self.emotion_model.classes,
            'num_classes': len(self.emotion_model.classes) if self.emotion_model.classes else 0,
            'device': str(self.emotion_model.device)
        }

        if self.use_ensemble:
            info['ensemble_size'] = len(self.emotion_model.models)
            info['accuracy_range'] = '76-88%'
        else:
            info['accuracy_range'] = '74-76%'

        return info

    def __repr__(self):
        model_type = 'Ensemble' if self.use_ensemble else 'Single'
        return f"ImageAnalyzerEnsemble(model_type={model_type})"
