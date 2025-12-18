"""
Experiment tracking utilities for AI Trainer Bot.
"""

import json
import uuid
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import datetime


class ExperimentTracker:
    """
    Track and manage machine learning experiments.
    """

    def __init__(self, base_dir: Union[str, Path] = 'experiments',
                 experiment_name: Optional[str] = None):
        """
        Initialize experiment tracker.

        Args:
            base_dir: Base directory for experiments
            experiment_name: Experiment name (auto-generated if None)
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

        if experiment_name is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            experiment_name = f"experiment_{timestamp}_{unique_id}"

        self.experiment_name = experiment_name
        self.experiment_dir = self.base_dir / experiment_name
        self.experiment_dir.mkdir(exist_ok=True)

        # Experiment metadata
        self.metadata = {
            'experiment_name': experiment_name,
            'created_at': datetime.datetime.now().isoformat(),
            'status': 'initialized',
            'config': {},
            'metrics': {},
            'artifacts': []
        }

        self.metadata_file = self.experiment_dir / 'metadata.json'
        self._save_metadata()

        # Aliases for tests
        self.log_dir = str(self.base_dir)
        self.metrics = self.metadata['metrics']
        self.current_experiment = experiment_name
        self.config = self.metadata['config']

    def start_experiment(self, experiment_name: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Start an experiment with configuration.

        Args:
            experiment_name: Optional experiment name override
            config: Experiment configuration
        """
        if experiment_name:
            self.experiment_name = experiment_name
            self.current_experiment = experiment_name
            self.experiment_dir = self.base_dir / experiment_name
            self.experiment_dir.mkdir(exist_ok=True)
            self.metadata['experiment_name'] = experiment_name
            self.metadata_file = self.experiment_dir / 'metadata.json'

        if config:
            self.metadata['config'] = config
            self.config = config

        self.metadata['status'] = 'running'
        self.metadata['started_at'] = datetime.datetime.now().isoformat()
        self._save_metadata()

    def end_experiment(self):
        """
        End the experiment.
        """
        self.metadata['status'] = 'completed'
        self.metadata['finished_at'] = datetime.datetime.now().isoformat()
        self.current_experiment = None
        self._save_metadata()

    def set_config(self, config: Dict[str, Any]):
        """
        Set experiment configuration.

        Args:
            config: Configuration dictionary
        """
        self.metadata['config'] = config
        self._save_metadata()

    def log_metric(self, key: str, value: Union[int, float], step: Optional[int] = None):
        """
        Log a metric value.

        Args:
            key: Metric name
            value: Metric value
            step: Step/epoch number
        """
        if 'metrics' not in self.metadata:
            self.metadata['metrics'] = {}

        if key not in self.metadata['metrics']:
            self.metadata['metrics'][key] = []

        self.metadata['metrics'][key].append((step, value))

        self._save_metadata()

    def log_metrics(self, metrics: Dict[str, Union[int, float]], step: Optional[int] = None):
        """
        Log multiple metrics.

        Args:
            metrics: Metrics dictionary
            step: Step/epoch number
        """
        for key, value in metrics.items():
            self.log_metric(key, value, step)

    def log_artifact(self, artifact_path: Union[str, Path], artifact_name: str,
                    artifact_type: str = 'model'):
        """
        Log an artifact.

        Args:
            artifact_path: Path to artifact file
            artifact_name: Artifact name
            artifact_type: Artifact type
        """
        artifact_path = Path(artifact_path)

        # Copy artifact to experiment directory
        artifacts_dir = self.experiment_dir / 'artifacts'
        artifacts_dir.mkdir(exist_ok=True)

        dest_path = artifacts_dir / artifact_name
        import shutil
        shutil.copy2(artifact_path, dest_path)

        # Log in metadata
        artifact_info = {
            'name': artifact_name,
            'type': artifact_type,
            'original_path': artifact_path.as_posix(),
            'stored_path': str(dest_path),
            'timestamp': datetime.datetime.now().isoformat()
        }

        if 'artifacts' not in self.metadata:
            self.metadata['artifacts'] = []

        self.metadata['artifacts'].append(artifact_info)
        self._save_metadata()

    def set_status(self, status: str):
        """
        Set experiment status.

        Args:
            status: Status string ('running', 'completed', 'failed', etc.)
        """
        self.metadata['status'] = status
        if status in ['completed', 'failed']:
            self.metadata['finished_at'] = datetime.datetime.now().isoformat()
        self._save_metadata()

    def add_tag(self, tag: str):
        """
        Add a tag to the experiment.

        Args:
            tag: Tag string
        """
        if 'tags' not in self.metadata:
            self.metadata['tags'] = []

        if tag not in self.metadata['tags']:
            self.metadata['tags'].append(tag)
            self._save_metadata()

    def add_note(self, note: str):
        """
        Add a note to the experiment.

        Args:
            note: Note text
        """
        if 'notes' not in self.metadata:
            self.metadata['notes'] = []

        note_entry = {
            'text': note,
            'timestamp': datetime.datetime.now().isoformat()
        }

        self.metadata['notes'].append(note_entry)
        self._save_metadata()

    def get_summary(self) -> Dict[str, Any]:
        """
        Get experiment summary.

        Returns:
            Summary dictionary
        """
        summary = self.metadata.copy()
        summary['name'] = self.experiment_name

        # Simplify artifacts to list of names
        if 'artifacts' in summary:
            summary['artifacts'] = [a['name'] for a in summary['artifacts']]

        # Add computed metrics
        if 'metrics' in summary:
            for metric_name, values in summary['metrics'].items():
                if values:
                    if isinstance(values[0], dict):
                        metric_values = [v['value'] for v in values]
                    else:
                        metric_values = [v[1] for v in values]  # tuple (step, value)
                    summary[f'{metric_name}_final'] = metric_values[-1]
                    summary[f'{metric_name}_best'] = max(metric_values) if metric_values else None
                    summary[f'{metric_name}_mean'] = sum(metric_values) / len(metric_values)

        return summary

    def _save_metadata(self):
        """Save metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def _load_metadata(self):
        """Load metadata from file."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)

    @classmethod
    def load_experiment(cls, experiment_dir: Union[str, Path]) -> 'ExperimentTracker':
        """
        Load existing experiment.

        Args:
            experiment_dir: Experiment directory

        Returns:
            ExperimentTracker instance
        """
        experiment_dir = Path(experiment_dir)
        tracker = cls.__new__(cls)
        tracker.base_dir = experiment_dir.parent
        tracker.experiment_name = experiment_dir.name
        tracker.experiment_dir = experiment_dir
        tracker.metadata_file = experiment_dir / 'metadata.json'
        tracker._load_metadata()
        return tracker

    @classmethod
    def list_experiments(cls, base_dir: Union[str, Path] = 'experiments') -> List[str]:
        """
        List all experiments.

        Args:
            base_dir: Base experiments directory

        Returns:
            List of experiment names
        """
        base_dir = Path(base_dir)
        if not base_dir.exists():
            return []

        return [d.name for d in base_dir.iterdir() if d.is_dir()]

    @classmethod
    def get_experiment_summary(cls, experiment_name: str,
                              base_dir: Union[str, Path] = 'experiments') -> Optional[Dict[str, Any]]:
        """
        Get summary of a specific experiment.

        Args:
            experiment_name: Experiment name
            base_dir: Base experiments directory

        Returns:
            Experiment summary or None if not found
        """
        try:
            tracker = cls.load_experiment(Path(base_dir) / experiment_name)
            return tracker.get_summary()
        except:
            return None

    def get_experiment_summary(self) -> Optional[Dict[str, Any]]:
        """
        Get summary of the current experiment.

        Returns:
            Experiment summary
        """
        return self.get_summary()


