"""
Utility functions for AI Trainer Bot.
"""

import os
import random
import numpy as np
import torch
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import json
import yaml
import hashlib
import time
from datetime import datetime


def set_seed(seed: int = 42):
    """
    Set random seed for reproducibility.

    Args:
        seed: Random seed
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    # Make deterministic
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    # Set environment variable for Python hash seed
    os.environ['PYTHONHASHSEED'] = str(seed)


def get_device(device: Optional[str] = None) -> torch.device:
    """
    Get PyTorch device.

    Args:
        device: Device string ('cpu', 'cuda', 'cuda:0', etc.)

    Returns:
        PyTorch device
    """
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

    return torch.device(device)


def count_parameters(model: torch.nn.Module) -> int:
    """
    Count trainable parameters in a model.

    Args:
        model: PyTorch model

    Returns:
        Number of trainable parameters
    """
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def get_model_size_mb(model: torch.nn.Module) -> float:
    """
    Get model size in MB.

    Args:
        model: PyTorch model

    Returns:
        Model size in MB
    """
    param_size = 0
    for param in model.parameters():
        param_size += param.nelement() * param.element_size()

    buffer_size = 0
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()

    size_mb = (param_size + buffer_size) / 1024 / 1024
    return size_mb


def save_checkpoint(model: torch.nn.Module, optimizer: torch.optim.Optimizer,
                   scheduler: Optional[Any], epoch: int, loss: float,
                   filepath: Union[str, Path]):
    """
    Save model checkpoint.

    Args:
        model: PyTorch model
        optimizer: Optimizer
        scheduler: Learning rate scheduler
        epoch: Current epoch
        loss: Current loss
        filepath: Checkpoint file path
    """
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
    }

    if scheduler is not None:
        checkpoint['scheduler_state_dict'] = scheduler.state_dict()

    torch.save(checkpoint, filepath)


def load_checkpoint(filepath: Union[str, Path], model: torch.nn.Module,
                   optimizer: Optional[torch.optim.Optimizer] = None,
                   scheduler: Optional[Any] = None) -> Dict[str, Any]:
    """
    Load model checkpoint.

    Args:
        filepath: Checkpoint file path
        model: PyTorch model
        optimizer: Optimizer (optional)
        scheduler: Learning rate scheduler (optional)

    Returns:
        Checkpoint metadata
    """
    checkpoint = torch.load(filepath, map_location='cpu')

    model.load_state_dict(checkpoint['model_state_dict'])

    if optimizer is not None and 'optimizer_state_dict' in checkpoint:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

    if scheduler is not None and 'scheduler_state_dict' in checkpoint:
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])

    return checkpoint['epoch'], checkpoint['loss']


def compute_hash(data: Any) -> str:
    """
    Compute hash of data for caching.

    Args:
        data: Data to hash

    Returns:
        SHA256 hash string
    """
    if isinstance(data, (dict, list)):
        data_str = json.dumps(data, sort_keys=True)
    elif isinstance(data, np.ndarray):
        data_str = data.tobytes()
    elif isinstance(data, torch.Tensor):
        data_str = data.cpu().numpy().tobytes()
    else:
        data_str = str(data)

    return hashlib.sha256(data_str.encode()).hexdigest()


def create_experiment_id() -> str:
    """
    Create unique experiment ID.

    Returns:
        Experiment ID string
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_suffix = ''.join(random.choices('0123456789abcdef', k=8))
    return f"{timestamp}_{random_suffix}"


