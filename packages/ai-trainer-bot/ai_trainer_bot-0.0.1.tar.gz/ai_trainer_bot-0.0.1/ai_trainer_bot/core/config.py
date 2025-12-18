"""
Configuration handling for AI Trainer Bot.
"""

import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """
    Configuration class for managing training parameters.
    """

    def __init__(self, config_dict: Dict[str, Any]):
        """
        Initialize config from dictionary.

        Args:
            config_dict: Configuration dictionary
        """
        self._config = config_dict

        # Extract main sections
        self.model = ConfigSection(config_dict.get('model', {}))
        self.data = ConfigSection(config_dict.get('data', {}))
        self.training = ConfigSection(config_dict.get('training', {}))
        self.output = ConfigSection(config_dict.get('output', {}))

    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'Config':
        """
        Load configuration from YAML file.

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            Config object
        """
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return cls(config_dict)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """
        Create config from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            Config object
        """
        return cls(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return self._config

    def save_yaml(self, yaml_path: str):
        """Save config to YAML file."""
        with open(yaml_path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)


class ConfigSection:
    """
    A section of configuration with attribute access.
    """

    def __init__(self, section_dict: Dict[str, Any]):
        self._dict = section_dict.copy()  # Make a copy to avoid modifying original
        for key, value in section_dict.items():
            setattr(self, key, value)

    def __setattr__(self, name: str, value: Any):
        """Set attribute and update internal dict."""
        if name == '_dict':
            super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)
            if hasattr(self, '_dict') and name in self._dict:
                self._dict[name] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get value with default."""
        return getattr(self, key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Convert section to dictionary."""
        return self._dict