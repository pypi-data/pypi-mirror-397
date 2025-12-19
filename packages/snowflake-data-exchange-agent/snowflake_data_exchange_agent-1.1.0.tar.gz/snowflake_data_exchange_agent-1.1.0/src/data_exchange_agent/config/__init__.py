"""Configuration management module."""

from data_exchange_agent.config.manager import ConfigManager


__all__ = ["ConfigManager"]

# Backward compatibility
Config = ConfigManager()
