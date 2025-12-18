"""
Inference utilities for AI Trainer Bot.
"""

import torch
import numpy as np
from typing import Dict, Any, Optional, Union, List
from pathlib import Path


class InferenceEngine:
    """
    Inference engine for deployed models.
    """

    def __init__(self, model_path: Union[str, Path], model_format: str = 'pytorch',
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize inference engine.

        Args:
            model_path: Path to model file
            model_format: Model format ('pytorch', 'torchscript', 'onnx')
            config: Inference configuration
        """
        self.model_path = Path(model_path)
        self.model_format = model_format
        self.config = config or {}
        self.model = None
        self.device = torch.device(self.config.get('device', 'cpu'))

        self._load_model()

    def _load_model(self):
        """Load model based on format."""
        if self.model_format == 'pytorch':
            self._load_pytorch_model()
        elif self.model_format == 'torchscript':
            self._load_torchscript_model()
        elif self.model_format == 'onnx':
            self._load_onnx_model()
        else:
            raise ValueError(f"Unsupported model format: {self.model_format}")

    def _load_pytorch_model(self):
        """Load PyTorch model."""
        # This assumes the model class is available
        # In practice, you'd need to instantiate the model class first
        checkpoint = torch.load(self.model_path, map_location=self.device)
        # self.model = ModelClass()
        # self.model.load_state_dict(checkpoint)
        # self.model.to(self.device)
        # self.model.eval()
        raise NotImplementedError("PyTorch model loading requires model class")

    def _load_torchscript_model(self):
        """Load TorchScript model."""
        self.model = torch.jit.load(str(self.model_path), map_location=self.device)
        self.model.eval()

    def _load_onnx_model(self):
        """Load ONNX model."""
        try:
            import onnxruntime as ort
        except ImportError:
            raise ImportError("ONNX inference requires 'pip install onnxruntime'")

        self.model = ort.InferenceSession(str(self.model_path))

    def preprocess(self, inputs: Union[torch.Tensor, np.ndarray, List]) -> torch.Tensor:
        """
        Preprocess inputs.

        Args:
            inputs: Raw inputs

        Returns:
            Preprocessed tensor
        """
        if isinstance(inputs, np.ndarray):
            inputs = torch.from_numpy(inputs)
        elif isinstance(inputs, list):
            inputs = torch.tensor(inputs)
        elif not isinstance(inputs, torch.Tensor):
            raise ValueError(f"Unsupported input type: {type(inputs)}")

        # Move to device
        inputs = inputs.to(self.device)

        # Add batch dimension if needed
        if inputs.dim() == 3:  # (C, H, W) -> (1, C, H, W)
            inputs = inputs.unsqueeze(0)
        elif inputs.dim() == 1:  # (seq_len,) -> (1, seq_len)
            inputs = inputs.unsqueeze(0)

        return inputs

    def predict(self, inputs: Union[torch.Tensor, np.ndarray, List], batch_size: Optional[int] = None) -> Union[torch.Tensor, np.ndarray]:
        """
        Run inference.

        Args:
            inputs: Preprocessed inputs

        Returns:
            Model predictions
        """
        inputs = self.preprocess(inputs)

        if self.model_format in ['pytorch', 'torchscript']:
            with torch.no_grad():
                outputs = self.model(inputs)
        elif self.model_format == 'onnx':
            inputs_np = inputs.cpu().numpy()
            input_name = self.model.get_inputs()[0].name
            outputs = self.model.run(None, {input_name: inputs_np})[0]
            outputs = torch.from_numpy(outputs)

        return self.postprocess(outputs)

    def postprocess(self, outputs: torch.Tensor) -> Union[torch.Tensor, np.ndarray]:
        """
        Postprocess outputs.

        Args:
            outputs: Raw model outputs

        Returns:
            Postprocessed outputs
        """
        # Apply softmax for classification
        if self.config.get('task_type') == 'classification':
            outputs = torch.softmax(outputs, dim=1)

        # Convert to numpy if requested
        if self.config.get('return_numpy', True):
            outputs = outputs.cpu().numpy()

        return outputs

    def predict_batch(self, inputs: List[Union[torch.Tensor, np.ndarray, List]]) -> List:
        """
        Run batch inference.

        Args:
            inputs: List of inputs

        Returns:
            List of predictions
        """
        predictions = []
        for input_data in inputs:
            pred = self.predict(input_data)
            predictions.append(pred)
        return predictions

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.

        Returns:
            Model information dictionary
        """
        info = {
            'format': self.model_format,
            'path': str(self.model_path),
            'device': str(self.device),
        }

        if hasattr(self.model, 'parameters'):
            info['num_parameters'] = sum(p.numel() for p in self.model.parameters())

        return info


class BatchInferenceEngine(InferenceEngine):
    """
    Inference engine optimized for batch processing.
    """

    def __init__(self, model_path: Union[str, Path], model_format: str = 'pytorch',
                 config: Optional[Dict[str, Any]] = None, batch_size: int = 32):
        """
        Initialize batch inference engine.

        Args:
            model_path: Path to model file
            model_format: Model format
            config: Inference configuration
            batch_size: Batch size for processing
        """
        super().__init__(model_path, model_format, config)
        self.batch_size = batch_size

    def predict_batch(self, inputs: List[Union[torch.Tensor, np.ndarray, List]]) -> List:
        """
        Run optimized batch inference.

        Args:
            inputs: List of inputs

        Returns:
            List of predictions
        """
        # Group inputs into batches
        batches = [inputs[i:i + self.batch_size] for i in range(0, len(inputs), self.batch_size)]

        all_predictions = []
        for batch in batches:
            # Preprocess batch
            batch_tensors = [self.preprocess(inp) for inp in batch]
            batch_tensor = torch.stack(batch_tensors)

            # Run inference
            batch_outputs = self.predict(batch_tensor)

            # Split back into individual predictions
            for i in range(len(batch)):
                pred = batch_outputs[i]
                all_predictions.append(pred)

        return all_predictions


def create_inference_engine(model_path: str, model_format: str = 'auto',
                           config: Optional[Dict[str, Any]] = None) -> InferenceEngine:
    """
    Create inference engine with automatic format detection.

    Args:
        model_path: Path to model file
        model_format: Model format ('auto' for automatic detection)
        config: Inference configuration

    Returns:
        InferenceEngine instance
    """
    path = Path(model_path)

    if model_format == 'auto':
        if path.suffix == '.pt':
            model_format = 'torchscript'
        elif path.suffix == '.pth':
            model_format = 'pytorch'
        elif path.suffix == '.onnx':
            model_format = 'onnx'
        else:
            raise ValueError(f"Cannot auto-detect format for {path.suffix}")

    return InferenceEngine(model_path, model_format, config)