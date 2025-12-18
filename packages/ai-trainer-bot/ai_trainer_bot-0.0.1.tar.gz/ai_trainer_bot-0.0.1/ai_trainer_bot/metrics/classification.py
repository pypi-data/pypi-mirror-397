"""
Classification metrics for AI Trainer Bot.
"""

import torch
import torch.nn.functional as F
from typing import Dict, Any, List, Optional
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


class ClassificationMetrics:
    """
    Collection of classification metrics.
    """

    def __init__(self, num_classes: int = 2, average: str = 'macro'):
        """
        Initialize classification metrics.

        Args:
            num_classes: Number of classes
            average: Averaging method for multi-class metrics
        """
        self.num_classes = num_classes
        self.average = average

    def accuracy(self, predictions: torch.Tensor, targets: torch.Tensor) -> float:
        """
        Calculate accuracy.

        Args:
            predictions: Model predictions (logits or probabilities)
            targets: Ground truth labels

        Returns:
            Accuracy score
        """
        if predictions.dim() > 1 and predictions.shape[1] > 1:
            predictions = torch.argmax(predictions, dim=1)

        predictions = predictions.cpu().numpy()
        targets = targets.cpu().numpy()

        return accuracy_score(targets, predictions)

    def precision(self, predictions: torch.Tensor, targets: torch.Tensor) -> float:
        """
        Calculate precision.

        Args:
            predictions: Model predictions
            targets: Ground truth labels

        Returns:
            Precision score
        """
        if predictions.dim() > 1 and predictions.shape[1] > 1:
            predictions = torch.argmax(predictions, dim=1)

        predictions = predictions.cpu().numpy()
        targets = targets.cpu().numpy()

        return precision_score(targets, predictions, average=self.average, zero_division=0)

    def recall(self, predictions: torch.Tensor, targets: torch.Tensor) -> float:
        """
        Calculate recall.

        Args:
            predictions: Model predictions
            targets: Ground truth labels

        Returns:
            Recall score
        """
        if predictions.dim() > 1 and predictions.shape[1] > 1:
            predictions = torch.argmax(predictions, dim=1)

        predictions = predictions.cpu().numpy()
        targets = targets.cpu().numpy()

        return recall_score(targets, predictions, average=self.average, zero_division=0)

    def f1_score(self, predictions: torch.Tensor, targets: torch.Tensor) -> float:
        """
        Calculate F1 score.

        Args:
            predictions: Model predictions
            targets: Ground truth labels

        Returns:
            F1 score
        """
        if predictions.dim() > 1 and predictions.shape[1] > 1:
            predictions = torch.argmax(predictions, dim=1)

        predictions = predictions.cpu().numpy()
        targets = targets.cpu().numpy()

        return f1_score(targets, predictions, average=self.average, zero_division=0)

    def top_k_accuracy(self, predictions: torch.Tensor, targets: torch.Tensor,
                      k: int = 5) -> float:
        """
        Calculate top-k accuracy.

        Args:
            predictions: Model predictions (logits)
            targets: Ground truth labels
            k: Top-k value

        Returns:
            Top-k accuracy score
        """
        if predictions.dim() == 1:
            raise ValueError("Top-k accuracy requires multi-class predictions")

        _, pred_indices = torch.topk(predictions, k, dim=1)
        targets = targets.unsqueeze(1).expand_as(pred_indices)

        correct = (pred_indices == targets).any(dim=1)
        return correct.float().mean().item()

    def confusion_matrix(self, predictions: torch.Tensor, targets: torch.Tensor):
        """
        Calculate confusion matrix.

        Args:
            predictions: Model predictions
            targets: Ground truth labels

        Returns:
            Confusion matrix
        """
        from sklearn.metrics import confusion_matrix

        if predictions.dim() > 1 and predictions.shape[1] > 1:
            predictions = torch.argmax(predictions, dim=1)

        predictions = predictions.cpu().numpy()
        targets = targets.cpu().numpy()

        return confusion_matrix(targets, predictions)

    def compute_all(self, predictions: torch.Tensor, targets: torch.Tensor) -> Dict[str, float]:
        """
        Compute all classification metrics.

        Args:
            predictions: Model predictions
            targets: Ground truth labels

        Returns:
            Dictionary of all metrics
        """
        return {
            'accuracy': self.accuracy(predictions, targets),
            'precision': self.precision(predictions, targets),
            'recall': self.recall(predictions, targets),
            'f1_score': self.f1_score(predictions, targets),
        }