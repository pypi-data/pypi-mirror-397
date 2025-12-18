"""
Model export utilities for AI Trainer Bot.
"""

import torch
import os
from typing import Dict, Any, Optional, Union
from pathlib import Path


class ModelExporter:
    """
    Base class for model exporters.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize exporter.

        Args:
            config: Export configuration
        """
        self.config = config
        self.output_dir = Path(config.get('output_dir', 'exports'))

    def export(self, model: torch.nn.Module, export_path: Union[str, Path],
               **kwargs) -> str:
        """
        Export model.

        Args:
            model: PyTorch model to export
            export_path: Path to save exported model
            **kwargs: Additional export arguments

        Returns:
            Path to exported model
        """
        raise NotImplementedError

    def _ensure_output_dir(self):
        """Ensure output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)


class PyTorchExporter(ModelExporter):
    """
    Export PyTorch models.
    """

    def export(self, model: torch.nn.Module, export_path: Union[str, Path],
               **kwargs) -> str:
        """
        Export PyTorch model.

        Args:
            model: PyTorch model
            export_path: Export path
            **kwargs: Additional arguments

        Returns:
            Export path
        """
        export_path = Path(export_path)
        if export_path.suffix != '.pth':
            export_path = export_path.with_suffix('.pth')

        self._ensure_output_dir()

        # Set model to evaluation mode
        model.eval()

        # Save model state dict
        torch.save(model.state_dict(), export_path)

        return str(export_path)


class TorchScriptExporter(ModelExporter):
    """
    Export models to TorchScript.
    """

    def export(self, model: torch.nn.Module, export_path: Union[str, Path],
               example_input: Optional[torch.Tensor] = None, **kwargs) -> str:
        """
        Export model to TorchScript.

        Args:
            model: PyTorch model
            export_path: Export path
            example_input: Example input tensor for tracing
            **kwargs: Additional arguments

        Returns:
            Export path
        """
        export_path = Path(export_path)
        if export_path.suffix != '.pt':
            export_path = export_path.with_suffix('.pt')

        self._ensure_output_dir()

        # Set model to evaluation mode
        model.eval()

        # Export to TorchScript
        if example_input is not None:
            # Tracing mode
            with torch.no_grad():
                scripted_model = torch.jit.trace(model, example_input)
        else:
            # Scripting mode
            scripted_model = torch.jit.script(model)

        scripted_model.save(export_path)

        return str(export_path)


class ONNXExporter(ModelExporter):
    """
    Export models to ONNX format.
    """

    def export(self, model: torch.nn.Module, export_path: Union[str, Path],
               input_sample: torch.Tensor, opset_version: int = 11,
               **kwargs) -> str:
        """
        Export model to ONNX.

        Args:
            model: PyTorch model
            export_path: Export path
            input_sample: Sample input tensor
            opset_version: ONNX opset version
            **kwargs: Additional arguments

        Returns:
            Export path
        """
        try:
            import onnxruntime
        except ImportError:
            raise ImportError("ONNX export requires 'pip install onnxruntime'")

        export_path = Path(export_path)
        if export_path.suffix != '.onnx':
            export_path = export_path.with_suffix('.onnx')

        self._ensure_output_dir()

        # Set model to evaluation mode
        model.eval()

        # Export to ONNX
        torch.onnx.export(
            model,
            input_sample,
            export_path,
            opset_version=opset_version,
            verbose=False,
            **kwargs
        )

        return str(export_path)


class TensorFlowExporter(ModelExporter):
    """
    Export models to TensorFlow format.
    """

    def export(self, model: torch.nn.Module, export_path: Union[str, Path],
               **kwargs) -> str:
        """
        Export model to TensorFlow.

        Args:
            model: PyTorch model
            export_path: Export path
            **kwargs: Additional arguments

        Returns:
            Export path
        """
        raise NotImplementedError("TensorFlow export not implemented yet")


class ExporterRegistry:
    """
    Registry for model exporters.
    """

    _registry = {
        'pytorch': PyTorchExporter,
        'torchscript': TorchScriptExporter,
        'onnx': ONNXExporter,
        'tensorflow': TensorFlowExporter,
    }

    @classmethod
    def get_exporter(cls, format_name: str) -> type:
        """
        Get exporter class by format name.

        Args:
            format_name: Export format name

        Returns:
            Exporter class
        """
        if format_name not in cls._registry:
            raise ValueError(f"Unsupported export format: {format_name}. "
                           f"Available formats: {list(cls._registry.keys())}")
        return cls._registry[format_name]

    @classmethod
    def list_formats(cls) -> list:
        """List available export formats."""
        return list(cls._registry.keys())


def export_model(model: torch.nn.Module, format_name: str,
                export_path: Union[str, Path], config: Dict[str, Any],
                **kwargs) -> str:
    """
    Export model to specified format.

    Args:
        model: PyTorch model
        format_name: Export format
        export_path: Export path
        config: Export configuration
        **kwargs: Additional arguments

    Returns:
        Path to exported model
    """
    exporter_class = ExporterRegistry.get_exporter(format_name)
    exporter = exporter_class(config)
    return exporter.export(model, export_path, **kwargs)