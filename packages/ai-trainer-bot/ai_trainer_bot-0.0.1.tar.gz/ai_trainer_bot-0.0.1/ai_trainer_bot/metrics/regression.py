"""
Regression metrics for AI Trainer Bot.
"""

import torch
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


class RegressionMetrics:
    """
    Collection of regression metrics.
    """

    def __init__(self):
        """Initialize regression metrics."""
        pass

    def mse(self, predictions: torch.Tensor, targets: torch.Tensor) -> float:
        """
        Calculate mean squared error.

        Args:
            predictions: Model predictions
            targets: Ground truth values

        Returns:
            MSE score
        """
        predictions = predictions.cpu().numpy().flatten()
        targets = targets.cpu().numpy().flatten()

        return mean_squared_error(targets, predictions)

    def rmse(self, predictions: torch.Tensor, targets: torch.Tensor) -> float:
        """
        Calculate root mean squared error.

        Args:
            predictions: Model predictions
            targets: Ground truth values

        Returns:
            RMSE score
        """
        return np.sqrt(self.mse(predictions, targets))

    def mae(self, predictions: torch.Tensor, targets: torch.Tensor) -> float:
        """
        Calculate mean absolute error.

        Args:
            predictions: Model predictions
            targets: Ground truth values

        Returns:
            MAE score
        """
        predictions = predictions.cpu().numpy().flatten()
        targets = targets.cpu().numpy().flatten()

        return mean_absolute_error(targets, predictions)

    def r2_score(self, predictions: torch.Tensor, targets: torch.Tensor) -> float:
        """
        Calculate R² score.

        Args:
            predictions: Model predictions
            targets: Ground truth values

        Returns:
            R² score
        """
        predictions = predictions.cpu().numpy().flatten()
        targets = targets.cpu().numpy().flatten()

        return r2_score(targets, predictions)

    def mape(self, predictions: torch.Tensor, targets: torch.Tensor) -> float:
        """
        Calculate mean absolute percentage error.

        Args:
            predictions: Model predictions
            targets: Ground truth values

        Returns:
            MAPE score
        """
        predictions = predictions.cpu().numpy().flatten()
        targets = targets.cpu().numpy().flatten()

        # Avoid division by zero
        mask = targets != 0
        if not mask.any():
            return np.nan

        return np.mean(np.abs((targets[mask] - predictions[mask]) / targets[mask])) * 100

    def explained_variance(self, predictions: torch.Tensor, targets: torch.Tensor) -> float:
        """
        Calculate explained variance score.

        Args:
            predictions: Model predictions
            targets: Ground truth values

        Returns:
            Explained variance score
        """
        from sklearn.metrics import explained_variance_score

        predictions = predictions.cpu().numpy().flatten()
        targets = targets.cpu().numpy().flatten()

        return explained_variance_score(targets, predictions)

    def compute_all(self, predictions: torch.Tensor, targets: torch.Tensor) -> Dict[str, float]:
        """
        Compute all regression metrics.

        Args:
            predictions: Model predictions
            targets: Ground truth values

        Returns:
            Dictionary of all metrics
        """
        return {
            'mse': self.mse(predictions, targets),
            'rmse': self.rmse(predictions, targets),
            'mae': self.mae(predictions, targets),
            'r2_score': self.r2_score(predictions, targets),
            'mape': self.mape(predictions, targets),
            'explained_variance': self.explained_variance(predictions, targets),
        }