def format_time(seconds: float) -> str:
    """
    Format time in seconds to human-readable string.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def memory_usage_mb() -> float:
    """
    Get current memory usage in MB.

    Returns:
        Memory usage in MB
    """
    import psutil
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def gpu_memory_usage() -> Optional[Dict[str, float]]:
    """
    Get GPU memory usage.

    Returns:
        Dictionary with GPU memory info or None if no GPU
    """
    if not torch.cuda.is_available():
        return None

    info = {}
    for i in range(torch.cuda.device_count()):
        allocated = torch.cuda.memory_allocated(i) / 1024 / 1024
        reserved = torch.cuda.memory_reserved(i) / 1024 / 1024
        info[f'gpu_{i}'] = {
            'allocated_mb': allocated,
            'reserved_mb': reserved
        }

    return info


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """
    Safe division that returns default value if denominator is zero.

    Args:
        a: Numerator
        b: Denominator
        default: Default value

    Returns:
        Division result or default
    """
    return a / b if b != 0 else default


def flatten_dict(d: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
    """
    Flatten nested dictionary.

    Args:
        d: Nested dictionary
        prefix: Key prefix

    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Unflatten dictionary with dotted keys.

    Args:
        d: Flattened dictionary

    Returns:
        Nested dictionary
    """
    result = {}
    for key, value in d.items():
        keys = key.split('.')
        current = result
        for k in keys[:-1]:
            current = current.setdefault(k, {})
        current[keys[-1]] = value
    return result


def load_yaml(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Load YAML file.

    Args:
        filepath: YAML file path

    Returns:
        Dictionary from YAML
    """
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)


def save_yaml(data: Dict[str, Any], filepath: Union[str, Path]):
    """
    Save dictionary to YAML file.

    Args:
        data: Dictionary to save
        filepath: Output file path
    """
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)


def load_json(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Load JSON file.

    Args:
        filepath: JSON file path

    Returns:
        Dictionary from JSON
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], filepath: Union[str, Path]):
    """
    Save dictionary to JSON file.

    Args:
        data: Dictionary to save
        filepath: Output file path
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def ensure_dir(filepath: Union[str, Path]):
    """
    Ensure directory exists for file path.

    Args:
        filepath: File path
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)


def find_files(directory: Union[str, Path], pattern: str = "*") -> List[Path]:
    """
    Find files matching pattern in directory.

    Args:
        directory: Directory to search
        pattern: Glob pattern

    Returns:
        List of matching file paths
    """
    return list(Path(directory).glob(pattern))


def get_file_size_mb(filepath: Union[str, Path]) -> float:
    """
    Get file size in MB.

    Args:
        filepath: File path

    Returns:
        File size in MB
    """
    return Path(filepath).stat().st_size / 1024 / 1024


def timer(func):
    """
    Decorator to time function execution.

    Args:
        func: Function to time

    Returns:
        Wrapped function
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {format_time(end_time - start_time)}")
        return result
    return wrapper


class AverageMeter:
    """
    Computes and stores the average and current value.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val: float, n: int = 1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


class ProgressBar:
    """
    Simple progress bar for console output.
    """

    def __init__(self, total: int, prefix: str = 'Progress', suffix: str = '',
                 decimals: int = 1, length: int = 50, fill: str = '█'):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.iteration = 0

    def update(self, iteration: Optional[int] = None):
        if iteration is not None:
            self.iteration = iteration
        else:
            self.iteration += 1

        percent = (self.iteration / float(self.total)) * 100
        filled_length = int(self.length * self.iteration // self.total)
        bar = self.fill * filled_length + '-' * (self.length - filled_length)

        print(f'\r{self.prefix} |{bar}| {percent:.{self.decimals}f}% {self.suffix}', end='', flush=True)

        if self.iteration == self.total:
            print()


def validate_config(config: Dict[str, Any], required_keys: List[str]) -> List[str]:
    """
    Validate configuration has required keys.

    Args:
        config: Configuration dictionary
        required_keys: List of required keys

    Returns:
        List of missing keys
    """
    missing = []
    for key in required_keys:
        if key not in config:
            missing.append(key)
    return missing


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries.

    Args:
        base_config: Base configuration
        override_config: Override configuration

    Returns:
        Merged configuration
    """
    merged = base_config.copy()
    for key, value in override_config.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    return merged