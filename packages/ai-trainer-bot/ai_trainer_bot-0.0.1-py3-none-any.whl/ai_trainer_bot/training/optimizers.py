"""
Optimizer configurations for AI Trainer Bot.
"""

import torch.optim as optim
from typing import Dict, Any, Optional, List


class OptimizerRegistry:
    """
    Registry for optimizers.
    """

    _registry = {}

    @classmethod
    def register(cls, name: str, optimizer_class: type):
        """Register an optimizer."""
        cls._registry[name] = optimizer_class

    @classmethod
    def get_optimizer(cls, name: str):
        """Get optimizer by name."""
        return cls._registry.get(name)

    @classmethod
    def list_optimizers(cls):
        """List available optimizers."""
        return list(cls._registry.keys())


def register_optimizer(name: str):
    """Decorator to register optimizers."""
    def decorator(optimizer_class):
        OptimizerRegistry.register(name, optimizer_class)
        return optimizer_class
    return decorator


@register_optimizer('adam')
class AdamOptimizer:
    """Adam optimizer."""

    @staticmethod
    def create(params, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        return optim.Adam(
            params,
            lr=config.get('lr', 0.001),
            betas=config.get('betas', (0.9, 0.999)),
            eps=config.get('eps', 1e-8),
            weight_decay=config.get('weight_decay', 0)
        )


@register_optimizer('adamw')
class AdamWOptimizer:
    """AdamW optimizer."""

    @staticmethod
    def create(params, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        return optim.AdamW(
            params,
            lr=config.get('lr', 0.001),
            betas=config.get('betas', (0.9, 0.999)),
            eps=config.get('eps', 1e-8),
            weight_decay=config.get('weight_decay', 0.01)
        )


@register_optimizer('sgd')
class SGDOptimizer:
    """SGD optimizer."""

    @staticmethod
    def create(params, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        return optim.SGD(
            params,
            lr=config.get('lr', 0.01),
            momentum=config.get('momentum', 0.9),
            weight_decay=config.get('weight_decay', 0),
            nesterov=config.get('nesterov', False)
        )


@register_optimizer('rmsprop')
class RMSpropOptimizer:
    """RMSprop optimizer."""

    @staticmethod
    def create(params, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        return optim.RMSprop(
            params,
            lr=config.get('lr', 0.01),
            alpha=config.get('alpha', 0.99),
            eps=config.get('eps', 1e-8),
            weight_decay=config.get('weight_decay', 0),
            momentum=config.get('momentum', 0)
        )


@register_optimizer('adagrad')
class AdagradOptimizer:
    """Adagrad optimizer."""

    @staticmethod
    def create(params, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        return optim.Adagrad(
            params,
            lr=config.get('lr', 0.01),
            lr_decay=config.get('lr_decay', 0),
            weight_decay=config.get('weight_decay', 0),
            eps=config.get('eps', 1e-10)
        )


def get_optimizer(name: str, params, config: Optional[Dict[str, Any]] = None):
    """
    Get optimizer by name.

    Args:
        name: Optimizer name
        params: Model parameters
        config: Optimizer configuration

    Returns:
        Optimizer instance
    """
    optimizer_class = OptimizerRegistry.get_optimizer(name)
    if optimizer_class is None:
        raise ValueError(f"Optimizer '{name}' not found. "
                        f"Available optimizers: {OptimizerRegistry.list_optimizers()}")
    return optimizer_class.create(params, config)