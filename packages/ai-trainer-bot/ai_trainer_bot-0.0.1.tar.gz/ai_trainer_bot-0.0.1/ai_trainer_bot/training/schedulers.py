"""
Learning rate schedulers for AI Trainer Bot.
"""

import torch.optim.lr_scheduler as lr_scheduler
from typing import Dict, Any, Optional


class SchedulerRegistry:
    """
    Registry for learning rate schedulers.
    """

    _registry = {}

    @classmethod
    def register(cls, name: str, scheduler_class: type):
        """Register a scheduler."""
        cls._registry[name] = scheduler_class

    @classmethod
    def get_scheduler(cls, name: str):
        """Get scheduler by name."""
        return cls._registry.get(name)

    @classmethod
    def list_schedulers(cls):
        """List available schedulers."""
        return list(cls._registry.keys())


def register_scheduler(name: str):
    """Decorator to register schedulers."""
    def decorator(scheduler_class):
        SchedulerRegistry.register(name, scheduler_class)
        return scheduler_class
    return decorator


@register_scheduler('step')
class StepScheduler:
    """Step learning rate scheduler."""

    @staticmethod
    def create(optimizer, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        return lr_scheduler.StepLR(
            optimizer,
            step_size=config.get('step_size', 30),
            gamma=config.get('gamma', 0.1)
        )


@register_scheduler('cosine')
class CosineScheduler:
    """Cosine annealing scheduler."""

    @staticmethod
    def create(optimizer, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        return lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=config.get('T_max', 100),
            eta_min=config.get('eta_min', 0)
        )


@register_scheduler('exponential')
class ExponentialScheduler:
    """Exponential learning rate scheduler."""

    @staticmethod
    def create(optimizer, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        return lr_scheduler.ExponentialLR(
            optimizer,
            gamma=config.get('gamma', 0.9)
        )


@register_scheduler('plateau')
class ReduceOnPlateauScheduler:
    """Reduce on plateau scheduler."""

    @staticmethod
    def create(optimizer, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        return lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode=config.get('mode', 'min'),
            factor=config.get('factor', 0.1),
            patience=config.get('patience', 10),
            min_lr=config.get('min_lr', 1e-6)
        )


@register_scheduler('cyclic')
class CyclicScheduler:
    """Cyclic learning rate scheduler."""

    @staticmethod
    def create(optimizer, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        return lr_scheduler.CyclicLR(
            optimizer,
            base_lr=config.get('base_lr', 0.001),
            max_lr=config.get('max_lr', 0.01),
            step_size_up=config.get('step_size_up', 2000),
            mode=config.get('mode', 'triangular')
        )


@register_scheduler('one_cycle')
class OneCycleScheduler:
    """One cycle learning rate scheduler."""

    @staticmethod
    def create(optimizer, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        return lr_scheduler.OneCycleLR(
            optimizer,
            max_lr=config.get('max_lr', 0.01),
            epochs=config.get('epochs', 100),
            steps_per_epoch=config.get('steps_per_epoch', 100),
            pct_start=config.get('pct_start', 0.3),
            anneal_strategy=config.get('anneal_strategy', 'cos')
        )


def get_scheduler(name: str, optimizer, config: Optional[Dict[str, Any]] = None):
    """
    Get scheduler by name.

    Args:
        name: Scheduler name
        optimizer: Optimizer instance
        config: Scheduler configuration

    Returns:
        Scheduler instance
    """
    scheduler_class = SchedulerRegistry.get_scheduler(name)
    if scheduler_class is None:
        raise ValueError(f"Scheduler '{name}' not found. "
                        f"Available schedulers: {SchedulerRegistry.list_schedulers()}")
    return scheduler_class.create(optimizer, config)