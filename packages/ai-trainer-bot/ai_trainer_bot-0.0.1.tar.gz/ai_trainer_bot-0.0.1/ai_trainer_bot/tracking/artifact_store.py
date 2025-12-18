"""
Artifact storage utilities for AI Trainer Bot.
"""

import os
import shutil
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import json
import pickle


class ArtifactStore:
    """
    Local artifact storage for models, checkpoints, and other files.
    """

    def __init__(self, base_dir: Union[str, Path], experiment_name: str = 'experiment'):
        """
        Initialize artifact store.

        Args:
            base_dir: Base directory for artifacts
            experiment_name: Experiment name
        """
        self.base_dir = Path(base_dir)
        self.experiment_name = experiment_name
        self.experiment_dir = self.base_dir / experiment_name

        # Create directories
        self.models_dir = self.experiment_dir / 'models'
        self.checkpoints_dir = self.experiment_dir / 'checkpoints'
        self.logs_dir = self.experiment_dir / 'logs'
        self.metrics_dir = self.experiment_dir / 'metrics'

        self._create_directories()

        # Aliases for tests
        self.store_path = self.experiment_dir

    def store_artifact(self, name: str, data: Any):
        """Store an artifact."""
        # Store simple key/value artifacts at the base directory
        with open(self.base_dir / f"{name}.json", 'w') as f:
            json.dump(data, f)

    def delete_artifact(self, name: str):
        """Delete an artifact."""
        path = self.base_dir / f"{name}.json"
        if not path.exists():
            raise FileNotFoundError(f"Artifact {name} not found")
        path.unlink()

    def retrieve_artifact(self, name: str) -> Any:
        """Retrieve an artifact."""
        path = self.base_dir / f"{name}.json"
        if not path.exists():
            raise FileNotFoundError(f"Artifact {name} not found")
        with open(path, 'r') as f:
            return json.load(f)

    def list_artifacts(self) -> List[str]:
        """List stored artifacts."""
        return [f.stem for f in self.base_dir.iterdir() if f.is_file() and f.suffix == '.json']

    def save_artifact(self, artifact_path: Union[str, Path], name: str):
        """Save an artifact file into the experiment directory (simple copy)."""
        dest = self.experiment_dir / name
        shutil.copy2(artifact_path, dest)

    def _create_directories(self):
        """Create necessary directories."""
        for dir_path in [self.models_dir, self.checkpoints_dir,
                        self.logs_dir, self.metrics_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def save_model(self, model, filename: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Save model artifact.

        Args:
            model: Model object (PyTorch model, etc.)
            filename: Filename for the model
            metadata: Additional metadata
        """
        model_path = self.models_dir / filename

        # Save model (assuming PyTorch for now)
        import torch
        torch.save(model.state_dict(), model_path)

        # Save metadata
        if metadata:
            metadata_path = model_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

    def load_model(self, model_class, filename: str):
        """
        Load model artifact.

        Args:
            model_class: Model class to instantiate
            filename: Model filename

        Returns:
            Loaded model
        """
        model_path = self.models_dir / filename
        model = model_class()
        import torch
        model.load_state_dict(torch.load(model_path))
        return model

    def save_checkpoint(self, checkpoint: Dict[str, Any], filename: str,
                       epoch: Optional[int] = None):
        """
        Save training checkpoint.

        Args:
            checkpoint: Checkpoint dictionary
            filename: Checkpoint filename
            epoch: Epoch number
        """
        checkpoint_path = self.checkpoints_dir / filename

        # Add metadata
        checkpoint['epoch'] = epoch
        checkpoint['experiment'] = self.experiment_name

        torch.save(checkpoint, checkpoint_path)

    def load_checkpoint(self, filename: str) -> Dict[str, Any]:
        """
        Load training checkpoint.

        Args:
            filename: Checkpoint filename

        Returns:
            Checkpoint dictionary
        """
        checkpoint_path = self.checkpoints_dir / filename
        return torch.load(checkpoint_path)

    def list_checkpoints(self) -> List[str]:
        """List all checkpoint files."""
        return [f.name for f in self.checkpoints_dir.glob('*.pth')]

    def get_latest_checkpoint(self) -> Optional[str]:
        """Get the latest checkpoint filename."""
        checkpoints = self.list_checkpoints()
        if not checkpoints:
            return None

        # Sort by modification time
        checkpoints.sort(key=lambda x: (self.checkpoints_dir / x).stat().st_mtime,
                        reverse=True)
        return checkpoints[0]

    def save_metrics(self, metrics: Dict[str, Any], filename: str):
        """
        Save metrics data.

        Args:
            metrics: Metrics dictionary
            filename: Metrics filename
        """
        metrics_path = self.metrics_dir / filename
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)

    def load_metrics(self, filename: str) -> Dict[str, Any]:
        """
        Load metrics data.

        Args:
            filename: Metrics filename

        Returns:
            Metrics dictionary
        """
        metrics_path = self.metrics_dir / filename
        with open(metrics_path, 'r') as f:
            return json.load(f)

    def save_log(self, log_data: str, filename: str):
        """
        Save log data.

        Args:
            log_data: Log content
            filename: Log filename
        """
        log_path = self.logs_dir / filename
        with open(log_path, 'a') as f:
            f.write(log_data + '\n')

    def save_artifact_file(self, source_path: Union[str, Path], artifact_name: str,
                     artifact_type: str = 'misc'):
        """
        Save arbitrary artifact.

        Args:
            source_path: Source file path
            artifact_name: Artifact name
            artifact_type: Artifact type/category
        """
        artifact_dir = self.experiment_dir / artifact_type
        artifact_dir.mkdir(exist_ok=True)

        dest_path = artifact_dir / artifact_name
        shutil.copy2(source_path, dest_path)

    def list_artifacts_by_type(self, artifact_type: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List all artifacts.

        Args:
            artifact_type: Specific artifact type to list

        Returns:
            Dictionary of artifact types and filenames
        """
        artifacts = {}

        if artifact_type:
            types_to_check = [artifact_type]
        else:
            types_to_check = ['models', 'checkpoints', 'logs', 'metrics', 'misc']

        for art_type in types_to_check:
            type_dir = self.experiment_dir / art_type
            if type_dir.exists():
                artifacts[art_type] = [f.name for f in type_dir.glob('*')]

        return artifacts

    def get_artifact_path(self, artifact_name: str, artifact_type: str = 'misc') -> Path:
        """
        Get full path to artifact.

        Args:
            artifact_name: Artifact name
            artifact_type: Artifact type

        Returns:
            Full path to artifact
        """
        return self.experiment_dir / artifact_type / artifact_name

    def clean_old_checkpoints(self, keep_last: int = 5):
        """
        Clean old checkpoints, keeping only the most recent ones.

        Args:
            keep_last: Number of recent checkpoints to keep
        """
        checkpoints = self.list_checkpoints()
        if len(checkpoints) <= keep_last:
            return

        # Sort by modification time (oldest first)
        checkpoints.sort(key=lambda x: (self.checkpoints_dir / x).stat().st_mtime)

        # Remove old checkpoints
        for checkpoint in checkpoints[:-keep_last]:
            (self.checkpoints_dir / checkpoint).unlink()

    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get storage information.

        Returns:
            Storage info dictionary
        """
        total_size = 0
        file_count = 0

        for dir_path in [self.models_dir, self.checkpoints_dir,
                        self.logs_dir, self.metrics_dir]:
            if dir_path.exists():
                for file_path in dir_path.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                        file_count += 1

        return {
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'file_count': file_count,
            'experiment_dir': str(self.experiment_dir)
        }