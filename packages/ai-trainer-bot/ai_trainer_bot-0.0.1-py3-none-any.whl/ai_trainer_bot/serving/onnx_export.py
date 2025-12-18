"""
ONNX export utilities for AI Trainer Bot.
"""

import torch
import numpy as np
from typing import Dict, Any, Optional, Union, Tuple
from pathlib import Path


class ONNXExporter:
    """
    Specialized ONNX exporter with validation and optimization.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ONNX exporter.

        Args:
            config: ONNX export configuration
        """
        self.config = config
        self.opset_version = config.get('opset_version', 11)
        self.verbose = config.get('verbose', False)
        self.optimize = config.get('optimize', True)

    def export(self, model: torch.nn.Module, export_path: Union[str, Path],
               input_sample: torch.Tensor, dynamic_axes: Optional[Dict[str, Dict[int, str]]] = None) -> str:
        """
        Export model to ONNX format.

        Args:
            model: PyTorch model
            export_path: Export path
            input_sample: Sample input tensor
            dynamic_axes: Dynamic axes specification

        Returns:
            Path to exported ONNX model
        """
        export_path = Path(export_path)
        if export_path.suffix != '.onnx':
            export_path = export_path.with_suffix('.onnx')

        # Ensure parent directory exists
        export_path.parent.mkdir(parents=True, exist_ok=True)

        # Set model to evaluation mode
        model.eval()

        # Export to ONNX
        torch.onnx.export(
            model,
            input_sample,
            export_path,
            opset_version=self.opset_version,
            verbose=self.verbose,
            input_names=self.config.get('input_names', ['input']),
            output_names=self.config.get('output_names', ['output']),
            dynamic_axes=dynamic_axes,
        )

        # Validate exported model
        self._validate_onnx_model(export_path, input_sample)

        # Optimize if requested
        if self.optimize:
            self._optimize_onnx_model(export_path)

        return str(export_path)

    def export_to_onnx(self, model: torch.nn.Module, input_sample: torch.Tensor, export_path: Union[str, Path],
                       dynamic_axes: Optional[Dict[str, Dict[int, str]]] = None, opset_version: Optional[int] = None) -> str:
        """
        Export model to ONNX format (alias for export).

        Args:
            model: PyTorch model
            input_sample: Sample input tensor
            export_path: Export path
            dynamic_axes: Dynamic axes specification
            opset_version: ONNX opset version

        Returns:
            Path to exported ONNX model
        """
        if opset_version:
            self.opset_version = opset_version
        return self.export(model, export_path, input_sample, dynamic_axes)

    def _validate_onnx_model(self, model_path: Path, input_sample: torch.Tensor):
        """
        Validate exported ONNX model.

        Args:
            model_path: Path to ONNX model
            input_sample: Sample input tensor
        """
        try:
            import onnxruntime as ort
        except ImportError:
            print("Warning: onnxruntime not installed. Skipping ONNX validation.")
            return

        # Load ONNX model
        ort_session = ort.InferenceSession(str(model_path))

        # Get PyTorch output
        pytorch_model = self._load_pytorch_model()
        if pytorch_model is None:
            return

        pytorch_model.eval()
        with torch.no_grad():
            pytorch_output = pytorch_model(input_sample)

        # Get ONNX output
        ort_inputs = {ort_session.get_inputs()[0].name: input_sample.numpy()}
        onnx_output = ort_session.run(None, ort_inputs)[0]

        # Compare outputs
        pytorch_output_np = pytorch_output.numpy()
        diff = np.abs(pytorch_output_np - onnx_output).max()

        if diff > 1e-5:
            print(f"Warning: Large difference between PyTorch and ONNX outputs: {diff}")
        else:
            print("ONNX model validation passed.")

    def validate_onnx_model(self, model_path: Union[str, Path]) -> bool:
        """Public helper to validate ONNX model existence and runtime loading.

        Returns True if the ONNX model can be loaded by onnxruntime, False otherwise.
        """
        try:
            import onnxruntime as ort
        except ImportError:
            return False

        try:
            ort.InferenceSession(str(model_path))
            return True
        except Exception:
            return False

    def _optimize_onnx_model(self, model_path: Path):
        """
        Optimize ONNX model.

        Args:
            model_path: Path to ONNX model
        """
        try:
            from onnxruntime.transformers.onnx_model import OnnxModel
            from onnxruntime.transformers.optimizer import optimize_model
        except ImportError:
            print("Warning: onnxruntime-tools not installed. Skipping ONNX optimization.")
            return

        # Load and optimize model
        model = OnnxModel.load(str(model_path))
        optimized_model = optimize_model(model)
        optimized_model.save_model_to_file(str(model_path))

        print("ONNX model optimized.")

    def _load_pytorch_model(self):
        """Load PyTorch model for validation."""
        # This would need to be implemented based on how models are saved
        return None

    def get_model_info(self, model_path: Path) -> Dict[str, Any]:
        """
        Get information about ONNX model.

        Args:
            model_path: Path to ONNX model

        Returns:
            Model information dictionary
        """
        try:
            import onnx
        except ImportError:
            raise ImportError("ONNX info requires 'pip install onnx'")

        model = onnx.load(str(model_path))

        info = {
            'opset_version': model.opset_import[0].version,
            'producer_name': model.producer_name,
            'producer_version': model.producer_version,
            'domain': model.domain,
            'model_version': model.model_version,
            'inputs': [],
            'outputs': [],
        }

        for input_tensor in model.graph.input:
            info['inputs'].append({
                'name': input_tensor.name,
                'shape': [dim.dim_value for dim in input_tensor.type.tensor_type.shape.dim],
            })

        for output_tensor in model.graph.output:
            info['outputs'].append({
                'name': output_tensor.name,
                'shape': [dim.dim_value for dim in output_tensor.type.tensor_type.shape.dim],
            })

        return info


def create_input_sample(batch_size: int = 1, channels: int = 3,
                       height: int = 224, width: int = 224) -> torch.Tensor:
    """
    Create sample input tensor for ONNX export.

    Args:
        batch_size: Batch size
        channels: Number of channels
        height: Image height
        width: Image width

    Returns:
        Sample input tensor
    """
    return torch.randn(batch_size, channels, height, width)


def export_to_onnx(model: torch.nn.Module, export_path: str,
                  input_sample: Optional[torch.Tensor] = None,
                  config: Optional[Dict[str, Any]] = None) -> str:
    """
    Convenience function to export model to ONNX.

    Args:
        model: PyTorch model
        export_path: Export path
        input_sample: Sample input tensor
        config: Export configuration

    Returns:
        Path to exported ONNX model
    """
    config = config or {}
    exporter = ONNXExporter(config)

    if input_sample is None:
        input_sample = create_input_sample()

    return exporter.export(model, export_path, input_sample)