class ExperimentManager:
    """
    Manage multiple experiments.
    """

    def __init__(self, base_dir: Union[str, Path] = 'experiments'):
        """
        Initialize experiment manager.

        Args:
            base_dir: Base directory for experiments
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def create_experiment(self, name: Optional[str] = None,
                         config: Optional[Dict[str, Any]] = None) -> ExperimentTracker:
        """
        Create new experiment.

        Args:
            name: Experiment name
            config: Initial configuration

        Returns:
            ExperimentTracker instance
        """
        tracker = ExperimentTracker(self.base_dir, name)
        if config:
            tracker.set_config(config)
        tracker.set_status('running')
        return tracker

    def get_experiment(self, name: str) -> Optional[ExperimentTracker]:
        """
        Get existing experiment.

        Args:
            name: Experiment name

        Returns:
            ExperimentTracker instance or None
        """
        experiment_dir = self.base_dir / name
        if experiment_dir.exists():
            return ExperimentTracker.load_experiment(experiment_dir)
        return None

    def list_experiments(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all experiments with summaries.

        Args:
            status_filter: Filter by status

        Returns:
            List of experiment summaries
        """
        experiments = []
        for exp_name in ExperimentTracker.list_experiments(self.base_dir):
            summary = ExperimentTracker.get_experiment_summary(exp_name, self.base_dir)
            if summary:
                if status_filter is None or summary.get('status') == status_filter:
                    experiments.append(summary)
        return experiments

    def compare_experiments(self, experiment_names: List[str]) -> Dict[str, Any]:
        """
        Compare multiple experiments.

        Args:
            experiment_names: List of experiment names

        Returns:
            Comparison dictionary
        """
        comparison = {}
        for name in experiment_names:
            summary = ExperimentTracker.get_experiment_summary(name, self.base_dir)
            if summary:
                comparison[name] = summary

        return comparison