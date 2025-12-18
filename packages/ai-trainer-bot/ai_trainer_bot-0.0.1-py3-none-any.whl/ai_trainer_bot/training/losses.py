"""
Loss functions for AI Trainer Bot.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, Optional


class LossRegistry:
    """
    Registry for loss functions.
    """

    _registry = {}

    @classmethod
    def register(cls, name: str, loss_class: type):
        """Register a loss function."""
        cls._registry[name] = loss_class

    @classmethod
    def get_loss(cls, name: str):
        """Get loss function by name."""
        return cls._registry.get(name)

    @classmethod
    def list_losses(cls):
        """List available loss functions."""
        return list(cls._registry.keys())


def register_loss(name: str):
    """Decorator to register loss functions."""
    def decorator(loss_class):
        LossRegistry.register(name, loss_class)
        return loss_class
    return decorator


@register_loss('cross_entropy')
class CrossEntropyLoss(nn.CrossEntropyLoss):
    """Cross entropy loss."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        super().__init__(
            weight=config.get('weight'),
            reduction=config.get('reduction', 'mean')
        )


@register_loss('bce')
class BCELoss(nn.BCELoss):
    """Binary cross entropy loss."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        super().__init__(reduction=config.get('reduction', 'mean'))


@register_loss('bce_with_logits')
class BCEWithLogitsLoss(nn.BCEWithLogitsLoss):
    """Binary cross entropy with logits loss."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        super().__init__(
            pos_weight=config.get('pos_weight'),
            reduction=config.get('reduction', 'mean')
        )


@register_loss('mse')
class MSELoss(nn.MSELoss):
    """Mean squared error loss."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        super().__init__(reduction=config.get('reduction', 'mean'))


@register_loss('l1')
class L1Loss(nn.L1Loss):
    """L1 loss."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        super().__init__(reduction=config.get('reduction', 'mean'))


@register_loss('focal')
class FocalLoss(nn.Module):
    """
    Focal loss for addressing class imbalance.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        config = config or {}
        self.alpha = config.get('alpha', 1)
        self.gamma = config.get('gamma', 2)
        self.reduction = config.get('reduction', 'mean')

    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss

        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss


@register_loss('dice')
class DiceLoss(nn.Module):
    """
    Dice loss for segmentation tasks.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        config = config or {}
        self.smooth = config.get('smooth', 1.0)

    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        inputs = torch.sigmoid(inputs)

        inputs = inputs.view(-1)
        targets = targets.view(-1)

        intersection = (inputs * targets).sum()
        dice = (2. * intersection + self.smooth) / (inputs.sum() + targets.sum() + self.smooth)

        return 1 - dice


def get_loss_function(name: str, config: Optional[Dict[str, Any]] = None):
    """
    Get loss function by name.

    Args:
        name: Loss function name
        config: Loss configuration

    Returns:
        Loss function instance
    """
    loss_class = LossRegistry.get_loss(name)
    if loss_class is None:
        raise ValueError(f"Loss function '{name}' not found. "
                        f"Available losses: {LossRegistry.list_losses()}")
    return loss_class(config)