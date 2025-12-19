"""Configuration file manager."""

from pathlib import Path
from typing import Any

import yaml

from kb_trend.config.models import Settings


class ConfigManager:
    """Manages configuration file operations."""

    def __init__(self, config_path: Path):
        """Initialize config manager.

        Args:
            config_path: Path to settings.yaml file
        """
        self.config_path = config_path

    def load(self) -> Settings:
        """Load settings from YAML file.

        Returns:
            Loaded settings

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Run 'kb-trend init' to create one."
            )

        with open(self.config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if data is None:
            raise ValueError(f"Empty configuration file: {self.config_path}")

        # Convert nested dicts to proper types
        if 'db_path' in data and data['db_path'] is not None:
            data['db_path'] = Path(data['db_path'])

        return Settings(**data)

    def save(self, settings: Settings) -> None:
        """Save settings to YAML file.

        Args:
            settings: Settings to save
        """
        # Convert to dict and handle Path objects
        data = settings.model_dump(mode='python')
        if 'db_path' in data and isinstance(data['db_path'], Path):
            data['db_path'] = str(data['db_path'])

        # Ensure parent directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    def to_dict(self, settings: Settings) -> dict[str, Any]:
        """Convert settings to dictionary for hashing.

        Args:
            settings: Settings to convert

        Returns:
            Dictionary representation
        """
        data = settings.model_dump(mode='python')
        # Convert Path to string for consistent hashing
        if 'db_path' in data and isinstance(data['db_path'], Path):
            data['db_path'] = str(data['db_path'])
        return data
