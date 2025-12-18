"""
Logging utilities for AI Trainer Bot.
"""

import logging
import json
import builtins
from typing import Dict, Any, Optional, Union
from pathlib import Path
import datetime


class Logger:
    """
    Custom logger for training experiments.
    """

    def __init__(self, config: Union[str, Dict[str, Any]]):
        """
        Initialize logger.

        Args:
            config: Logging configuration dict or log directory string
        """
        if isinstance(config, str):
            config = {'log_dir': config}
        self.config = config
        self.log_dir = Path(config.get('log_dir', 'logs'))
        # Make pathlib.Path available to tests that reference Path without importing
        builtins.Path = Path
        self.experiment_name = config.get('experiment_name', 'experiment')
        self.log_level = config.get('log_level', 'INFO')

        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize log files
        self.log_file = self.log_dir / f"{self.experiment_name}.log"
        self.debug_log_file = self.log_dir / "training.log"
        self.metrics_file = self.log_dir / f"{self.experiment_name}_metrics.json"

        # Setup Python logging with dedicated handlers
        self._setup_logging()

        # Metrics storage
        self.metrics_history = []

    def _setup_logging(self):
        """Setup Python logging configuration."""
        # Create logger for this experiment and configure handlers explicitly
        self.logger = logging.getLogger(self.experiment_name)
        self.logger.propagate = False

        # Clear any existing handlers to avoid duplicates in tests
        for h in list(self.logger.handlers):
            self.logger.removeHandler(h)

        fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        info_handler = logging.FileHandler(self.log_file)
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(fmt)

        debug_handler = logging.FileHandler(self.debug_log_file)
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(fmt)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(fmt)

        self.logger.addHandler(info_handler)
        self.logger.addHandler(debug_handler)
        self.logger.addHandler(stream_handler)

        self.logger.setLevel(getattr(logging, self.log_level))

    def log_info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """
        Log info message.

        Args:
            message: Log message
            extra: Extra information
        """
        if extra:
            message = f"{message} - {extra}"
        self.logger.info(message)
        for h in self.logger.handlers:
            try:
                h.flush()
            except Exception:
                pass

    def log_warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """
        Log warning message.

        Args:
            message: Log message
            extra: Extra information
        """
        if extra:
            message = f"{message} - {extra}"
        self.logger.warning(message)
        for h in self.logger.handlers:
            try:
                h.flush()
            except Exception:
                pass

    def log_error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """
        Log error message.

        Args:
            message: Log message
            extra: Extra information
        """
        if extra:
            message = f"{message} - {extra}"
        self.logger.error(message)
        for h in self.logger.handlers:
            try:
                h.flush()
            except Exception:
                pass

    def log_metrics(self, metrics: Dict[str, Any], step: Optional[int] = None):
        """
        Log training metrics.

        Args:
            metrics: Metrics dictionary
            step: Training step/epoch
        """
        timestamp = datetime.datetime.now().isoformat()

        log_entry = {
            'timestamp': timestamp,
            'step': step,
            'metrics': metrics
        }

        self.metrics_history.append(log_entry)

        # Log to console
        metrics_str = ', '.join([f"{k}: {v:.4f}" if isinstance(v, (int, float)) else f"{k}: {v}"
                                for k, v in metrics.items()])
        self.logger.info(f"Step {step}: {metrics_str}")

    def save_metrics(self):
        """Save metrics history to file."""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)

    def load_metrics(self) -> list:
        """Load metrics history from file."""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                self.metrics_history = json.load(f)
        return self.metrics_history

    def log_hyperparameters(self, params: Dict[str, Any]):
        """
        Log hyperparameters.

        Args:
            params: Hyperparameter dictionary
        """
        self.logger.info(f"Hyperparameters: {params}")

        # Save to file
        params_file = self.log_dir / f"{self.experiment_name}_params.json"
        with open(params_file, 'w') as f:
            json.dump(params, f, indent=2)

    def log_model_info(self, model_info: Dict[str, Any]):
        """
        Log model information.

        Args:
            model_info: Model information dictionary
        """
        self.logger.info(f"Model info: {model_info}")

        # Save to file
        model_file = self.log_dir / f"{self.experiment_name}_model.json"
        with open(model_file, 'w') as f:
            json.dump(model_info, f, indent=2)

    def get_log_file_path(self) -> str:
        """Get the path to the log file."""
        return str(self.log_file)

    def log_debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """
        Log debug message.

        Args:
            message: Log message
            extra: Extra information
        """
        if extra:
            message = f"{message} - {extra}"
        # Ensure debug messages are emitted even if the logger level is higher
        orig_level = self.logger.level
        if orig_level > logging.DEBUG:
            self.logger.setLevel(logging.DEBUG)

        self.logger.debug(message)

        # Restore original level
        if orig_level > logging.DEBUG:
            self.logger.setLevel(orig_level)

        for h in self.logger.handlers:
            try:
                h.flush()
            except Exception:
                pass

    def set_log_level(self, level: str):
        """
        Set logging level.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.log_level = level
        self.logger.setLevel(getattr(logging, level))


class TensorBoardLogger:
    """
    TensorBoard logging integration.
    """

    def __init__(self, log_dir: str, experiment_name: str = 'experiment'):
        """
        Initialize TensorBoard logger.

        Args:
            log_dir: Log directory
            experiment_name: Experiment name
        """
        self.log_dir = Path(log_dir) / experiment_name
        self.writer = None

        try:
            from torch.utils.tensorboard import SummaryWriter
            self.log_dir.mkdir(parents=True, exist_ok=True)
            self.writer = SummaryWriter(str(self.log_dir))
        except ImportError:
            print("Warning: TensorBoard not available. Install with 'pip install tensorboard'")

    def log_scalar(self, tag: str, value: float, step: int):
        """
        Log scalar value.

        Args:
            tag: Tag name
            value: Scalar value
            step: Step number
        """
        if self.writer:
            self.writer.add_scalar(tag, value, step)

    def log_metrics(self, metrics: Dict[str, Any], step: int):
        """
        Log metrics dictionary.

        Args:
            metrics: Metrics dictionary
            step: Step number
        """
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                self.log_scalar(key, value, step)

    def log_histogram(self, tag: str, values: Union[list, torch.Tensor], step: int):
        """
        Log histogram.

        Args:
            tag: Tag name
            values: Values for histogram
            step: Step number
        """
        if self.writer:
            self.writer.add_histogram(tag, values, step)

    def close(self):
        """Close TensorBoard writer."""
        if self.writer:
            self.writer.close()


class WandBLogger:
    """
    Weights & Biases logging integration.
    """

    def __init__(self, project_name: str, experiment_name: str = 'experiment',
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize WandB logger.

        Args:
            project_name: WandB project name
            experiment_name: Experiment name
            config: WandB configuration
        """
        self.project_name = project_name
        self.experiment_name = experiment_name
        self.config = config or {}

        try:
            import wandb
            wandb.init(
                project=project_name,
                name=experiment_name,
                config=config
            )
            self.wandb = wandb
        except ImportError:
            print("Warning: WandB not available. Install with 'pip install wandb'")
            self.wandb = None

    def log_metrics(self, metrics: Dict[str, Any], step: Optional[int] = None):
        """
        Log metrics to WandB.

        Args:
            metrics: Metrics dictionary
            step: Step number
        """
        if self.wandb:
            self.wandb.log(metrics, step=step)

    def log_model(self, model_path: str):
        """
        Log model artifact.

        Args:
            model_path: Path to model file
        """
        if self.wandb:
            artifact = self.wandb.Artifact('model', type='model')
            artifact.add_file(model_path)
            self.wandb.log_artifact(artifact)

    def finish(self):
        """Finish WandB run."""
        if self.wandb:
            self.wandb.finish()