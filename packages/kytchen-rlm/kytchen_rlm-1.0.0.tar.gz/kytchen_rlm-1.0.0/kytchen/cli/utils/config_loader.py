"""Two-tier configuration system for Kytchen CLI.

Supports configuration at two levels:
1. Global config (~/.kytchen/config.yaml or ~/.kytchen/config.json)
2. Project config (./kytchenfile.yaml or ./kytchenfile.json)

Project config takes precedence over global config.
Environment variables take precedence over both.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Try to import PyYAML
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None

# =============================================================================
# Config file locations
# =============================================================================

GLOBAL_CONFIG_DIR = Path.home() / ".kytchen"
GLOBAL_CONFIG_FILES = [
    GLOBAL_CONFIG_DIR / "config.yaml",
    GLOBAL_CONFIG_DIR / "config.yml",
    GLOBAL_CONFIG_DIR / "config.json",
]

PROJECT_CONFIG_FILES = [
    Path.cwd() / "kytchenfile.yaml",
    Path.cwd() / "kytchenfile.yml",
    Path.cwd() / "kytchenfile.json",
    Path.cwd() / ".kytchen.yaml",
    Path.cwd() / ".kytchen.yml",
    Path.cwd() / ".kytchen.json",
]


# =============================================================================
# Config file operations
# =============================================================================

def _load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML config file."""
    if not YAML_AVAILABLE:
        raise RuntimeError(
            "YAML support requires PyYAML. Install with: pip install 'kytchen[yaml]'"
        )

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a YAML object, got: {type(data)}")

    return data


