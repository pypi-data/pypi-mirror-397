"""Dog emotion detection model"""

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging


class DogEmotionModelArchitecture(nn.Module):
    """
    Dog emotion model architecture (matches training code EXACTLY)

    Important: This must match the training code structure exactly.
    Training code directly modifies ResNet's fc layer without wrapper.
    """

    def __init__(self, num_classes=13, model_name='resnet34', pretrained=False):
        super(DogEmotionModelArchitecture, self).__init__()

        # Load the base ResNet model (matching training code exactly)
        if model_name == 'resnet18':
            weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
            base_model = models.resnet18(weights=weights)
        elif model_name == 'resnet34':
            weights = models.ResNet34_Weights.IMAGENET1K_V1 if pretrained else None
            base_model = models.resnet34(weights=weights)
        elif model_name == 'resnet50':
            weights = models.ResNet50_Weights.IMAGENET1K_V1 if pretrained else None
            base_model = models.resnet50(weights=weights)
        else:
            raise ValueError(f"Unsupported model: {model_name}")

        # Copy all layers from base_model to self (no wrapper)
        # This makes state_dict keys match training format exactly
        self.conv1 = base_model.conv1
        self.bn1 = base_model.bn1
        self.relu = base_model.relu
        self.maxpool = base_model.maxpool
        self.layer1 = base_model.layer1
        self.layer2 = base_model.layer2
        self.layer3 = base_model.layer3
        self.layer4 = base_model.layer4
        self.avgpool = base_model.avgpool

        # Replace the fc layer with correct number of classes
        in_features = base_model.fc.in_features
        self.fc = nn.Linear(in_features, num_classes)

        # Store metadata
        self.num_classes = num_classes
        self.model_name = model_name

    def forward(self, x):
        # ResNet forward pass (copied from torchvision.models.resnet)
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)

        return x


class DogEmotionModel:
    """
    Dog emotion detection model wrapper

    This class handles loading the trained model and performing inference
    on dog images to detect emotions.
    """

    def __init__(self, model_path: Optional[Union[str, Path]] = None):
        """
        Initialize the emotion detection model

        Args:
            model_path: Path to the trained model file (.pth)
                       If None, uses default bundled model
        """
        self.logger = logging.getLogger(__name__)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Set default model path
        if model_path is None:
            model_path = Path(__file__).parent / 'traini_dog_emotion_.pth'
        else:
            model_path = Path(model_path)

        self.model_path = model_path
        self.model = None
        self.classes = None  # Will be loaded from checkpoint
        self.model_config = None  # Will be loaded from checkpoint
        self.transform = self._create_transform()

        # Load model
        self._load_model()

    def _create_transform(self):
        """
        Create image preprocessing transform (matches training validation transform)

        Returns:
            torchvision.transforms composition
        """
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def _load_model(self):
        """Load the trained model from file (matches training save format)"""
        try:
            self.logger.info(f"Loading model from {self.model_path}")

            # Load model checkpoint
            checkpoint = torch.load(
                self.model_path,
                map_location=self.device,
                weights_only=False
            )

            # Extract classes and model config from checkpoint
            if isinstance(checkpoint, dict):
                # Get classes (list of emotion labels)
                if 'classes' in checkpoint:
                    self.classes = checkpoint['classes']
                    self.logger.info(f"Loaded {len(self.classes)} emotion classes from checkpoint")
                else:
                    # Fallback to default classes if not in checkpoint
                    self.logger.warning("Classes not found in checkpoint, using default emotions")
                    self.classes = ['happy', 'sad', 'angry', 'fearful', 'relaxed', 'playful', 'alert']

                # Get model config
                if 'model_config' in checkpoint:
                    self.model_config = checkpoint['model_config']
                    model_name = self.model_config.get('model_name', 'resnet34')
                    num_classes = self.model_config.get('num_classes', len(self.classes))
                else:
                    # Fallback defaults
                    model_name = 'resnet34'
                    num_classes = len(self.classes)
                    self.logger.warning(f"Model config not found, using defaults: {model_name}, {num_classes} classes")

                # Create model architecture
                model = DogEmotionModelArchitecture(
                    num_classes=num_classes,
                    model_name=model_name,
                    pretrained=False
                )

                # Load state dict
                if 'model_state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['model_state_dict'])
                elif 'state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['state_dict'])
                else:
                    # Checkpoint itself is the state dict
                    model.load_state_dict(checkpoint)
            else:
                # Old format: checkpoint is directly the state dict
                self.logger.warning("Old checkpoint format detected, using defaults")
                self.classes = ['happy', 'sad', 'angry', 'fearful', 'relaxed', 'playful', 'alert']
                model = DogEmotionModelArchitecture(
                    num_classes=len(self.classes),
                    model_name='resnet34',
                    pretrained=False
                )
                model.load_state_dict(checkpoint)

            model = model.to(self.device)
            model.eval()

            self.model = model
            self.logger.info(f"Model loaded successfully: {model.model_name} with {len(self.classes)} classes")
            self.logger.info(f"Emotion classes: {self.classes}")

        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            raise RuntimeError(f"Failed to load model: {str(e)}")

    def preprocess_image(self, image_bytes: bytes) -> torch.Tensor:
        """
        Preprocess image bytes for model input

        Args:
            image_bytes: Raw image bytes

        Returns:
            Preprocessed image tensor
        """
        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Apply transforms
            image_tensor = self.transform(image)

            # Add batch dimension
            image_tensor = image_tensor.unsqueeze(0)

            return image_tensor.to(self.device)

        except Exception as e:
            raise ValueError(f"Error preprocessing image: {str(e)}")

    def predict(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Predict emotion from image

        Args:
            image_bytes: Raw image bytes

        Returns:
            Dictionary containing:
                - emotion: Predicted emotion label
                - confidence: Confidence score (0-1)
                - all_predictions: Dict of all emotion probabilities
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")

        if self.classes is None:
            raise RuntimeError("Emotion classes not loaded")

        try:
            # Preprocess image
            image_tensor = self.preprocess_image(image_bytes)

            # Run inference
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)

            # Get predictions
            probs = probabilities.cpu().numpy()[0]
            predicted_idx = probs.argmax()

            # Build all predictions dict using loaded classes
            all_predictions = {
                self.classes[i]: float(probs[i])
                for i in range(len(self.classes))
            }

            # Sort by confidence
            all_predictions = dict(
                sorted(all_predictions.items(), key=lambda x: x[1], reverse=True)
            )

            return {
                'emotion': self.classes[predicted_idx],
                'confidence': float(probs[predicted_idx]),
                'all_predictions': all_predictions
            }

        except Exception as e:
            self.logger.error(f"Error during prediction: {str(e)}")
            raise RuntimeError(f"Prediction failed: {str(e)}")

    def __repr__(self):
        num_classes = len(self.classes) if self.classes else 0
        model_name = self.model_config.get('model_name', 'unknown') if self.model_config else 'unknown'
        return f"DogEmotionModel(model={model_name}, device={self.device}, num_classes={num_classes})"
