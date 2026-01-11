"""
Shared configuration utilities.

Provides common configuration loading and validation functionality.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_env_file(env_path: Optional[Path] = None) -> None:
    """
    Load environment variables from .env file.

    Args:
        env_path: Path to .env file (defaults to .env in repo root)
    """
    if env_path is None:
        # Look for .env in repo root (one level up from shared/)
        env_path = Path(__file__).parent.parent / '.env'

    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment from {env_path}")
    else:
        logger.warning(f".env file not found at {env_path}")


def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to YAML config file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    logger.info(f"Loaded configuration from {config_path}")
    return config or {}


def get_required_env_var(var_name: str, error_msg: Optional[str] = None) -> str:
    """
    Get a required environment variable.

    Args:
        var_name: Name of environment variable
        error_msg: Optional custom error message

    Returns:
        Environment variable value

    Raises:
        ValueError: If environment variable is not set
    """
    value = os.getenv(var_name)
    if not value:
        msg = error_msg or f"Required environment variable {var_name} is not set"
        raise ValueError(msg)
    return value


def get_env_var(var_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get an optional environment variable with default.

    Args:
        var_name: Name of environment variable
        default: Default value if not set

    Returns:
        Environment variable value or default
    """
    return os.getenv(var_name, default)


def validate_required_env_vars(required_vars: List[str]) -> List[str]:
    """
    Validate that all required environment variables are set.

    Args:
        required_vars: List of required variable names

    Returns:
        List of missing variable names (empty if all present)
    """
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")

    return missing


def setup_logging(log_file: Optional[str] = None,
                 log_level: str = "INFO",
                 include_console: bool = True) -> None:
    """
    Setup logging configuration.

    Args:
        log_file: Optional log file path
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        include_console: Whether to log to console
    """
    handlers = []

    # Console handler
    if include_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        handlers.append(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        force=True  # Override any existing configuration
    )

    logger.info(f"Logging configured (level={log_level}, file={log_file})")


class Config:
    """
    Configuration container that merges environment variables and YAML config.
    """

    def __init__(self, yaml_path: Optional[Path] = None):
        """
        Initialize configuration.

        Args:
            yaml_path: Optional path to YAML config file
        """
        self.yaml_config = {}
        if yaml_path and yaml_path.exists():
            self.yaml_config = load_yaml_config(yaml_path)

    def get(self, key: str, default: Any = None, from_env: bool = True) -> Any:
        """
        Get a configuration value.

        Looks in environment variables first, then YAML config.

        Args:
            key: Configuration key
            default: Default value if not found
            from_env: Whether to check environment variables

        Returns:
            Configuration value or default
        """
        if from_env:
            env_value = os.getenv(key)
            if env_value is not None:
                return env_value

        # Navigate nested YAML config using dot notation
        value = self.yaml_config
        for part in key.split('.'):
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    def get_required(self, key: str, from_env: bool = True) -> Any:
        """
        Get a required configuration value.

        Args:
            key: Configuration key
            from_env: Whether to check environment variables

        Returns:
            Configuration value

        Raises:
            ValueError: If configuration value not found
        """
        value = self.get(key, from_env=from_env)
        if value is None:
            raise ValueError(f"Required configuration '{key}' not found")
        return value