def _load_json(path: Path) -> dict[str, Any]:
    """Load JSON config file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a JSON object, got: {type(data)}")

    return data


def _save_yaml(path: Path, config: dict[str, Any]) -> None:
    """Save config to YAML file."""
    if not YAML_AVAILABLE:
        raise RuntimeError(
            "YAML support requires PyYAML. Install with: pip install 'kytchen[yaml]'"
        )

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def _save_json(path: Path, config: dict[str, Any]) -> None:
    """Save config to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def load_config_file(path: Path) -> dict[str, Any]:
    """
    Load a config file (YAML or JSON).

    Args:
        path: Path to config file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    suffix = path.suffix.lower()

    if suffix in {".yaml", ".yml"}:
        return _load_yaml(path)
    elif suffix == ".json":
        return _load_json(path)
    else:
        raise ValueError(f"Unsupported config file format: {suffix}")


def save_config_file(path: Path, config: dict[str, Any]) -> None:
    """
    Save a config file (YAML or JSON).

    Args:
        path: Path to config file
        config: Configuration dictionary to save
    """
    suffix = path.suffix.lower()

    if suffix in {".yaml", ".yml"}:
        _save_yaml(path, config)
    elif suffix == ".json":
        _save_json(path, config)
    else:
        raise ValueError(f"Unsupported config file format: {suffix}")


# =============================================================================
# Config discovery and merging
# =============================================================================

def find_global_config() -> Path | None:
    """
    Find the global config file.

    Returns:
        Path to global config file, or None if not found
    """
    for path in GLOBAL_CONFIG_FILES:
        if path.exists():
            return path
    return None


def find_project_config() -> Path | None:
    """
    Find the project config file.

    Returns:
        Path to project config file, or None if not found
    """
    for path in PROJECT_CONFIG_FILES:
        if path.exists():
            return path
    return None


def load_global_config() -> dict[str, Any]:
    """
    Load global config.

    Returns:
        Global configuration dictionary (empty if no config file)
    """
    path = find_global_config()
    if path is None:
        return {}

    try:
        return load_config_file(path)
    except Exception:
        return {}


def load_project_config() -> dict[str, Any]:
    """
    Load project config.

    Returns:
        Project configuration dictionary (empty if no config file)
    """
    path = find_project_config()
    if path is None:
        return {}

    try:
        return load_config_file(path)
    except Exception:
        return {}


def load_merged_config() -> dict[str, Any]:
    """
    Load and merge global and project configs.

    Project config takes precedence over global config.

    Returns:
        Merged configuration dictionary
    """
    global_config = load_global_config()
    project_config = load_project_config()

    # Deep merge (project overrides global)
    merged = {**global_config}

    for key, value in project_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            # Merge nested dicts
            merged[key] = {**merged[key], **value}
        else:
            # Override
            merged[key] = value

    return merged


# =============================================================================
# Config value access
# =============================================================================

def get_config_value(key: str, default: Any = None, use_env: bool = True) -> Any:
    """
    Get a config value with environment variable override.

    Precedence (highest to lowest):
    1. Environment variable (if use_env=True)
    2. Project config
    3. Global config
    4. Default value

    Args:
        key: Config key (supports dot notation, e.g., "provider.model")
        default: Default value if key not found
        use_env: Whether to check environment variables

    Returns:
        Config value or default
    """
    # Check environment variable first
    if use_env:
        env_key = f"KYTCHEN_{key.upper().replace('.', '_')}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value

    # Load merged config
    config = load_merged_config()

    # Handle dot notation
    keys = key.split(".")
    value = config

    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default

    return value


def set_config_value(
    key: str,
    value: Any,
    global_config: bool = False,
) -> None:
    """
    Set a config value.

    Args:
        key: Config key (supports dot notation, e.g., "provider.model")
        value: Value to set
        global_config: If True, set in global config; otherwise project config
    """
    # Determine config file
    if global_config:
        path = find_global_config()
        if path is None:
            # Create default global config file
            path = GLOBAL_CONFIG_FILES[0]  # Use YAML by default
        config = load_global_config()
    else:
        path = find_project_config()
        if path is None:
            # Create default project config file
            path = PROJECT_CONFIG_FILES[0]  # Use YAML by default
        config = load_project_config()

    # Handle dot notation
    keys = key.split(".")
    current = config

    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        elif not isinstance(current[k], dict):
            raise ValueError(f"Cannot set nested key '{key}': '{k}' is not a dict")
        current = current[k]

    # Set the value
    current[keys[-1]] = value

    # Save config
    save_config_file(path, config)


def delete_config_value(key: str, global_config: bool = False) -> bool:
    """
    Delete a config value.

    Args:
        key: Config key to delete (supports dot notation)
        global_config: If True, delete from global config; otherwise project config

    Returns:
        True if key was deleted, False if not found
    """
    # Determine config file
    if global_config:
        path = find_global_config()
        if path is None:
            return False
        config = load_global_config()
    else:
        path = find_project_config()
        if path is None:
            return False
        config = load_project_config()

    # Handle dot notation
    keys = key.split(".")
    current = config

    for k in keys[:-1]:
        if not isinstance(current, dict) or k not in current:
            return False
        current = current[k]

    # Delete the value
    if not isinstance(current, dict) or keys[-1] not in current:
        return False

    del current[keys[-1]]

    # Save config
    save_config_file(path, config)
    return True


# =============================================================================
# Config file creation
# =============================================================================

def create_default_config(path: Path, template: str = "minimal") -> None:
    """
    Create a default config file.

    Args:
        path: Path to create config file at
        template: Template to use ("minimal", "full", "local", "cloud")
    """
    if template == "minimal":
        config = {
            "provider": "anthropic",
            "root_model": "claude-sonnet-4-20250514",
            "max_cost_usd": 5.0,
        }
    elif template == "full":
        config = {
            "provider": "anthropic",
            "root_model": "claude-sonnet-4-20250514",
            "sub_model": "claude-sonnet-4-20250514",
            "max_tokens": None,
            "max_cost_usd": 5.0,
            "max_iterations": 50,
            "max_depth": 2,
            "max_wall_time_seconds": 300.0,
            "max_sub_queries": 100,
            "enable_code_execution": True,
            "sandbox_timeout_seconds": 30.0,
            "enable_caching": True,
            "log_trajectory": True,
            "log_level": "INFO",
        }
    elif template == "local":
        config = {
            "provider": "anthropic",
            "root_model": "claude-sonnet-4-20250514",
            "max_cost_usd": 1.0,
            "log_trajectory": True,
        }
    elif template == "cloud":
        config = {
            "provider": "anthropic",
            "root_model": "claude-sonnet-4-20250514",
            "max_cost_usd": 10.0,
            "enable_caching": True,
        }
    else:
        raise ValueError(f"Unknown template: {template}")

    save_config_file(path, config)
