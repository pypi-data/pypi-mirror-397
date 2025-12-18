"""
Base model class for AI Trainer Bot.
"""

import torch
import torch.nn as nn
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseModel(nn.Module, ABC):
    """
    Base class for all models in AI Trainer Bot.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize base model.

        Args:
            config: Model configuration
        """
        super().__init__()
        self.config = config

    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input tensor

        Returns:
            Output tensor
        """
        pass

    def get_num_parameters(self) -> int:
        """Get number of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def get_model_size_mb(self) -> float:
        """Get model size in MB."""
        param_size = 0
        for param in self.parameters():
            param_size += param.nelement() * param.element_size()
        buffer_size = 0
        for buffer in self.buffers():
            buffer_size += buffer.nelement() * buffer.element_size()

        size_mb = (param_size + buffer_size) / 1024 / 1024
        return size_mb

    def save(self, path: str):
        """Save model to file."""
        torch.save(self.state_dict(), path)

    def load(self, path: str):
        """Load model from file."""
        self.load_state_dict(torch.load(path))

    def freeze_layers(self, layer_names: List[str]):
        """Freeze specific layers."""
        for name, param in self.named_parameters():
            if any(layer_name in name for layer_name in layer_names):
                param.requires_grad = False

    def unfreeze_layers(self, layer_names: List[str]):
        """Unfreeze specific layers."""
        for name, param in self.named_parameters():
            if any(layer_name in name for layer_name in layer_names):
                param.requires_grad = True

    def get_layer_names(self) -> List[str]:
        """Get all layer names."""
        return [name for name, _ in self.named_parameters()]


class ClassificationModel(BaseModel):
    """
    Base class for classification models.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.num_classes = config.get('num_classes', 10)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass for classification."""
        # Implement in subclasses
        raise NotImplementedError("Subclasses must implement forward method")


class RegressionModel(BaseModel):
    """
    Base class for regression models.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.output_dim = config.get('output_dim', 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass for regression."""
        # Implement in subclasses
        raise NotImplementedError("Subclasses must implement forward method")