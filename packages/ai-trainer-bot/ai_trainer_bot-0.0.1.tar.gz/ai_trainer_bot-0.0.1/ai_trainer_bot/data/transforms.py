"""
Data transformation utilities for AI Trainer Bot.
"""

from typing import Dict, Any, List, Optional, Callable, Union
import torch
import numpy as np
from torchvision import transforms as T
from PIL import Image


class TransformPipeline:
    """
    Composable data transformation pipeline.
    """

    def __init__(self, transforms: List[Callable]):
        """
        Initialize transformation pipeline.

        Args:
            transforms: List of transformation functions
        """
        self.transforms = transforms

    def __call__(self, data: Any) -> Any:
        """
        Apply transformation pipeline.

        Args:
            data: Input data

        Returns:
            Transformed data
        """
        for transform in self.transforms:
            data = transform(data)
        return data

    def add_transform(self, transform: Callable):
        """Add a transformation to the pipeline."""
        self.transforms.append(transform)

    def remove_transform(self, index: int):
        """Remove a transformation from the pipeline."""
        if 0 <= index < len(self.transforms):
            self.transforms.pop(index)


class ImageTransforms:
    """
    Image-specific transformations.
    """

    @staticmethod
    def resize(size: Union[int, tuple]) -> Callable:
        """Resize transformation."""
        return T.Resize(size)

    @staticmethod
    def center_crop(size: Union[int, tuple]) -> Callable:
        """Center crop transformation."""
        return T.CenterCrop(size)

    @staticmethod
    def random_crop(size: Union[int, tuple]) -> Callable:
        """Random crop transformation."""
        return T.RandomCrop(size)

    @staticmethod
    def random_horizontal_flip(p: float = 0.5) -> Callable:
        """Random horizontal flip."""
        return T.RandomHorizontalFlip(p)

    @staticmethod
    def normalize(mean: List[float], std: List[float]) -> Callable:
        """Normalize transformation."""
        return T.Normalize(mean=mean, std=std)

    @staticmethod
    def to_tensor() -> Callable:
        """Convert to tensor."""
        return T.ToTensor()

    @staticmethod
    def compose(*transforms: Callable) -> TransformPipeline:
        """Compose multiple transformations."""
        return TransformPipeline(list(transforms))


class TextTransforms:
    """
    Text-specific transformations.
    """

    @staticmethod
    def tokenize(tokenizer: Callable) -> Callable:
        """Tokenization transformation."""
        def transform(text: str) -> List[str]:
            return tokenizer(text)
        return transform

    @staticmethod
    def pad_sequence(max_length: int, pad_token: str = "<pad>") -> Callable:
        """Pad sequence to max length."""
        def transform(tokens: List[str]) -> List[str]:
            if len(tokens) < max_length:
                tokens.extend([pad_token] * (max_length - len(tokens)))
            return tokens[:max_length]
        return transform

    @staticmethod
    def truncate(max_length: int) -> Callable:
        """Truncate sequence to max length."""
        def transform(tokens: List[str]) -> List[str]:
            return tokens[:max_length]
        return transform


class TensorTransforms:
    """
    Tensor-specific transformations.
    """

    @staticmethod
    def to_device(device: str) -> Callable:
        """Move tensor to device."""
        def transform(tensor: torch.Tensor) -> torch.Tensor:
            return tensor.to(device)
        return transform

    @staticmethod
    def unsqueeze(dim: int = 0) -> Callable:
        """Unsqueeze tensor."""
        def transform(tensor: torch.Tensor) -> torch.Tensor:
            return tensor.unsqueeze(dim)
        return transform

    @staticmethod
    @staticmethod
    def squeeze(dim: Optional[int] = None) -> Callable:
        """Squeeze tensor."""
        def transform(tensor: torch.Tensor) -> torch.Tensor:
            if dim is None:
                return tensor.squeeze()
            else:
                return tensor.squeeze(dim)
        return transform


def build_transform_pipeline(config: Dict[str, Any]) -> TransformPipeline:
    """
    Build transformation pipeline from configuration.

    Args:
        config: Transformation configuration

    Returns:
        TransformPipeline object
    """
    transforms = []

    # Add transforms based on config
    if config.get('resize'):
        transforms.append(ImageTransforms.resize(config['resize']))

    if config.get('normalize'):
        transforms.append(ImageTransforms.normalize(
            config['normalize']['mean'],
            config['normalize']['std']
        ))

    transforms.append(ImageTransforms.to_tensor())

    return TransformPipeline(transforms)