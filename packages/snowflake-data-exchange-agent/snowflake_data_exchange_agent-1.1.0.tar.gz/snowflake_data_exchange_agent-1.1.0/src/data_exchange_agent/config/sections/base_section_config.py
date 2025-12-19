from abc import ABC, ABCMeta, abstractmethod
from typing import Any

from data_exchange_agent.config.base_config import BaseConfig


class ValidatingMeta(ABCMeta):
    """Metaclass that automatically validates after __init__."""

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Call the metaclass."""
        # Create the instance
        instance = super().__call__(*args, **kwargs)
        # Run automatic validation first
        if hasattr(cls, "_required_fields"):
            error = instance._validate_required_fields()
            if error:
                raise ValueError(error)
        # Then run custom validation if method exists
        if hasattr(instance, "_custom_validation"):
            attributes_error = instance._custom_validation()
            if attributes_error:
                raise ValueError(attributes_error)
        return instance


class BaseSectionConfig(BaseConfig, ABC, metaclass=ValidatingMeta):
    """Base configuration class with common functionality."""

    # List of required fields for the configuration. Fields must be string or convertible to string.
    # It should be overridden by subclasses.
    # For example:
    # _required_fields = ["field1", "field2", "field3"]
    _required_fields: list[str] = []

    def _validate_required_fields(self) -> str | None:
        """Automatically validate all required fields."""
        for field_name in self._required_fields:
            if not hasattr(self, field_name):
                return f"{field_name} is required but not set."

            value = getattr(self, field_name)

            required_error = self._validate_required_field(value, field_name)
            if required_error:
                return required_error

        return None

    def __getitem__(self, key: str) -> Any:
        """Get an item from the configuration."""
        if not hasattr(self, key):
            raise KeyError(f"'{key}' not found in configuration.")
        if key.startswith("_"):
            raise KeyError(f"Private attributes cannot be accessed via indexing, got '{key}'.")
        return getattr(self, key)

    @abstractmethod
    def _custom_validation(self) -> str | None:
        """
        Validate the configuration using custom validation logic.

        Returns:
            str | None: Error message string or None on success.

        This method must be overridden in the subclasses to add additional validation logic.
        If no validation is required, return None.

        """
        pass

    def _validate_required_field(self, value: Any, field_name: str) -> str | None:
        """Validate a required field."""
        if value is None:
            return f"{field_name} value cannot be None."
        if isinstance(value, str):
            if not value:
                return f"{field_name} value cannot be empty."
            if not value.strip():
                return f"{field_name} value cannot contain only whitespace."
        return self._validate_scalar_field(value, field_name)

    def _validate_scalar_field(self, value: Any, field_name: str) -> str | None:
        """Validate a scalar field."""
        if not isinstance(value, str | bool | int | float | None):
            return f"{field_name} value must be string, boolean, integer, float, or None, got {type(value).__name__}."
        return None

    @staticmethod
    def _mask_sensitive_data(data: str) -> str:
        """Mask sensitive data for security in repr."""
        if len(data) <= 2:
            return "*" * len(data)
        unmasked_length = min(3, len(data) - 2)
        asterisks = "*" * (len(data) - unmasked_length)
        return f"{data[:unmasked_length]}{asterisks}"
