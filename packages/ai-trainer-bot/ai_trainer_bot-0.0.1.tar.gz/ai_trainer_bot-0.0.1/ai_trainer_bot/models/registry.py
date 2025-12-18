"""
Model registry for AI Trainer Bot.
"""

from typing import Dict, Type, Any, Optional
import torch.nn as nn


class ModelRegistry:
    """
    Registry for managing model classes.
    """

    _registry: Dict[str, Type[nn.Module]] = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        """
        Decorator to register a model class.

        Args:
            name: Model name

        Returns:
            Decorator function
        """
        def decorator(model_class: Type[nn.Module]) -> Type[nn.Module]:
            cls._registry[name] = model_class
            return model_class
        return decorator

    @classmethod
    def get_model(cls, name: str) -> Type[nn.Module]:
        """
        Get model class by name.

        Args:
            name: Model name

        Returns:
            Model class
        """
        if name not in cls._registry:
            raise ValueError(f"Model '{name}' not found in registry. "
                           f"Available models: {list(cls._registry.keys())}")
        return cls._registry[name]

    @classmethod
    def list_models(cls) -> List[str]:
        """List all registered model names."""
        return list(cls._registry.keys())

    @classmethod
    def create_model(cls, name: str, **kwargs) -> nn.Module:
        """
        Create model instance.

        Args:
            name: Model name
            **kwargs: Model initialization arguments

        Returns:
            Model instance
        """
        model_class = cls.get_model(name)
        return model_class(**kwargs)


# Convenience function for registering models
def register_model(name: str) -> Callable:
    """
    Register a model class.

    Args:
        name: Model name

    Returns:
        Decorator function
    """
    return ModelRegistry.register(name)