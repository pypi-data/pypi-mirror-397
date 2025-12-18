"""
Custom metric implementations for AI Trainer Bot.
"""

import torch
import torch.nn.functional as F
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod


class Metric(ABC):
    """
    Base class for custom metrics.
    """

    @abstractmethod
    def __call__(self, predictions: torch.Tensor, targets: torch.Tensor) -> float:
        """
        Compute metric.

        Args:
            predictions: Model predictions
            targets: Ground truth values

        Returns:
            Metric value
        """
        pass

    @abstractmethod
    def name(self) -> str:
        """Return metric name."""
        pass


class CustomAccuracy(Metric):
    """
    Custom accuracy metric with threshold.
    """

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

    def __call__(self, predictions: torch.Tensor, targets: torch.Tensor) -> float:
        predictions = (predictions > self.threshold).float()
        correct = (predictions == targets).float()
        return correct.mean().item()

    def name(self) -> str:
        return f"custom_accuracy_{self.threshold}"


class IoU(Metric):
    """
    Intersection over Union (IoU) for segmentation.
    """

    def __init__(self, num_classes: int = 2, ignore_index: Optional[int] = None):
        self.num_classes = num_classes
        self.ignore_index = ignore_index

    def __call__(self, predictions: torch.Tensor, targets: torch.Tensor) -> float:
        if predictions.dtype == torch.float32 or predictions.dtype == torch.float64:
            if predictions.dim() > 1 and predictions.shape[1] > 1:
                predictions = torch.argmax(predictions, dim=1)

        iou_scores = []
        for class_idx in range(self.num_classes):
            if class_idx == self.ignore_index:
                continue

            pred_mask = (predictions == class_idx)
            target_mask = (targets == class_idx)

            intersection = (pred_mask & target_mask).sum().float()
            union = (pred_mask | target_mask).sum().float()

            if union == 0:
                iou_scores.append(1.0)  # Perfect score if no pixels of this class
            else:
                iou_scores.append((intersection / union).item())

        return sum(iou_scores) / len(iou_scores)

    def name(self) -> str:
        return "iou"


class DiceCoefficient(Metric):
    """
    Dice coefficient for segmentation.
    """

    def __init__(self, num_classes: int = 2, smooth: float = 1e-6):
        self.num_classes = num_classes
        self.smooth = smooth

    def __call__(self, predictions: torch.Tensor, targets: torch.Tensor) -> float:
        if predictions.dtype == torch.float32 or predictions.dtype == torch.float64:
            if predictions.dim() > 1 and predictions.shape[1] > 1:
                predictions = torch.argmax(predictions, dim=1)

        dice_scores = []
        for class_idx in range(self.num_classes):
            pred_mask = (predictions == class_idx).float()
            target_mask = (targets == class_idx).float()

            intersection = (pred_mask * target_mask).sum()
            pred_sum = pred_mask.sum()
            target_sum = target_mask.sum()

            if target_sum == 0:
                continue  # Skip classes not present in targets

            dice = (2 * intersection + self.smooth) / (pred_sum + target_sum + self.smooth)
            dice_scores.append(dice.item())

        return sum(dice_scores) / len(dice_scores) if dice_scores else 0.0

    def name(self) -> str:
        return "dice"


class BLEUScore(Metric):
    """
    BLEU score for text generation evaluation.
    """

    def __init__(self, n_gram: int = 4):
        self.n_gram = n_gram

    def __call__(self, predictions: List[str], targets: List[str]) -> float:
        # Simple BLEU implementation
        # In practice, you'd use a library like nltk or sacrebleu
        total_bleu = 0
        for pred, target in zip(predictions, targets):
            pred_tokens = pred.split()
            target_tokens = target.split()

            if len(pred_tokens) == 0 or len(target_tokens) == 0:
                continue

            # Calculate n-gram matches
            bleu_score = self._calculate_bleu(pred_tokens, target_tokens)
            total_bleu += bleu_score

        return total_bleu / len(predictions) if predictions else 0.0

    def _calculate_bleu(self, pred_tokens: List[str], target_tokens: List[str]) -> float:
        """Calculate BLEU score for a single prediction-target pair."""
        # Simplified BLEU calculation
        matches = 0
        total = len(pred_tokens)

        for i in range(len(pred_tokens)):
            if i < len(target_tokens) and pred_tokens[i] == target_tokens[i]:
                matches += 1

        if total == 0:
            return 0.0

        return matches / total

    def name(self) -> str:
        return f"bleu_{self.n_gram}"


class ROUGEScore(Metric):
    """
    ROUGE score for text summarization evaluation.
    """

    def __init__(self, rouge_type: str = 'rouge-1'):
        self.rouge_type = rouge_type

    def __call__(self, predictions: List[str], targets: List[str]) -> float:
        # Simplified ROUGE implementation
        total_rouge = 0
        for pred, target in zip(predictions, targets):
            rouge_score = self._calculate_rouge(pred, target)
            total_rouge += rouge_score

        return total_rouge / len(predictions) if predictions else 0.0

    def _calculate_rouge(self, prediction: str, target: str) -> float:
        """Calculate ROUGE score for a single prediction-target pair."""
        pred_tokens = set(prediction.split())
        target_tokens = set(target.split())

        if len(target_tokens) == 0:
            return 0.0

        intersection = pred_tokens & target_tokens
        return len(intersection) / len(target_tokens)

    def name(self) -> str:
        return self.rouge_type


class MetricRegistry:
    """
    Registry for custom metrics.
    """

    _registry: Dict[str, type] = {}

    @classmethod
    def register(cls, name: str, metric_class: type):
        """Register a metric."""
        cls._registry[name] = metric_class

    @classmethod
    def get_metric(cls, name: str) -> type:
        """Get metric by name."""
        return cls._registry.get(name)

    @classmethod
    def list_metrics(cls) -> List[str]:
        """List available metrics."""
        return list(cls._registry.keys())


def register_metric(name: str):
    """Decorator to register metrics."""
    def decorator(metric_class):
        MetricRegistry.register(name, metric_class)
        return metric_class
    return decorator


# Register default metrics
MetricRegistry.register('custom_accuracy', CustomAccuracy)
MetricRegistry.register('iou', IoU)
MetricRegistry.register('dice', DiceCoefficient)
MetricRegistry.register('bleu', BLEUScore)
MetricRegistry.register('rouge', ROUGEScore)