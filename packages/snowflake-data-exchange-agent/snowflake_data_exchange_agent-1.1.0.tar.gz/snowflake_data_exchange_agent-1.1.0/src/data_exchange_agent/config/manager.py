import argparse

from typing import Any

from data_exchange_agent import custom_exceptions
from data_exchange_agent.config.cli import CLIConfig
from data_exchange_agent.config.default import DefaultConfig
from data_exchange_agent.config.toml import TomlConfig
from data_exchange_agent.constants.paths import CONFIGURATION_FILE_PATH


class ConfigManager:
    """Configuration manager that handles CLI, TOML and default configurations with precedence rules."""

    def __init__(self):
        """Initialize configuration manager."""
        self.cli_config: CLIConfig = CLIConfig()
        self.toml_config: TomlConfig = TomlConfig()
        self.default_config: DefaultConfig = DefaultConfig()

    def load_cli_config(self, args: argparse.Namespace | dict[str, Any]) -> None:
        """
        Load CLI configuration from command line arguments.

        Args:
            args: Command line arguments (argparse.Namespace or dict[str, Any])

        """
        self.cli_config.load_config(args)

    def load_toml_config(self, config_path: str = CONFIGURATION_FILE_PATH) -> None:
        """
        Load TOML configuration from file.

        Args:
            config_path: Path to the TOML configuration file

        """
        self.toml_config.load_config(config_path)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with a default fallback.

        Args:
            key: Configuration key in dot notation
            default: Default value if key is not found

        Returns:
            Configuration value or default

        """
        try:
            return self[key]
        except KeyError:
            return default
        except Exception as e:
            raise custom_exceptions.ConfigurationError(f"Error getting configuration value for key '{key}'.") from e

    def __getitem__(self, key: str) -> Any:
        """
        Get configuration value using dot notation with CLI precedence over TOML.

        Args:
            key: Configuration key in dot notation (e.g., "application.workers")

        Returns:
            Configuration value from CLI if set, otherwise from TOML

        Raises:
            KeyError: If the configuration key is not found

        """
        parts = key.split(".")

        # Validate that no private attributes are accessed via indexing
        for part in parts:
            if part.startswith("_"):
                raise KeyError(
                    f"Private attributes cannot be accessed via indexing, got '{part}' as part of key '{key}'."
                )

        # Try CLI config first
        cli_value = self._get_value(parts, self.cli_config)
        if cli_value is not None:
            return cli_value

        # Then try TOML config
        toml_value = self._get_value(parts, self.toml_config)
        if toml_value is not None:
            return toml_value

        # Finally try default config
        default_value = self._get_value(parts, self.default_config)
        if default_value is not None:
            return default_value

        raise KeyError(f"Configuration key '{key}' not found.")

    def _get_value(self, parts: list[str], root_value: Any) -> Any:
        """
        Navigate through nested configuration using dot notation.

        Args:
            parts: List of keys to navigate (e.g., ['application', 'workers'])
            root_value: Root configuration object to start from

        Returns:
            The value at the specified path, or None if not found

        """
        value = root_value
        try:
            for part in parts:
                if isinstance(value, dict):
                    value = value[part]
                else:
                    value = getattr(value, part)
            return value
        except (AttributeError, KeyError, TypeError):
            return None

    def __contains__(self, key: str) -> bool:
        """Check if a configuration key exists."""
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __repr__(self) -> str:
        """Return string representation of configuration manager."""
        return f"ConfigManager(cli_config={self.cli_config}, toml_config={self.toml_config})"
