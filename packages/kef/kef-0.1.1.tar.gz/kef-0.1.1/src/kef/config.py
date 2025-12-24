"""Configuration management for Kaggle projects using OmegaConf.

This module provides a ConfigManager class that handles configuration merging
from base (repository-level) and project-level configuration files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from omegaconf import DictConfig, OmegaConf


class ConfigManager:
    """Manages configuration loading and merging for Kaggle projects.

    Supports hierarchical configuration with:
    - Base configuration at repository root (kef.yaml)
    - Project-local configuration (key.yaml or local kef.yaml override)

    Configurations are automatically merged with project config overriding base config.
    """

    def __init__(self, config_dir: Path | None = None) -> None:
        """Initialize ConfigManager.

        Args:
            config_dir: Optional directory to start searching from for key.yaml/kef.yaml.
                       If None, searches from current working directory.
        """
        self.start_dir = Path(config_dir) if config_dir else Path.cwd()
        self.project_config_path: Path | None = None
        self.base_config_path: Path | None = None
        self.config: DictConfig = OmegaConf.create({})
        self._loaded = False
        self._discovered = False

    def discover(self, force: bool = False) -> None:
        """Discover configuration files without loading them."""
        if self._discovered and not force:
            return
        self.project_config_path = self.find_project_config(self.start_dir)
        self.base_config_path = self.find_base_config()
        self._discovered = True

    def find_git_root(self, start_path: Path | None = None) -> Path | None:
        """Find the git repository root directory.

        Args:
            start_path: Path to start searching from. If None, uses current directory.

        Returns:
            Path to git root, or None if not in a git repository.
        """
        search_path = start_path or Path.cwd()

        # Walk up the directory tree looking for .git
        for path in [search_path, *search_path.parents]:
            if (path / ".git").exists():
                return path

        return None

    def find_base_config(self) -> Path | None:
        """Find base configuration file at repository root.

        Returns:
            Path to kef.yaml at git root, or None if not found.
        """
        git_root = self.find_git_root()
        if git_root:
            base_config = git_root / "kef.yaml"
            if base_config.exists():
                return base_config
        return None

    def find_project_config(self, start_dir: Path | None = None) -> Path | None:
        """Find project-local configuration file.

        Searches upward from start_dir for key.yaml (project-specific)
        or kef.yaml (local override). Prefers key.yaml if both exist.

        Args:
            start_dir: Directory to start searching from.

        Returns:
            Path to key.yaml or kef.yaml, or None if not found.
        """
        search_path = start_dir or Path.cwd()
        if not search_path.is_dir():
            search_path = search_path.parent

        for path in [search_path, *search_path.parents]:
            # Prefer key.yaml (project-specific config) over kef.yaml (local override)
            key_yaml = path / "key.yaml"
            if key_yaml.exists():
                return key_yaml

            kef_yaml = path / "kef.yaml"
            if kef_yaml.exists():
                return kef_yaml

        return None

    def load_base_config(self) -> None:
        """Load base configuration from repository root.

        Sets self.base_config_path and merges configuration.
        """
        if not self.base_config_path:
            self.base_config_path = self.find_base_config()
        if self.base_config_path:
            base_cfg = OmegaConf.load(self.base_config_path)
            self.config = OmegaConf.merge(self.config, base_cfg)  # type: ignore[assignment]

    def load_project_config(self) -> None:
        """Load project-local configuration.

        Project config overrides base config.
        The project_config_path is auto-discovered in __init__.
        """
        if self.project_config_path:
            project_cfg = OmegaConf.load(self.project_config_path)
            self.config = OmegaConf.merge(self.config, project_cfg)  # type: ignore[assignment]

    def load(self) -> DictConfig:
        """Load and merge all configurations.

        Loads base configuration first, then project configuration.
        Project configuration takes precedence over base configuration.

        Returns:
            Merged configuration as OmegaConf DictConfig object.
        """
        if self._loaded:
            return self.config

        self.discover()

        # Load base if found
        if self.base_config_path:
            base_cfg = OmegaConf.load(self.base_config_path)
            self.config = OmegaConf.merge(self.config, base_cfg)  # type: ignore[assignment]

        # Load project if found and different from base
        if self.project_config_path and self.project_config_path != self.base_config_path:
            project_cfg = OmegaConf.load(self.project_config_path)
            self.config = OmegaConf.merge(self.config, project_cfg)  # type: ignore[assignment]

        self._loaded = True
        return self.config

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.

        Args:
            key: Configuration key (supports dot notation, e.g., "db.host").
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        try:
            return OmegaConf.select(self.config, key, default=default)
        except Exception:
            return default

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Configuration as dictionary.
        """
        result = OmegaConf.to_container(self.config, resolve=True)
        return cast(dict[str, Any], result) if isinstance(result, dict) else {}

    def to_yaml(self) -> str:
        """Convert configuration to YAML string.

        Returns:
            Configuration as YAML string.
        """
        return OmegaConf.to_yaml(self.config)

    def __repr__(self) -> str:
        """Return string representation of ConfigManager."""
        return f"ConfigManager(base={self.base_config_path}, project={self.project_config_path})"
