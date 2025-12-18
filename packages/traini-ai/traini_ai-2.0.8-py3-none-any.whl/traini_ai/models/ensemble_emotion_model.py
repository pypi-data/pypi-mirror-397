"""
Ensemble Dog Emotion Detection Model
Uses 4 different models for improved accuracy
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import io
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import logging
import numpy as np
import os


# =====================================================================
# 注意力机制模块
# =====================================================================

class ChannelAttention(nn.Module):
    """通道注意力"""
    def __init__(self, channels, reduction=16):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(channels, channels // reduction, bias=False),
            nn.ReLU(),
            nn.Linear(channels // reduction, channels, bias=False)
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        b, c, _, _ = x.size()
        avg_out = self.fc(self.avg_pool(x).view(b, c))
        max_out = self.fc(self.max_pool(x).view(b, c))
        out = self.sigmoid(avg_out + max_out).view(b, c, 1, 1)
        return x * out


class SpatialAttention(nn.Module):
    """空间注意力"""
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(2, 1, kernel_size=7, padding=3)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        x_cat = torch.cat([avg_out, max_out], dim=1)
        out = self.sigmoid(self.conv(x_cat))
        return x * out


# =====================================================================
# 模型架构定义
# =====================================================================

class Model1_AttentionResNet50(nn.Module):
    """注意力ResNet50 - 最强单模型"""
    def __init__(self, num_classes=13):
        super().__init__()
        weights = models.ResNet50_Weights.IMAGENET1K_V2
        backbone = models.resnet50(weights=weights)

        self.conv1 = backbone.conv1
        self.bn1 = backbone.bn1
        self.relu = backbone.relu
        self.maxpool = backbone.maxpool
        self.layer1 = backbone.layer1
        self.layer2 = backbone.layer2
        self.layer3 = backbone.layer3
        self.layer4 = backbone.layer4

        self.attention3 = nn.Sequential(
            ChannelAttention(1024),
            SpatialAttention()
        )
        self.attention4 = nn.Sequential(
            ChannelAttention(2048),
            SpatialAttention()
        )

        self.avgpool = backbone.avgpool
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.BatchNorm1d(1024),
            nn.Dropout(0.3),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(0.2),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.attention3(x)
        x = self.layer4(x)
        x = self.attention4(x)

        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x


class Model2_ResNet50(nn.Module):
    """标准ResNet50"""
    def __init__(self, num_classes=13):
        super().__init__()
        weights = models.ResNet50_Weights.IMAGENET1K_V2
        self.backbone = models.resnet50(weights=weights)
        in_features = self.backbone.fc.in_features

        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(in_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


class Model3_ResNet101(nn.Module):
    """深度ResNet101"""
    def __init__(self, num_classes=13):
        super().__init__()
        weights = models.ResNet101_Weights.IMAGENET1K_V2
        self.backbone = models.resnet101(weights=weights)
        in_features = self.backbone.fc.in_features

        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(in_features, 1024),
            nn.ReLU(),
            nn.BatchNorm1d(1024),
            nn.Dropout(0.3),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


class Model4_EfficientNet(nn.Module):
    """高效EfficientNet"""
    def __init__(self, num_classes=13):
        super().__init__()
        try:
            weights = models.EfficientNet_B3_Weights.IMAGENET1K_V1
            self.backbone = models.efficientnet_b3(weights=weights)
            in_features = self.backbone.classifier[1].in_features

            self.backbone.classifier = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(in_features, 512),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(512, num_classes)
            )
        except:
            weights = models.ResNet152_Weights.IMAGENET1K_V2
            self.backbone = models.resnet152(weights=weights)
            in_features = self.backbone.fc.in_features

            self.backbone.fc = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(in_features, 512),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(512, num_classes)
            )

    def forward(self, x):
        return self.backbone(x)


# =====================================================================
# 集成模型类
# =====================================================================

class EnsembleDogEmotionModel:
    """
    Ensemble Dog Emotion Detection Model

    Uses 4 different models:
    1. AttentionResNet50 (Attention mechanism)
    2. ResNet50 (Standard version)
    3. ResNet101 (Deep version)
    4. EfficientNet-B3 (Efficient version)

    Improves accuracy and robustness
    """

    # Hugging Face repository for model files
    HF_REPO = "TrainiAI/dog-emotion-models"

    def __init__(self, model_dir: Optional[Union[str, Path]] = None,
                 model_weights: Optional[List[float]] = None,
                 voting_strategy: str = 'weighted'):
        """
        Initialize ensemble model

        Args:
            model_dir: Directory containing 4 model files
                      If None, models will be auto-downloaded to cache directory
            model_weights: Optional list of weights for each model
                          If None, uses default weights based on accuracy
                          Order: [AttentionResNet50, ResNet50, ResNet101, EfficientNet]
            voting_strategy: Voting strategy - 'weighted' (default), 'soft', or 'hard'
                           - 'weighted': Weighted average of probabilities
                           - 'soft': Simple average of probabilities
                           - 'hard': Majority voting (each model votes for top emotion)
        """
        self.logger = logging.getLogger(__name__)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Set model directory - use cache if not specified
        if model_dir is None:
            # Use user cache directory
            cache_dir = Path.home() / '.cache' / 'traini_ai' / 'models'
            cache_dir.mkdir(parents=True, exist_ok=True)
            model_dir = cache_dir
        else:
            model_dir = Path(model_dir)

        self.model_dir = model_dir
        self.models = []
        self.classes = None
        self.transform = self._create_transform()

        # Set voting strategy
        self.voting_strategy = voting_strategy

        # Default weights based on test accuracy
        # AttentionResNet50: 75.9%, ResNet50: 75.87%, ResNet101: 74.5%, EfficientNet: 73.2%
        self.default_weights = [0.759, 0.7587, 0.745, 0.732]

        # Normalize default weights to sum to 1
        total = sum(self.default_weights)
        self.default_weights = [w / total for w in self.default_weights]

        # Use provided weights or default
        self.model_weights = model_weights if model_weights else self.default_weights

        # Load all 4 models
        self._load_models()

    def _create_transform(self):
        """Create image preprocessing transform"""
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def _download_model_if_needed(self, filename: str) -> Path:
        """
        Download model file from Hugging Face if not exists locally

        Args:
            filename: Name of the model file

        Returns:
            Path to the model file
        """
        model_path = self.model_dir / filename

        # If file exists, return it
        if model_path.exists():
            return model_path

        # Try to download from Hugging Face
        try:
            from huggingface_hub import hf_hub_download

            self.logger.info(f"Downloading {filename} from Hugging Face Hub...")

            downloaded_path = hf_hub_download(
                repo_id=self.HF_REPO,
                filename=filename,
                cache_dir=self.model_dir.parent,
                local_dir=self.model_dir,
                local_dir_use_symlinks=False
            )

            self.logger.info(f"✓ Downloaded {filename}")
            return Path(downloaded_path)

        except ImportError:
            raise RuntimeError(
                "huggingface_hub is required to download models. "
                "Install it with: pip install huggingface_hub"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to download {filename}: {str(e)}")

    def _load_models(self):
        """Load all 4 ensemble models"""
        model_configs = [
            {
                'name': 'AttentionResNet50',
                'file': 'best_model_attention_resnet50.pth',
                'class': Model1_AttentionResNet50
            },
            {
                'name': 'ResNet50',
                'file': 'best_model_resnet50.pth',
                'class': Model2_ResNet50
            },
            {
                'name': 'ResNet101',
                'file': 'best_model_resnet101.pth',
                'class': Model3_ResNet101
            },
            {
                'name': 'EfficientNet',
                'file': 'best_model_efficientnet.pth',
                'class': Model4_EfficientNet
            }
        ]

        self.logger.info("Loading ensemble models...")

        for config in model_configs:
            try:
                # Download if needed
                model_path = self._download_model_if_needed(config['file'])
            except Exception as e:
                self.logger.warning(f"Could not get model {config['name']}: {str(e)}")
                continue

            try:
                # Load checkpoint
                checkpoint = torch.load(
                    model_path,
                    map_location=self.device,
                    weights_only=False
                )

                # Get classes (only need to do this once)
                if self.classes is None and 'classes' in checkpoint:
                    self.classes = checkpoint['classes']
                    self.logger.info(f"Loaded {len(self.classes)} emotion classes")

                num_classes = len(self.classes) if self.classes else 13

                # Create model
                model = config['class'](num_classes=num_classes)

                # Load state dict
                if 'model_state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['model_state_dict'])
                else:
                    model.load_state_dict(checkpoint)

                model = model.to(self.device)
                model.eval()

                self.models.append(model)
                self.logger.info(f"✓ Loaded {config['name']}")

            except Exception as e:
                self.logger.error(f"Failed to load {config['name']}: {str(e)}")

        if len(self.models) == 0:
            raise RuntimeError("No ensemble models could be loaded")

        self.logger.info(f"Successfully loaded {len(self.models)}/4 ensemble models")

    @property
    def ensemble_size(self) -> int:
        """Return number of models in ensemble"""
        return len(self.models)

    def preprocess_image(self, image_bytes: bytes) -> torch.Tensor:
        """Preprocess image bytes for model input"""
        try:
            image = Image.open(io.BytesIO(image_bytes))

            if image.mode != 'RGB':
                image = image.convert('RGB')

            image_tensor = self.transform(image)
            image_tensor = image_tensor.unsqueeze(0)

            return image_tensor.to(self.device)

        except Exception as e:
            raise ValueError(f"Error preprocessing image: {str(e)}")

    def predict(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Predict emotion using ensemble (soft voting)

        Args:
            image_bytes: Raw image bytes

        Returns:
            Dictionary containing:
                - emotion: Predicted emotion label
                - confidence: Confidence score (0-1)
                - all_predictions: Dict of all emotion probabilities
                - model_predictions: Individual model predictions (for debugging)
        """
        if not self.models:
            raise RuntimeError("No models loaded")

        if self.classes is None:
            raise RuntimeError("Emotion classes not loaded")

        try:
            # Preprocess image
            image_tensor = self.preprocess_image(image_bytes)

            # Collect predictions from all models
            all_probs = []
            model_preds = []

            with torch.no_grad():
                for model in self.models:
                    outputs = model(image_tensor)
                    probs = F.softmax(outputs, dim=1)
                    probs_np = probs.cpu().numpy()[0]

                    all_probs.append(probs_np)

                    # Store individual model prediction
                    pred_idx = probs_np.argmax()
                    model_preds.append({
                        'emotion': self.classes[pred_idx],
                        'confidence': float(probs_np[pred_idx])
                    })

            # Apply voting strategy
            if self.voting_strategy == 'hard':
                # Hard voting: Each model votes for its top prediction
                votes = {}
                for pred in model_preds:
                    emotion = pred['emotion']
                    votes[emotion] = votes.get(emotion, 0) + 1

                # Get emotion with most votes
                predicted_emotion = max(votes.items(), key=lambda x: x[1])[0]
                predicted_idx = self.classes.index(predicted_emotion)

                # For confidence, use average of models that voted for this emotion
                confidences = [p['confidence'] for p in model_preds if p['emotion'] == predicted_emotion]
                avg_probs = np.mean(all_probs, axis=0)  # Still compute for all_predictions

            elif self.voting_strategy == 'weighted':
                # Weighted voting: Use model weights
                # Ensure we have correct number of weights
                weights = self.model_weights[:len(all_probs)]
                if len(weights) < len(all_probs):
                    # Pad with equal weights if needed
                    remaining = len(all_probs) - len(weights)
                    weights.extend([1.0/len(all_probs)] * remaining)

                # Normalize weights
                weights = np.array(weights)
                weights = weights / weights.sum()

                # Weighted average
                avg_probs = np.average(all_probs, axis=0, weights=weights)
                predicted_idx = avg_probs.argmax()

            else:  # 'soft' or default
                # Soft voting: Simple average of probabilities
                avg_probs = np.mean(all_probs, axis=0)
                predicted_idx = avg_probs.argmax()

            # Build all predictions dict
            all_predictions = {
                self.classes[i]: float(avg_probs[i])
                for i in range(len(self.classes))
            }

            # Sort by confidence
            all_predictions = dict(
                sorted(all_predictions.items(), key=lambda x: x[1], reverse=True)
            )

            result = {
                'emotion': self.classes[predicted_idx],
                'confidence': float(avg_probs[predicted_idx]),
                'all_predictions': all_predictions,
                'model_predictions': model_preds,
                'ensemble_size': len(self.models),
                'voting_strategy': self.voting_strategy,
                'model_weights': self.model_weights[:len(self.models)] if self.voting_strategy == 'weighted' else None
            }

            return result

        except Exception as e:
            self.logger.error(f"Error during prediction: {str(e)}")
            raise RuntimeError(f"Prediction failed: {str(e)}")

    def __repr__(self):
        num_classes = len(self.classes) if self.classes else 0
        return f"EnsembleDogEmotionModel(models={len(self.models)}, device={self.device}, num_classes={num_classes})"
